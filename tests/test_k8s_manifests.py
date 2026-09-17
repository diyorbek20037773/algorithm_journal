"""Static guarantees for the Kubernetes / Argo CD manifests.

CI additionally renders every overlay with kustomize and validates it with
kubeconform; these tests pin the project-specific rules a schema cannot see.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
K8S = ROOT / "k8s"

APP_WORKLOAD_FILES = ["web.yaml", "worker.yaml", "beat.yaml", "migrate-job.yaml"]


def _docs(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [doc for doc in yaml.safe_load_all(handle) if doc]


def _pod_spec(doc: dict) -> dict:
    spec = doc["spec"]
    if doc["kind"] == "CronJob":
        return spec["jobTemplate"]["spec"]["template"]["spec"]
    return spec["template"]["spec"]


def test_every_kustomization_references_existing_files() -> None:
    """A typo in a resources/components list must fail here, not in Argo CD."""
    kustomizations = list(K8S.rglob("kustomization.yaml"))
    assert len(kustomizations) >= 5
    for kfile in kustomizations:
        data = _docs(kfile)[0]
        for entry in [*data.get("resources", []), *data.get("components", [])]:
            assert (kfile.parent / entry).exists(), f"{kfile}: missing {entry}"


@pytest.mark.parametrize("filename", APP_WORKLOAD_FILES)
def test_app_workloads_are_hardened(filename: str) -> None:
    """Non-root, no privilege escalation, dropped capabilities, resource limits."""
    workloads = [d for d in _docs(K8S / "base" / filename) if d["kind"] in {"Deployment", "Job"}]
    assert workloads
    for doc in workloads:
        pod = _pod_spec(doc)
        assert pod["securityContext"]["runAsNonRoot"] is True
        assert pod["automountServiceAccountToken"] is False
        for container in pod["containers"]:
            sc = container["securityContext"]
            assert sc["allowPrivilegeEscalation"] is False
            assert sc["capabilities"]["drop"] == ["ALL"]
            assert container["resources"]["limits"]["memory"]
            assert container["resources"]["requests"]["cpu"]


@pytest.mark.parametrize("filename", APP_WORKLOAD_FILES)
def test_app_containers_read_config_and_secrets(filename: str) -> None:
    """Every app process gets the same ConfigMap and Secret — no drift between roles."""
    for doc in _docs(K8S / "base" / filename):
        if doc["kind"] not in {"Deployment", "Job"}:
            continue
        app = _pod_spec(doc)["containers"][0]
        assert app["image"] == "arer-web"
        refs = {next(iter(ref.values()))["name"] for ref in app["envFrom"]}
        assert refs == {"arer-config", "arer-secrets"}


def test_web_probes_use_split_liveness_and_readiness() -> None:
    """Liveness must not depend on the database; readiness must."""
    web = next(d for d in _docs(K8S / "base" / "web.yaml") if d["kind"] == "Deployment")
    container = _pod_spec(web)["containers"][0]
    assert container["livenessProbe"]["httpGet"]["path"] == "/livez/"
    assert container["startupProbe"]["httpGet"]["path"] == "/livez/"
    assert container["readinessProbe"]["httpGet"]["path"] == "/healthz/"
    for probe in ("livenessProbe", "readinessProbe", "startupProbe"):
        headers = {h["name"]: h["value"] for h in container[probe]["httpGet"]["httpHeaders"]}
        assert headers["Host"] == "localhost"


def test_probe_host_is_allowed_in_every_environment() -> None:
    """The probes' Host header must be in ALLOWED_HOSTS, or Django answers 400."""
    base = _docs(K8S / "base" / "configmap.yaml")[0]["data"]
    assert "localhost" in base["DJANGO_ALLOWED_HOSTS"].split(",")
    for overlay in ("staging", "production"):
        text = (K8S / "overlays" / overlay / "kustomization.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        for patch in data["patches"]:
            for op in yaml.safe_load(patch["patch"]):
                if op["path"] == "/data/DJANGO_ALLOWED_HOSTS":
                    assert "localhost" in op["value"].split(","), overlay


def test_kubernetes_runs_migrations_in_a_hook_not_in_replicas() -> None:
    """Replicas must not race on migrations; the Sync-hook Job owns them."""
    config = _docs(K8S / "base" / "configmap.yaml")[0]["data"]
    assert config["MIGRATE_ON_START"] == "false"
    job = _docs(K8S / "base" / "migrate-job.yaml")[0]
    assert job["metadata"]["annotations"]["argocd.argoproj.io/hook"] == "Sync"
    assert job["spec"]["template"]["spec"]["containers"][0]["args"] == ["migrate"]
    entrypoint = (ROOT / "scripts" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "  migrate)" in entrypoint
    assert 'MIGRATE_ON_START:-true}" = "true"' in entrypoint


def test_single_beat_scheduler() -> None:
    """Two beats would send every periodic task twice."""
    beat = _docs(K8S / "base" / "beat.yaml")[0]
    assert beat["spec"]["replicas"] == 1
    assert beat["spec"]["strategy"]["type"] == "Recreate"
    hpas = {d["spec"]["scaleTargetRef"]["name"] for d in _docs(K8S / "base" / "hpa.yaml")}
    assert "arer-beat" not in hpas


def test_observability_is_wired_into_the_app_config() -> None:
    """JSON logs for Fluent Bit and an OTLP endpoint that exists in the monitoring stack."""
    config = _docs(K8S / "base" / "configmap.yaml")[0]["data"]
    assert config["LOG_FORMAT"] == "json"
    endpoint = config["OTEL_EXPORTER_OTLP_ENDPOINT"]
    assert endpoint.startswith("http://otel-collector.monitoring.svc")
    collector = _docs(K8S / "monitoring" / "otel-collector.yaml")
    service = next(d for d in collector if d["kind"] == "Service")
    assert service["metadata"]["name"] == "otel-collector"
    assert 4318 in {p["port"] for p in service["spec"]["ports"]}


def test_audit_stream_is_routed_to_its_own_index() -> None:
    """The app's audit logger name and the Fluent Bit rewrite rule must agree."""
    from apps.core.observability import AUDIT_LOGGER_NAME

    fluent = next(
        d for d in _docs(K8S / "monitoring" / "fluent-bit.yaml") if d["kind"] == "ConfigMap"
    )
    conf = fluent["data"]["fluent-bit.conf"]
    assert AUDIT_LOGGER_NAME.replace(".", r"\.") in conf
    assert "Logstash_Prefix     arer-audit" in conf
    assert "Logstash_Prefix     k8s-audit" in conf
    policy = _docs(K8S / "cluster-audit" / "audit-policy.yaml")[0]
    assert policy["kind"] == "Policy"
    secrets_rule = policy["rules"][0]
    assert secrets_rule["level"] == "Metadata"
    assert "secrets" in secrets_rule["resources"][0]["resources"]


def test_argocd_apps_point_at_real_paths() -> None:
    """Each Application's path exists and targets the repository's main branch."""
    apps = [*_docs(K8S / "argocd" / "root.yaml")]
    for path in (K8S / "argocd" / "apps").glob("*.yaml"):
        apps.extend(_docs(path))
    applications = [a for a in apps if a["kind"] == "Application"]
    assert {a["metadata"]["name"] for a in applications} >= {
        "arer-root",
        "arer-staging",
        "arer-production",
        "arer-monitoring",
    }
    for app in applications:
        source = app["spec"]["source"]
        assert (ROOT / source["path"]).is_dir(), source["path"]
        assert source["targetRevision"] == "main"
        assert source["repoURL"].endswith("algorithm_journal.git")


def test_no_real_secrets_in_git() -> None:
    """Only the template Secret exists, and it holds placeholders."""
    secrets = [
        (path, doc)
        for path in K8S.rglob("*.yaml")
        for doc in _docs(path)
        if isinstance(doc, dict) and doc.get("kind") == "Secret"
    ]
    assert [p.name for p, _ in secrets] == ["secret.example.yaml"]
    for value in secrets[0][1]["stringData"].values():
        assert value in {"", "change-me"} or "change-me" in value

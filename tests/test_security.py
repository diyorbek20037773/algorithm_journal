"""Security requirements: 2FA, permissions, uploads, rate limits, audit log."""

from __future__ import annotations

import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import Client
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Role, User
from apps.core.models import AuditLog
from apps.submissions.models import SubmissionFile
from apps.submissions.services import validate_upload

pytestmark = pytest.mark.django_db


def test_staff_without_totp_is_redirected_to_enrolment(groups, section) -> None:
    """An editor with no confirmed device is sent to 2FA enrolment (SPEC §15.15)."""
    user = User.objects.create_user(email="noteotp@example.org", password="Algorithm2026!")
    user.groups.set([groups[Role.SECTION_EDITOR]])
    client = Client()
    client.force_login(user)
    response = client.get("/en/dashboard/")
    assert response.status_code == 302
    assert "two-factor" in response.headers["Location"]


def test_staff_with_totp_reaches_the_dashboard(editor_user, site_settings, about_pages) -> None:
    """A confirmed TOTP device lifts the gate."""
    client = Client()
    client.force_login(editor_user)
    assert client.get("/en/dashboard/").status_code == 200


def test_author_is_not_forced_into_2fa(author_user, site_settings, about_pages) -> None:
    """Readers and authors are never blocked by the staff 2FA policy."""
    client = Client()
    client.force_login(author_user)
    assert client.get("/en/dashboard/").status_code == 200


def test_requires_2fa_property(editor_user, author_user) -> None:
    """Only editorial roles require a second factor."""
    assert editor_user.requires_2fa
    assert not author_user.requires_2fa


def test_has_verified_totp(editor_user) -> None:
    """The helper reflects the confirmed device."""
    assert editor_user.has_verified_totp
    TOTPDevice.objects.filter(user=editor_user).update(confirmed=False)
    assert not editor_user.has_verified_totp


def test_password_policy_requires_twelve_characters() -> None:
    """Passwords shorter than twelve characters are rejected (SPEC §11)."""
    with pytest.raises(ValidationError):
        validate_password("Short1!")
    validate_password("Algorithm2026!Secure")


def test_argon2_is_the_default_hasher() -> None:
    """Argon2 is the first hasher outside the test settings (SPEC §11).

    ``config.settings.test`` swaps in MD5 to keep the suite fast, so the
    assertion reads the base settings module directly.
    """
    from config.settings import base

    assert base.PASSWORD_HASHERS[0].endswith("Argon2PasswordHasher")


def test_anonymous_cannot_reach_the_dashboard(client_anon, about_pages, site_settings) -> None:
    """Unauthenticated users are redirected to sign in."""
    response = client_anon.get("/en/dashboard/")
    assert response.status_code == 302
    assert "login" in response.headers["Location"]


def test_anonymous_cannot_submit(client_anon, about_pages, site_settings) -> None:
    """The submission wizard requires authentication."""
    assert client_anon.get("/en/submit/").status_code == 302


def test_author_cannot_reach_the_production_queue(author_user, site_settings, about_pages) -> None:
    """Production views are closed to authors."""
    client = Client()
    client.force_login(author_user)
    response = client.get("/en/production/")
    assert response.status_code in (302, 403)


def test_author_cannot_open_another_authors_draft(
    submission, author_user, reviewers, site_settings
) -> None:
    """A draft belongs to its submitter alone."""
    client = Client()
    client.force_login(reviewers[0])
    assert client.get(f"/en/submit/{submission.pk}/step-1/").status_code == 403


def test_upload_rejects_a_disallowed_extension() -> None:
    """Executables are refused."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    upload = SimpleUploadedFile("evil.exe", b"MZ\x90\x00", content_type="application/exe")
    with pytest.raises(ValidationError):
        validate_upload(upload, SubmissionFile.Kind.MANUSCRIPT_ANON)


def test_upload_rejects_an_oversized_file(settings) -> None:
    """Files above the configured size cap are refused."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    settings.MAX_UPLOAD_SIZE_MB = 1
    upload = SimpleUploadedFile("big.pdf", b"%PDF-1.4" + b"0" * (2 * 1024 * 1024))
    with pytest.raises(ValidationError):
        validate_upload(upload, SubmissionFile.Kind.MANUSCRIPT_ANON)


def test_upload_accepts_a_valid_pdf() -> None:
    """A small PDF passes validation."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    upload = SimpleUploadedFile("paper.pdf", b"%PDF-1.4\n1 0 obj\n", content_type="application/pdf")
    validate_upload(upload, SubmissionFile.Kind.MANUSCRIPT_ANON)


def test_uploaded_files_get_uuid_paths(submission) -> None:
    """Stored file names never contain the user-supplied name (SPEC §8)."""
    for record in submission.files.all():
        assert "submissions/" in record.file.name
        stem = record.file.name.rsplit("/", 1)[-1].split(".")[0]
        assert len(stem) == 32


def test_login_is_audited(author_user, site_settings, about_pages) -> None:
    """Successful sign-ins are written to the audit log."""
    client = Client()
    client.force_login(author_user)
    assert AuditLog.objects.filter(action=AuditLog.Action.LOGIN).exists()


def test_security_headers(client_anon, about_pages, site_settings) -> None:
    """Clickjacking and MIME-sniffing protections are active."""
    response = client_anon.get("/en/")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_csrf_is_enforced_on_the_contact_form(about_pages, site_settings) -> None:
    """Posting without a CSRF token is rejected."""
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        "/en/about/contact/",
        {"name": "x", "email": "x@example.org", "subject": "s", "body": "b" * 40},
    )
    assert response.status_code == 403


def test_submission_file_download_requires_permission(
    submission, author_user, reviewers, site_settings
) -> None:
    """Only the author, the editors and assigned reviewers may download files."""
    record = submission.files.first()
    stranger = Client()
    stranger.force_login(reviewers[2])
    assert stranger.get(f"/en/dashboard/file/{record.pk}/").status_code == 403

    owner = Client()
    owner.force_login(author_user)
    assert owner.get(f"/en/dashboard/file/{record.pk}/").status_code == 200


def test_pdf_metadata_is_stripped_from_reviewer_attachments(tmp_path) -> None:
    """The PDF scrubber removes document information."""
    import pikepdf

    from apps.submissions.services import strip_pdf_metadata

    path = tmp_path / "with-metadata.pdf"
    with pikepdf.Pdf.new() as pdf:
        pdf.add_blank_page()
        with pdf.open_metadata() as meta:
            meta["dc:creator"] = ["Secret Author"]
        pdf.save(path)

    class Field:
        """Minimal stand-in for a Django FileField value."""

        def __init__(self, p):
            self.path = str(p)
            self.name = str(p)

    assert strip_pdf_metadata(Field(path)) is True
    with pikepdf.open(path) as cleaned:
        info = {str(k): str(v) for k, v in cleaned.docinfo.items()}
        # pikepdf stamps its own /Producer when it writes the file; that key
        # carries no information about the author. Nothing identifying may remain.
        assert "/Author" not in info
        assert "/Creator" not in info
        assert "/Title" not in info
        assert "Secret Author" not in " ".join(info.values())
        with cleaned.open_metadata() as meta:
            assert "Secret Author" not in str(dict(meta))

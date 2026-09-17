"""Rewrite the stored "ALGORITHM"/"ARER" leftovers of the MEZON rename.

0003 changed the defaults, but databases seeded before the rename still carry the
old name in CMS pages, site settings, board e-mails, demo accounts and
submission references. This migration rewrites those stored values in place.
"""

from __future__ import annotations

import json

from django.db import migrations, models

REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("@algorithm-journal.uz", "@mezon-journal.uz"),
    ("ALGORITHM", "MEZON"),
    ("ALGORITM", "MEZON"),
    ("АЛГОРИТМ", "МЕЗОН"),
    ("ARER-", "MRER-"),
)

TEXT_MODELS: tuple[tuple[str, str], ...] = (
    ("core", "SiteSettings"),
    ("core", "Page"),
    ("core", "Announcement"),
    ("core", "EmailTemplate"),
    ("core", "MenuItem"),
    ("journal", "EditorialBoardMember"),
)


def _replace(value: str) -> str:
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def forwards(apps, schema_editor) -> None:  # noqa: ANN001
    """Replace the old name in every stored text field that shows on the site."""
    for app_label, model_name in TEXT_MODELS:
        model = apps.get_model(app_label, model_name)
        fields = [
            f
            for f in model._meta.concrete_fields
            if isinstance(f, (models.CharField, models.TextField, models.JSONField))
        ]
        for obj in model.objects.all():
            changed: list[str] = []
            for field in fields:
                value = getattr(obj, field.attname)
                if value in (None, "", {}, []):
                    continue
                if isinstance(field, models.JSONField):
                    new = json.loads(_replace(json.dumps(value, ensure_ascii=False)))
                elif isinstance(value, str):
                    new = _replace(value)
                else:
                    continue
                if new != value:
                    setattr(obj, field.attname, new)
                    changed.append(field.attname)
            if changed:
                obj.save(update_fields=changed)

    user_model = apps.get_model("accounts", "User")
    for user in user_model.objects.filter(email__iendswith="@algorithm-journal.uz"):
        new_email = _replace(user.email)
        if not user_model.objects.filter(email__iexact=new_email).exists():
            user.email = new_email
            user.save(update_fields=["email"])

    try:
        email_model = apps.get_model("account", "EmailAddress")
    except LookupError:
        email_model = None
    if email_model is not None:
        for address in email_model.objects.filter(email__iendswith="@algorithm-journal.uz"):
            new_email = _replace(address.email)
            if not email_model.objects.filter(email__iexact=new_email).exists():
                address.email = new_email
                address.save(update_fields=["email"])

    submission_model = apps.get_model("submissions", "Submission")
    for submission in submission_model.objects.filter(reference__startswith="ARER-"):
        new_reference = _replace(submission.reference)
        if not submission_model.objects.filter(reference=new_reference).exists():
            submission.reference = new_reference
            submission.save(update_fields=["reference"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_mezon_defaults"),
        ("accounts", "0002_initial"),
        ("journal", "0005_populate_search_vector"),
        ("submissions", "0001_initial"),
        ("account", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]

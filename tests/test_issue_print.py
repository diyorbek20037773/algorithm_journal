"""Issue PDF and author offprints: layout, pagination, permissions, e-mail."""

from __future__ import annotations

import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import Client
from pypdf import PdfReader

from apps.journal.models import Article, Author, EditorialBoardMember, Galley, Issue
from apps.production import issue_print


def make_pdf(pages: int, text: str = "Body") -> bytes:
    """A small A4 PDF with ``pages`` pages of text."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    for index in range(pages):
        pdf.drawString(72, 720, f"{text} page {index + 1}")
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def set_galley(article: Article, pages: int) -> None:
    galley = article.primary_galley
    galley.file.save("galley.pdf", ContentFile(make_pdf(pages, f"Article {article.pk}")), save=True)


@pytest.fixture
def second_article(db, article) -> Article:
    """Another article in the same issue with a 3-page galley."""
    other = Article.objects.create(
        issue=article.issue,
        section=article.section,
        license=article.license,
        status=Article.Status.DRAFT,
        language="uz",
        title="Soliq maʼmuriyatchiligi va qishloq xoʻjaligi",
        title_uz="Soliq maʼmuriyatchiligi va qishloq xoʻjaligi",
        article_number=2,
    )
    Author.objects.create(
        article=other,
        order=1,
        given_name="Gʻayrat",
        family_name="Qodirov",
        email="qodirov@example.org",
        is_corresponding=True,
    )
    galley = Galley(article=other, label=Galley.Label.PDF, mime="application/pdf", is_primary=True)
    galley.file.save("g.pdf", ContentFile(make_pdf(3, "Second")), save=False)
    galley.save()
    return other


@pytest.fixture
def client_production(production_user) -> Client:
    client = Client()
    client.force_login(production_user)
    return client


def pdf_text(field_file) -> tuple[int, list[str]]:
    field_file.open("rb")
    try:
        reader = PdfReader(io.BytesIO(field_file.read()))
    finally:
        field_file.close()
    return len(reader.pages), [page.extract_text() or "" for page in reader.pages]


@pytest.mark.django_db
def test_build_numbers_pages_and_writes_back_pagination(
    article, second_article, site_settings
) -> None:
    """Front matter, contents, articles in order with continuous numbers, back cover."""
    set_galley(article, 2)
    EditorialBoardMember.objects.create(
        full_name="Nodira Zokirova",
        role=EditorialBoardMember.Role.EDITOR_IN_CHIEF,
        degree="DSc",
    )
    issue = article.issue
    issue.print_language = "uz"
    issue.save()

    result = issue_print.build_issue_print(issue)

    issue.refresh_from_db()
    article.refresh_from_db()
    second_article.refresh_from_db()
    assert issue.full_issue_pdf
    assert issue.print_page_count == result.page_count

    pages, texts = pdf_text(issue.full_issue_pdf)
    # cover + board + contents (1) + 2 + 3 article pages + back cover
    assert pages == 1 + 1 + 1 + 2 + 3 + 1
    assert "Nodira Zokirova" in texts[1]
    assert "MUNDARIJA" in texts[2]
    # continuous numbering from the cover (page 1): articles start on page 4
    assert (article.pages_start, article.pages_end) == ("4", "5")
    assert (second_article.pages_start, second_article.pages_end) == ("6", "8")
    assert f"Article {article.pk} page 1" in texts[3]
    assert "Second page 3" in texts[7]
    # Uzbek Latin text with ʻ/ʼ is embedded, not dropped
    assert "Qodirov" in texts[2]


@pytest.mark.django_db
def test_offprint_contains_front_matter_and_only_its_article(
    article, second_article, site_settings
) -> None:
    """The author copy repeats the front matter and keeps issue page numbers."""
    set_galley(article, 2)
    issue_print.build_issue_print(article.issue)
    second_article.refresh_from_db()

    pages, texts = pdf_text(second_article.offprint_pdf)
    assert pages == 1 + 1 + 1 + 3 + 1
    joined = "\n".join(texts)
    assert "Second page 1" in joined
    assert f"Article {article.pk} page 1" not in joined
    assert "6" in texts[3]


@pytest.mark.django_db
def test_first_page_number_continues_a_previous_part(article, site_settings) -> None:
    set_galley(article, 2)
    issue = article.issue
    issue.print_first_page = 55
    issue.save()
    issue_print.build_issue_print(issue)
    article.refresh_from_db()
    assert (article.pages_start, article.pages_end) == ("58", "59")


@pytest.mark.django_db
def test_request_build_refuses_articles_without_galley(article, site_settings) -> None:
    article.galleys.all().delete()
    with pytest.raises(ValidationError):
        issue_print.request_build(article.issue)


@pytest.mark.django_db
def test_run_build_marks_a_damaged_galley_as_failed(article, site_settings) -> None:
    """The fixture galley is not a real PDF: the build fails with a readable reason."""
    status = issue_print.run_build(article.issue_id)
    issue = Issue.objects.get(pk=article.issue_id)
    assert status == "failed"
    assert issue.print_status == Issue.PrintStatus.FAILED
    assert f"#{article.pk}" in issue.print_error


@pytest.mark.django_db
def test_run_build_marks_ready(article, site_settings) -> None:
    set_galley(article, 1)
    assert issue_print.run_build(article.issue_id) == "ready"
    issue = Issue.objects.get(pk=article.issue_id)
    assert issue.print_status == Issue.PrintStatus.READY
    assert issue.print_built_at is not None


@pytest.mark.django_db
def test_send_offprint_attaches_the_pdf(article, site_settings, mailoutbox) -> None:
    set_galley(article, 1)
    issue_print.build_issue_print(article.issue)
    article.refresh_from_db()

    sent = issue_print.send_offprint(article)

    assert sent == 1
    message = mailoutbox[-1]
    assert message.to == ["karimov@example.org"]
    assert message.attachments[0][2] == "application/pdf"
    article.refresh_from_db()
    assert article.offprint_sent_at is not None


@pytest.mark.django_db
def test_send_offprint_requires_a_built_offprint(article, site_settings) -> None:
    with pytest.raises(ValidationError):
        issue_print.send_offprint(article)


@pytest.mark.django_db
def test_issue_builder_is_closed_to_authors(client_author, article, site_settings) -> None:
    """Regression: production actions used to require only a signed-in account."""
    issue = article.issue
    assert client_author.get(f"/en/production/issue/{issue.pk}/").status_code == 403
    response = client_author.post(f"/en/production/issue/{issue.pk}/publish/")
    assert response.status_code == 403
    response = client_author.post(f"/en/production/issue/{issue.pk}/pdf/build/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_production_adds_selected_articles_and_builds(
    client_production, article, volume, site_settings, django_capture_on_commit_callbacks
) -> None:
    set_galley(article, 1)
    target = Issue.objects.create(volume=volume, number=2)
    draft = Article.objects.create(
        section=article.section, license=article.license, title="Draft", language="en"
    )
    galley = Galley(article=draft, label=Galley.Label.PDF, mime="application/pdf", is_primary=True)
    galley.file.save("d.pdf", ContentFile(make_pdf(2)), save=False)
    galley.save()

    response = client_production.post(
        f"/en/production/issue/{target.pk}/add/", {"articles": [draft.pk]}
    )
    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.issue_id == target.pk

    page = client_production.get(f"/en/production/issue/{target.pk}/")
    assert page.status_code == 200
    assert "Build the journal PDF" in page.content.decode()

    with django_capture_on_commit_callbacks(execute=True):
        response = client_production.post(
            f"/en/production/issue/{target.pk}/pdf/build/",
            {"print_language": "ru", "print_first_page": "1"},
        )
    assert response.status_code == 302
    target.refresh_from_db()
    assert target.print_status == Issue.PrintStatus.READY
    assert target.print_language == "ru"

    download = client_production.get(f"/en/production/issue/{target.pk}/pdf/")
    assert download.status_code == 200
    assert download["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_offprint_download_is_limited_to_its_authors(
    article, author_user, groups, site_settings
) -> None:
    set_galley(article, 1)
    issue_print.build_issue_print(article.issue)
    url = f"/en/production/article/{article.pk}/offprint/"

    stranger = Client()
    stranger.force_login(author_user)
    assert stranger.get(url).status_code == 403

    Author.objects.filter(article=article, order=1).update(user=author_user)
    assert stranger.get(url).status_code == 200


@pytest.mark.django_db
def test_remove_articles_keeps_published_ones(article, second_article, site_settings) -> None:
    removed = issue_print.remove_articles(article.issue, [article.pk, second_article.pk])
    assert removed == 1
    article.refresh_from_db()
    second_article.refresh_from_db()
    assert article.issue_id is not None  # published: stays
    assert second_article.issue_id is None


def _png(color: tuple[int, int, int]) -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (60, 85), color).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.django_db
def test_uploaded_backgrounds_and_cover_design(article, second_article, site_settings) -> None:
    """Uploaded artwork is used; the cover lists the issue's articles and a QR code."""
    set_galley(article, 1)
    site_settings.print_cover_background.save("c.png", ContentFile(_png((20, 90, 70))), save=False)
    site_settings.print_back_cover_background.save(
        "b.png", ContentFile(_png((10, 40, 50))), save=False
    )
    site_settings.print_page_background.save(
        "p.png", ContentFile(_png((240, 250, 245))), save=False
    )
    site_settings.save()
    assert site_settings.print_page_background.name.startswith("branding/print/")
    issue = article.issue
    issue.print_language = "ru"
    issue.save()

    result = issue_print.render_issue(issue)

    reader = PdfReader(io.BytesIO(result.issue_pdf))
    cover = reader.pages[0].extract_text()
    # letter-spaced labels come out one glyph per line; the Russian month does not
    assert "Электронное издание" in cover
    assert "Bank Competition" in cover
    # every page that is not a cover carries the uploaded page background image
    inner = reader.pages[3]
    assert inner["/Resources"]["/XObject"]
    assert len(reader.pages) == result.page_count


def test_built_in_artwork_renders_without_uploads() -> None:
    """The generated covers work with no pictures, logos or indexing services."""
    from apps.production import print_layout as layout

    labels = layout.IssueLabels(
        journal_name="MEZON",
        journal_subtitle="Iqtisodiy tadqiqotlar sharhi",
        running_title="MEZON",
        issue_line="2026-yil, sentyabr · 9-son",
        year_badge="2026",
        issue_badge="SENTYABR · 9-SON",
        edition_note="Elektron nashr",
        contents_title="MUNDARIJA",
        contents_rail="MUNDARIJA • СОДЕРЖАНИЕ • CONTENTS",
        contacts=[("Telefon", "+998 71 000 00 00")],
        qr_url="https://example.org/uz/issue/1/9/",
        indexing=[("Google Scholar", None)],
        highlights_label="Ushbu sonda",
        highlights=[("Gʻalla bozori va narxlar", "Qodirov Gʻayrat")],
    )
    cover = PdfReader(io.BytesIO(layout.render_cover(labels))).pages[0].extract_text()
    back = PdfReader(io.BytesIO(layout.render_back_cover(labels))).pages[0].extract_text()
    assert "2026" in cover and "Google Scholar" in cover and "Qodirov" in cover
    assert "+998 71 000 00 00" in back

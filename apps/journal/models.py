"""Published content: sections, volumes, issues, articles, authors, board."""

from __future__ import annotations

import re
import uuid
from datetime import date
from typing import Any, ClassVar

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.core.markdown import render_markdown, strip_markdown
from apps.core.models import AutoTranslitMixin, TimeStampedModel

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+")


def galley_upload_to(instance: Galley, filename: str) -> str:
    """Store galleys under a UUID path — never a user-supplied file name."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"galleys/{uuid.uuid4().hex[:2]}/{uuid.uuid4().hex}.{suffix}"


def cover_upload_to(instance: Issue, filename: str) -> str:
    """Store issue covers under a UUID path."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
    return f"covers/{uuid.uuid4().hex}.{suffix}"


def photo_upload_to(instance: EditorialBoardMember, filename: str) -> str:
    """Store board member photos under a UUID path."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"board/{uuid.uuid4().hex}.{suffix}"


class License(TimeStampedModel):
    """A content licence applied to published articles."""

    code = models.CharField(_("code"), max_length=32, unique=True)
    name = models.CharField(_("name"), max_length=128)
    url = models.URLField(_("licence URL"))
    badge_svg = models.TextField(_("badge SVG"), blank=True)
    is_default = models.BooleanField(_("default licence"), default=False)

    class Meta:
        verbose_name = _("licence")
        verbose_name_plural = _("licences")
        ordering: ClassVar[list[str]] = ["code"]

    def __str__(self) -> str:
        return self.name

    @classmethod
    def default(cls) -> License | None:
        """Return the journal's default licence (CC BY 4.0)."""
        return cls.objects.filter(is_default=True).first() or cls.objects.first()


class Section(TimeStampedModel, AutoTranslitMixin):
    """A thematic rubric of the journal."""

    slug = models.SlugField(_("slug"), max_length=128, unique=True)
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    is_research = models.BooleanField(
        _("research section"),
        default=True,
        help_text=_("Non-research sections (reviews, commentary) are excluded from the home grid."),
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("section editors"),
        blank=True,
        related_name="edited_sections",
    )
    default_jel_prefixes = models.JSONField(_("suggested JEL prefixes"), default=list, blank=True)

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering: ClassVar[list[str]] = ["order", "name"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["order"])]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Public listing of the section's articles."""
        return reverse("journal:section_detail", kwargs={"slug": self.slug})

    @property
    def article_count(self) -> int:
        """Number of publicly visible articles in this section."""
        return self.articles.public().count()


class Volume(TimeStampedModel, AutoTranslitMixin):
    """A publication volume — one calendar year of the journal."""

    number = models.PositiveSmallIntegerField(_("volume number"), unique=True)
    year = models.PositiveSmallIntegerField(_("year"), db_index=True)
    title = models.CharField(_("title"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("volume")
        verbose_name_plural = _("volumes")
        ordering: ClassVar[list[str]] = ["-number"]

    def __str__(self) -> str:
        return f"Vol. {self.number} ({self.year})"

    def get_absolute_url(self) -> str:
        """Archive page anchored on this volume."""
        return f"{reverse('journal:archive')}?year={self.year}"


class IssueQuerySet(models.QuerySet):
    """Query helpers for issues."""

    def published(self) -> IssueQuerySet:
        """Only issues released to the public."""
        return self.filter(is_published=True)


class Issue(TimeStampedModel, AutoTranslitMixin):
    """A monthly issue belonging to a volume."""

    volume = models.ForeignKey(
        Volume, verbose_name=_("volume"), on_delete=models.PROTECT, related_name="issues"
    )
    number = models.PositiveSmallIntegerField(
        _("issue number"), validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    title = models.CharField(_("title"), max_length=255, blank=True)
    description = models.TextField(_("editorial note"), blank=True)
    published_at = models.DateField(_("published at"), null=True, blank=True, db_index=True)
    is_published = models.BooleanField(_("published"), default=False)
    is_current = models.BooleanField(_("current issue"), default=False)
    cover = models.ImageField(_("cover"), upload_to=cover_upload_to, blank=True, null=True)
    doi = models.CharField(_("issue DOI"), max_length=128, blank=True)
    pages_prefix = models.CharField(_("page prefix"), max_length=16, blank=True)
    full_issue_pdf = models.FileField(
        _("full issue PDF"), upload_to=galley_upload_to, blank=True, null=True
    )

    objects = IssueQuerySet.as_manager()

    class Meta:
        verbose_name = _("issue")
        verbose_name_plural = _("issues")
        ordering: ClassVar[list[str]] = ["-volume__number", "-number"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["volume", "number"], name="unique_issue_per_volume"),
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["is_published", "-published_at"]),
            models.Index(fields=["is_current"]),
        ]

    def __str__(self) -> str:
        return f"Vol. {self.volume.number} No. {self.number} ({self.volume.year})"

    def get_absolute_url(self) -> str:
        """Table of contents for this issue."""
        return reverse(
            "journal:issue_detail",
            kwargs={"volume": self.volume.number, "issue": self.number},
        )

    @property
    def label(self) -> str:
        """Short human label, e.g. ``Vol. 1 No. 3 (2026)``."""
        return f"Vol. {self.volume.number} No. {self.number} ({self.volume.year})"

    @property
    def description_html(self) -> str:
        """Rendered editorial note."""
        return render_markdown(self.description)

    def save(self, *args, **kwargs):
        """Ensure at most one issue is flagged as current."""
        super().save(*args, **kwargs)
        if self.is_current:
            Issue.objects.exclude(pk=self.pk).filter(is_current=True).update(is_current=False)

    @classmethod
    def current(cls) -> Issue | None:
        """The issue shown on the home page."""
        return (
            cls.objects.published()
            .filter(is_current=True)
            .select_related("volume")
            .first()
            or cls.objects.published().select_related("volume").first()
        )


class Keyword(TimeStampedModel, AutoTranslitMixin):
    """A controlled-ish keyword attached to articles."""

    name = models.CharField(_("keyword"), max_length=128)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)

    class Meta:
        verbose_name = _("keyword")
        verbose_name_plural = _("keywords")
        ordering: ClassVar[list[str]] = ["name"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["slug"])]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Articles carrying this keyword."""
        return reverse("journal:keyword_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """Derive the slug from the English keyword when missing."""
        if not self.slug:
            base = slugify(self.name_en or self.name)[:130] or uuid.uuid4().hex[:8]
            slug = base
            counter = 2
            while Keyword.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class JELCode(TimeStampedModel, AutoTranslitMixin):
    """A Journal of Economic Literature classification code."""

    code = models.CharField(_("code"), max_length=8, unique=True, db_index=True)
    label = models.CharField(_("label"), max_length=255)
    parent = models.ForeignKey(
        "self", verbose_name=_("parent"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children",
    )
    level = models.PositiveSmallIntegerField(_("level"), default=1)

    class Meta:
        verbose_name = _("JEL code")
        verbose_name_plural = _("JEL codes")
        ordering: ClassVar[list[str]] = ["code"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["level", "code"])]

    def __str__(self) -> str:
        return f"{self.code} — {self.label}"

    def get_absolute_url(self) -> str:
        """Articles classified under this JEL code."""
        return reverse("journal:jel_detail", kwargs={"code": self.code})


class ArticleQuerySet(models.QuerySet):
    """Query helpers restricting visibility to published content."""

    def public(self) -> ArticleQuerySet:
        """Articles a reader may see (published, online first, retracted)."""
        return self.filter(
            status__in=[
                Article.Status.PUBLISHED,
                Article.Status.ONLINE_FIRST,
                Article.Status.RETRACTED,
            ]
        )

    def published(self) -> ArticleQuerySet:
        """Articles that have been assigned to a published issue."""
        return self.filter(status=Article.Status.PUBLISHED)

    def online_first(self) -> ArticleQuerySet:
        """Ahead-of-issue articles."""
        return self.filter(status=Article.Status.ONLINE_FIRST)

    def with_related(self) -> ArticleQuerySet:
        """Prefetch everything a list or detail template needs."""
        return self.select_related("issue", "issue__volume", "section", "license").prefetch_related(
            "authors", "keywords", "jel_codes", "galleys"
        )


class Article(TimeStampedModel, AutoTranslitMixin):
    """A scholarly article — the central published object."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ONLINE_FIRST = "online_first", _("Online First")
        PUBLISHED = "published", _("Published")
        RETRACTED = "retracted", _("Retracted")
        WITHDRAWN = "withdrawn", _("Withdrawn")

    class DOIStatus(models.TextChoices):
        NONE = "none", _("Not assigned")
        RESERVED = "reserved", _("Reserved")
        REGISTERED = "registered", _("Registered")
        FAILED = "failed", _("Registration failed")
        UPDATED = "updated", _("Metadata updated")

    class ArticleType(models.TextChoices):
        RESEARCH = "research", _("Research article")
        REVIEW = "review", _("Review article")
        SHORT = "short_communication", _("Short communication")
        BOOK_REVIEW = "book_review", _("Book review")
        EDITORIAL = "editorial", _("Editorial")

    issue = models.ForeignKey(
        Issue, verbose_name=_("issue"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="articles",
    )
    section = models.ForeignKey(
        Section, verbose_name=_("section"), on_delete=models.PROTECT, related_name="articles"
    )
    article_type = models.CharField(
        _("article type"), max_length=32, choices=ArticleType.choices, default=ArticleType.RESEARCH
    )

    title = models.CharField(_("title"), max_length=500)
    subtitle = models.CharField(_("subtitle"), max_length=500, blank=True)
    abstract = models.TextField(_("abstract"), blank=True)
    slug = models.SlugField(_("slug"), max_length=255, blank=True)

    keywords = models.ManyToManyField(
        Keyword, verbose_name=_("keywords"), blank=True, related_name="articles"
    )
    jel_codes = models.ManyToManyField(
        JELCode, verbose_name=_("JEL codes"), blank=True, related_name="articles"
    )
    language = models.CharField(
        _("article language"),
        max_length=10,
        default="en",
        choices=[("en", "English"), ("uz", "Oʻzbekcha"), ("ru", "Русский")],
    )

    doi = models.CharField(_("DOI"), max_length=128, blank=True, db_index=True)
    doi_status = models.CharField(
        _("DOI status"), max_length=16, choices=DOIStatus.choices, default=DOIStatus.NONE
    )

    pages_start = models.CharField(_("first page"), max_length=16, blank=True)
    pages_end = models.CharField(_("last page"), max_length=16, blank=True)
    elocation_id = models.CharField(_("e-location ID"), max_length=32, blank=True)
    article_number = models.PositiveSmallIntegerField(_("article number"), null=True, blank=True)

    received_at = models.DateField(_("received"), null=True, blank=True)
    revised_at = models.DateField(_("revised"), null=True, blank=True)
    accepted_at = models.DateField(_("accepted"), null=True, blank=True)
    published_online_at = models.DateField(_("published online"), null=True, blank=True)
    published_at = models.DateField(_("published"), null=True, blank=True, db_index=True)

    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True
    )

    license = models.ForeignKey(
        License, verbose_name=_("licence"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="articles",
    )
    copyright_holder = models.CharField(
        _("copyright holder"), max_length=255, default="The Author(s)"
    )
    funding_statement = models.TextField(_("funding statement"), blank=True)
    conflict_of_interest_statement = models.TextField(
        _("conflict of interest statement"),
        blank=True,
        default="The authors declare no conflict of interest.",
    )
    data_availability_statement = models.TextField(_("data availability statement"), blank=True)
    ai_use_statement = models.TextField(
        _("AI use statement"),
        blank=True,
        default="No generative AI tools were used in the preparation of this article.",
    )
    acknowledgements = models.TextField(_("acknowledgements"), blank=True)
    retraction_notice = models.TextField(_("retraction notice"), blank=True)

    submission = models.OneToOneField(
        "submissions.Submission", verbose_name=_("submission"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="published_article",
    )

    views_count = models.PositiveIntegerField(_("views"), default=0)
    downloads_count = models.PositiveIntegerField(_("downloads"), default=0)
    cited_by_count = models.PositiveIntegerField(_("cited by (Crossref)"), default=0)
    cited_by_updated_at = models.DateTimeField(_("cited-by updated"), null=True, blank=True)
    is_featured = models.BooleanField(_("featured"), default=False)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering: ClassVar[list[str]] = ["-published_at", "-published_online_at", "-id"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["issue", "article_number"]),
            models.Index(fields=["section", "-published_at"]),
            models.Index(fields=["doi"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Canonical, human-readable landing page URL."""
        if self.slug:
            return reverse("journal:article_detail_slug", kwargs={"pk": self.pk, "slug": self.slug})
        return reverse("journal:article_detail", kwargs={"pk": self.pk})

    @property
    def canonical_url(self) -> str:
        """Language-neutral canonical URL used in Crossref and OAI records."""
        return f"{settings.SITE_URL}{self.get_absolute_url()}"

    @property
    def pdf_url(self) -> str:
        """Stable, language-neutral PDF URL (``citation_pdf_url``)."""
        return reverse("article_pdf", kwargs={"pk": self.pk})

    @property
    def absolute_pdf_url(self) -> str:
        """Absolute PDF URL for metadata consumers."""
        return f"{settings.SITE_URL}{self.pdf_url}"

    @property
    def doi_url(self) -> str:
        """Resolvable DOI link, or an empty string."""
        return f"https://doi.org/{self.doi}" if self.doi else ""

    @property
    def is_public(self) -> bool:
        """True when readers may open the landing page."""
        return self.status in {self.Status.PUBLISHED, self.Status.ONLINE_FIRST, self.Status.RETRACTED}

    @property
    def is_online_first(self) -> bool:
        """True for ahead-of-issue articles."""
        return self.status == self.Status.ONLINE_FIRST

    @property
    def pages(self) -> str:
        """Page range as printed in citations."""
        if self.pages_start and self.pages_end:
            return f"{self.pages_start}–{self.pages_end}"
        return self.pages_start or self.elocation_id or ""

    @property
    def primary_galley(self) -> Galley | None:
        """The primary PDF galley served by the download route."""
        galleys = list(self.galleys.all())
        for galley in galleys:
            if galley.is_primary and galley.mime == "application/pdf":
                return galley
        for galley in galleys:
            if galley.mime == "application/pdf":
                return galley
        return None

    @property
    def xml_galley(self) -> Galley | None:
        """The JATS XML galley, when one was uploaded."""
        return next((g for g in self.galleys.all() if g.mime in {"application/xml", "text/xml"}), None)

    @property
    def display_date(self) -> date | None:
        """Best available publication date."""
        return self.published_at or self.published_online_at

    @property
    def abstract_html(self) -> str:
        """Sanitised HTML rendering of the abstract."""
        return render_markdown(self.abstract)

    @property
    def abstract_plain(self) -> str:
        """Plain-text abstract for meta tags."""
        return strip_markdown(self.abstract)

    @property
    def citation_apa(self) -> str:
        """Pre-rendered APA 7 citation string (no JavaScript required)."""
        from apps.citations.services import render_citation

        return render_citation(self, "apa")

    def author_list(self) -> list[Author]:
        """Ordered authorship rows."""
        return list(self.authors.all())

    def authors_display(self, separator: str = ", ") -> str:
        """Comma-separated author names for lists and meta tags."""
        return separator.join(a.full_name for a in self.author_list())

    def build_slug(self) -> str:
        """Slug derived from the English title."""
        base = slugify(getattr(self, "title_en", None) or self.title)[:200]
        return base or f"article-{self.pk or uuid.uuid4().hex[:6]}"

    def save(self, *args, **kwargs):
        """Fill in the slug and default licence before saving."""
        if self.license_id is None:
            default = License.default()
            if default is not None:
                self.license = default
        super().save(*args, **kwargs)
        if not self.slug:
            Article.objects.filter(pk=self.pk).update(slug=self.build_slug())
            self.slug = self.build_slug()


class Author(TimeStampedModel, AutoTranslitMixin):
    """An authorship row on a published article."""

    CREDIT_ROLES: ClassVar[list[str]] = [
        "Conceptualization",
        "Data curation",
        "Formal analysis",
        "Funding acquisition",
        "Investigation",
        "Methodology",
        "Project administration",
        "Resources",
        "Software",
        "Supervision",
        "Validation",
        "Visualization",
        "Writing – original draft",
        "Writing – review & editing",
    ]

    article = models.ForeignKey(
        Article, verbose_name=_("article"), on_delete=models.CASCADE, related_name="authors"
    )
    order = models.PositiveSmallIntegerField(_("order"), default=1)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("account"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="authorships",
    )
    given_name = models.CharField(_("given name"), max_length=128)
    family_name = models.CharField(_("family name"), max_length=128)
    given_name_native = models.CharField(_("given name (native script)"), max_length=128, blank=True)
    family_name_native = models.CharField(
        _("family name (native script)"), max_length=128, blank=True
    )
    email = models.EmailField(_("e-mail"), blank=True)
    is_corresponding = models.BooleanField(_("corresponding author"), default=False)
    orcid = models.CharField(_("ORCID iD"), max_length=19, blank=True, db_index=True)
    orcid_verified = models.BooleanField(_("ORCID verified"), default=False)
    affiliation = models.CharField(_("affiliation"), max_length=300, blank=True)
    affiliation_ror = models.CharField(_("ROR ID"), max_length=64, blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True)
    country = CountryField(_("country"), blank=True)
    bio = models.TextField(_("biography"), blank=True)
    credit_roles = models.JSONField(_("CRediT roles"), default=list, blank=True)

    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")
        ordering: ClassVar[list[str]] = ["article", "order"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["family_name", "given_name"]),
            models.Index(fields=["orcid"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        """``Given Family`` in Latin script."""
        return f"{self.given_name} {self.family_name}".strip()

    @property
    def citation_name(self) -> str:
        """``Family, Given`` as required by Highwire ``citation_author``."""
        return f"{self.family_name}, {self.given_name}".strip(", ")

    @property
    def initials(self) -> str:
        """Initials used in APA-style citations."""
        return " ".join(f"{p[0]}." for p in self.given_name.split() if p)

    @property
    def slug(self) -> str:
        """Stable slug used for author landing pages."""
        return slugify(f"{self.given_name}-{self.family_name}") or "author"

    @property
    def orcid_url(self) -> str:
        """Public ORCID record URL, or an empty string."""
        return f"https://orcid.org/{self.orcid}" if self.orcid else ""

    @property
    def affiliation_display(self) -> str:
        """Affiliation with city and country appended."""
        parts = [self.affiliation, self.city]
        if self.country:
            parts.append(self.country.name)
        return ", ".join(p for p in parts if p)

    def get_absolute_url(self) -> str:
        """Author landing page listing every article by this person."""
        return reverse("journal:author_detail", kwargs={"slug": self.slug})


class Reference(TimeStampedModel):
    """One bibliographic reference of an article."""

    article = models.ForeignKey(
        Article, verbose_name=_("article"), on_delete=models.CASCADE, related_name="references"
    )
    order = models.PositiveSmallIntegerField(_("order"), default=1)
    raw_text = models.TextField(_("reference text"))
    doi = models.CharField(_("DOI"), max_length=128, blank=True)
    structured = models.JSONField(_("structured data"), default=dict, blank=True)

    class Meta:
        verbose_name = _("reference")
        verbose_name_plural = _("references")
        ordering: ClassVar[list[str]] = ["article", "order"]

    def __str__(self) -> str:
        return self.raw_text[:80]

    @property
    def doi_url(self) -> str:
        """Resolvable DOI link, or an empty string."""
        return f"https://doi.org/{self.doi}" if self.doi else ""

    @property
    def scholar_url(self) -> str:
        """Google Scholar search link for this reference."""
        from urllib.parse import quote_plus

        return f"https://scholar.google.com/scholar?q={quote_plus(self.raw_text[:250])}"

    def save(self, *args, **kwargs):
        """Auto-detect a DOI inside the raw reference text."""
        if not self.doi:
            match = DOI_RE.search(self.raw_text or "")
            if match:
                self.doi = match.group(0).rstrip(".,;)")
        super().save(*args, **kwargs)


class Galley(TimeStampedModel):
    """A downloadable rendition of an article (PDF, XML, supplementary file)."""

    class Label(models.TextChoices):
        PDF = "PDF", _("PDF")
        PDF_UZ = "PDF-UZ", _("PDF (Uzbek)")
        PDF_RU = "PDF-RU", _("PDF (Russian)")
        XML = "XML", _("JATS XML")
        SUPPLEMENTARY = "SUPP", _("Supplementary")

    article = models.ForeignKey(
        Article, verbose_name=_("article"), on_delete=models.CASCADE, related_name="galleys"
    )
    label = models.CharField(_("label"), max_length=16, choices=Label.choices, default=Label.PDF)
    language = models.CharField(_("language"), max_length=10, default="en")
    file = models.FileField(_("file"), upload_to=galley_upload_to)
    original_file = models.FileField(
        _("unstamped original"), upload_to=galley_upload_to, blank=True, null=True
    )
    mime = models.CharField(_("MIME type"), max_length=128, default="application/pdf")
    size = models.PositiveIntegerField(_("size in bytes"), default=0)
    is_primary = models.BooleanField(_("primary"), default=False)
    order = models.PositiveSmallIntegerField(_("order"), default=1)

    class Meta:
        verbose_name = _("galley")
        verbose_name_plural = _("galleys")
        ordering: ClassVar[list[str]] = ["article", "order"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["article", "is_primary"])]

    def __str__(self) -> str:
        return f"{self.get_label_display()} — {self.article_id}"

    def get_absolute_url(self) -> str:
        """Download route counting the access event."""
        return reverse("galley_download", kwargs={"pk": self.article_id, "galley_id": self.pk})

    @property
    def size_display(self) -> str:
        """Human-readable file size."""
        size = float(self.size or 0)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"


class EditorialBoardMember(TimeStampedModel, AutoTranslitMixin):
    """A member of the editorial, advisory or reviewer board."""

    class Role(models.TextChoices):
        EDITOR_IN_CHIEF = "editor_in_chief", _("Editor-in-Chief")
        DEPUTY_EDITOR = "deputy_editor", _("Deputy Editor")
        MANAGING_EDITOR = "managing_editor", _("Managing Editor")
        SECTION_EDITOR = "section_editor", _("Section Editor")
        BOARD_MEMBER = "board_member", _("Editorial Board Member")
        ADVISORY = "advisory", _("International Advisory Board")
        REVIEWER_BOARD = "reviewer_board", _("Reviewer Board")

    #: Display order of the role groups on the board page.
    ROLE_ORDER: ClassVar[list[str]] = [
        Role.EDITOR_IN_CHIEF,
        Role.DEPUTY_EDITOR,
        Role.MANAGING_EDITOR,
        Role.SECTION_EDITOR,
        Role.BOARD_MEMBER,
        Role.ADVISORY,
        Role.REVIEWER_BOARD,
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("account"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="board_memberships",
    )
    full_name = models.CharField(_("full name"), max_length=255)
    role = models.CharField(
        _("role"), max_length=32, choices=Role.choices, default=Role.BOARD_MEMBER, db_index=True
    )
    degree = models.CharField(_("academic degree"), max_length=255, blank=True)
    academic_title = models.CharField(_("academic title"), max_length=255, blank=True)
    affiliation = models.CharField(_("affiliation"), max_length=300, blank=True)
    country = CountryField(_("country"), blank=True)
    orcid = models.CharField(_("ORCID iD"), max_length=19, blank=True)
    scopus_author_id = models.CharField(_("Scopus Author ID"), max_length=32, blank=True)
    email = models.EmailField(_("e-mail"), blank=True)
    photo = models.ImageField(_("photo"), upload_to=photo_upload_to, blank=True, null=True)
    bio = models.TextField(_("biography"), blank=True)
    expertise = models.CharField(_("expertise"), max_length=500, blank=True)
    sections = models.ManyToManyField(
        Section, verbose_name=_("sections"), blank=True, related_name="board_members"
    )
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    is_demo = models.BooleanField(
        _("demo entry"),
        default=False,
        help_text=_("Seeded placeholder — replace with a real board member."),
    )

    class Meta:
        verbose_name = _("editorial board member")
        verbose_name_plural = _("editorial board members")
        ordering: ClassVar[list[str]] = ["order", "full_name"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["role", "order"])]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_role_display()})"

    def get_absolute_url(self) -> str:
        """Anchor on the editorial board page."""
        return f"{reverse('journal:editorial_board')}#member-{self.pk}"

    @property
    def orcid_url(self) -> str:
        """Public ORCID record URL, or an empty string."""
        return f"https://orcid.org/{self.orcid}" if self.orcid else ""

    @property
    def scopus_url(self) -> str:
        """Scopus author profile URL, or an empty string."""
        if not self.scopus_author_id:
            return ""
        return f"https://www.scopus.com/authid/detail.uri?authorId={self.scopus_author_id}"

    @property
    def obfuscated_email(self) -> str:
        """E-mail with the ``@`` replaced, to slow naive harvesters."""
        return self.email.replace("@", " [at] ") if self.email else ""

    @property
    def initials(self) -> str:
        """Initials used by the avatar placeholder."""
        parts = [p for p in self.full_name.split() if p]
        return "".join(p[0].upper() for p in parts[:2])


class ArticleStatisticSnapshot(TimeStampedModel):
    """Denormalised per-article totals used by the public statistics page."""

    article = models.OneToOneField(
        Article, verbose_name=_("article"), on_delete=models.CASCADE, related_name="statistics"
    )
    views_total = models.PositiveIntegerField(_("total views"), default=0)
    downloads_total = models.PositiveIntegerField(_("total downloads"), default=0)
    views_last_30d = models.PositiveIntegerField(_("views (30 days)"), default=0)
    downloads_last_30d = models.PositiveIntegerField(_("downloads (30 days)"), default=0)
    computed_at = models.DateTimeField(_("computed at"), default=timezone.now)

    class Meta:
        verbose_name = _("article statistics")
        verbose_name_plural = _("article statistics")
        ordering: ClassVar[list[str]] = ["-views_total"]

    def __str__(self) -> str:
        return f"Stats for #{self.article_id}"

    def as_dict(self) -> dict[str, Any]:
        """Serialise the snapshot for API responses."""
        return {
            "views_total": self.views_total,
            "downloads_total": self.downloads_total,
            "views_last_30d": self.views_last_30d,
            "downloads_last_30d": self.downloads_last_30d,
        }

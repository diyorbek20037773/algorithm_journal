"""Serialisers for the read-only public API."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.journal.models import Article, Author, Issue, Section


class AuthorSerializer(serializers.ModelSerializer):
    """Public author representation (e-mail only for corresponding authors)."""

    full_name = serializers.CharField(read_only=True)
    country = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = (
            "order",
            "given_name",
            "family_name",
            "full_name",
            "orcid",
            "affiliation",
            "city",
            "country",
            "is_corresponding",
            "email",
        )

    def get_country(self, obj: Author) -> str:
        """ISO country code, or an empty string."""
        return obj.country.code if obj.country else ""

    def get_email(self, obj: Author) -> str:
        """Only corresponding authors expose an e-mail address."""
        return obj.email if obj.is_corresponding else ""


class SectionSerializer(serializers.ModelSerializer):
    """Journal section."""

    class Meta:
        model = Section
        fields = ("slug", "name", "description", "order")


class IssueListSerializer(serializers.ModelSerializer):
    """Issue summary."""

    volume = serializers.IntegerField(source="volume.number", read_only=True)
    year = serializers.IntegerField(source="volume.year", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ("id", "volume", "number", "year", "title", "published_at", "doi", "url")

    def get_url(self, obj: Issue) -> str:
        """Absolute URL of the issue table of contents."""
        request = self.context.get("request")
        url = obj.get_absolute_url()
        return request.build_absolute_uri(url) if request else url


class ArticleListSerializer(serializers.ModelSerializer):
    """Article summary used by list endpoints."""

    authors = AuthorSerializer(many=True, read_only=True)
    section = serializers.CharField(source="section.name", read_only=True)
    keywords = serializers.SerializerMethodField()
    jel_codes = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    issue_number = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "subtitle",
            "abstract",
            "doi",
            "status",
            "language",
            "section",
            "authors",
            "keywords",
            "jel_codes",
            "volume",
            "issue_number",
            "pages_start",
            "pages_end",
            "published_at",
            "published_online_at",
            "views_count",
            "downloads_count",
            "cited_by_count",
            "url",
            "pdf_url",
        )

    def get_keywords(self, obj: Article) -> list[str]:
        """Keyword names in the active language."""
        return [k.name for k in obj.keywords.all()]

    def get_jel_codes(self, obj: Article) -> list[str]:
        """JEL classification codes."""
        return [j.code for j in obj.jel_codes.all()]

    def get_url(self, obj: Article) -> str:
        """Absolute landing page URL."""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url()) if request else obj.canonical_url

    def get_pdf_url(self, obj: Article) -> str:
        """Absolute PDF URL."""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.pdf_url) if request else obj.absolute_pdf_url

    def get_volume(self, obj: Article) -> int | None:
        """Volume number, or ``None`` for Online First."""
        return obj.issue.volume.number if obj.issue_id else None

    def get_issue_number(self, obj: Article) -> int | None:
        """Issue number, or ``None`` for Online First."""
        return obj.issue.number if obj.issue_id else None


class ArticleDetailSerializer(ArticleListSerializer):
    """Full article representation including references and statements."""

    references = serializers.SerializerMethodField()
    license = serializers.SerializerMethodField()
    titles = serializers.SerializerMethodField()
    abstracts = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = (
            *ArticleListSerializer.Meta.fields,
            "titles",
            "abstracts",
            "references",
            "license",
            "funding_statement",
            "conflict_of_interest_statement",
            "data_availability_statement",
            "ai_use_statement",
            "acknowledgements",
            "received_at",
            "accepted_at",
        )

    def get_references(self, obj: Article) -> list[dict[str, Any]]:
        """Ordered reference list with detected DOIs."""
        return [{"order": r.order, "text": r.raw_text, "doi": r.doi} for r in obj.references.all()]

    def get_license(self, obj: Article) -> dict[str, str]:
        """Licence code, name and URL."""
        if obj.license is None:
            return {}
        return {"code": obj.license.code, "name": obj.license.name, "url": obj.license.url}

    def get_titles(self, obj: Article) -> dict[str, str]:
        """Title in every language that has content."""
        return {
            code.replace("_", "-"): getattr(obj, f"title_{code}")
            for code in ("en", "uz", "uz_cyrl", "ru")
            if getattr(obj, f"title_{code}", None)
        }

    def get_abstracts(self, obj: Article) -> dict[str, str]:
        """Abstract in every language that has content."""
        return {
            code.replace("_", "-"): getattr(obj, f"abstract_{code}")
            for code in ("en", "uz", "uz_cyrl", "ru")
            if getattr(obj, f"abstract_{code}", None)
        }

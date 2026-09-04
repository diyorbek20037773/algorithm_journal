"""Populate the database with the journal's configuration and demo content.

The command is idempotent: running it twice leaves the database in the same
state.  It creates site settings, sections, licences, the JEL tree, CMS pages,
e-mail templates, indexing services, the demonstration editorial board, demo
users, three published issues with twelve articles, two Online First articles,
usage statistics and submissions in every workflow state.
"""

from __future__ import annotations

import datetime as dt
import random
from typing import Any

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models import Profile, Role, User
from apps.core.models import (
    Announcement,
    EmailTemplate,
    IndexingService,
    Page,
    SiteSettings,
)
from apps.journal.models import (
    Article,
    Author,
    EditorialBoardMember,
    Galley,
    Issue,
    JELCode,
    Keyword,
    License,
    Reference,
    Section,
    Volume,
)
from seed import articles as article_seed
from seed import content as content_seed
from seed.demo_pdf import build_article_pdf
from seed.demo_submissions import create_demo_submissions
from seed.jel_loader import load_jel

DEMO_PASSWORD = "Algorithm2026!"
LANGS = ("en", "uz", "ru")


def set_translated(obj: Any, field: str, values: dict[str, str]) -> None:
    """Assign a translated field in every language provided."""
    for code, value in values.items():
        setattr(obj, f"{field}_{code.replace('-', '_')}", value)
    setattr(obj, field, values.get("en", ""))


class Command(BaseCommand):
    """``manage.py seed_demo`` — load the complete demonstration journal."""

    help = "Seed the journal with settings, policies and demonstration content."

    def add_arguments(self, parser) -> None:
        """Register command-line options."""
        parser.add_argument(
            "--minimal",
            action="store_true",
            help="Seed configuration and pages only, without demo articles or submissions.",
        )
        parser.add_argument(
            "--reset-content",
            action="store_true",
            help="Delete existing demo articles and submissions before seeding.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        """Run every seeding step in order."""
        self.rng = random.Random(20260904)
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding ARER demonstration data"))

        if options["reset_content"]:
            self._reset_content()

        self.seed_settings()
        self.seed_licenses()
        self.seed_sections()
        self.seed_jel()
        self.seed_indexing()
        self.seed_pages()
        self.seed_email_templates()
        self.seed_announcements()
        users = self.seed_users()
        self.seed_board(users)

        if options["minimal"]:
            self.stdout.write(self.style.SUCCESS("Minimal seed complete."))
            return

        issues = self.seed_issues()
        self.seed_articles(issues)
        self.seed_statistics()
        created = create_demo_submissions(self.stdout, self.style)
        self.stdout.write(self.style.SUCCESS(f"Created {created} demonstration submissions."))
        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete. Sign in with admin@algorithm-journal.uz / Algorithm2026!"
            )
        )

    # ------------------------------------------------------------------ reset
    def _reset_content(self) -> None:
        """Delete demo articles, issues and submissions."""
        from apps.submissions.models import Submission

        Submission.objects.all().delete()
        Article.objects.all().delete()
        Issue.objects.all().delete()
        Volume.objects.all().delete()
        self.stdout.write("  reset existing demo content")

    # --------------------------------------------------------------- settings
    def seed_settings(self) -> None:
        """Create or update the SiteSettings singleton in four languages."""
        site = SiteSettings.load()
        set_translated(
            site,
            "journal_name",
            {
                "en": "ALGORITHM: Review of Economic Research",
                "uz": "«ALGORITM» — iqtisodiy tadqiqotlar sharhi",
                "ru": "«АЛГОРИТМ» — обзор экономических исследований",
            },
        )
        site.journal_name_uz_cyrl = "«АЛГОРИТМ» — иқтисодий тадқиқотлар шарҳи"
        set_translated(
            site,
            "journal_subtitle",
            {
                "en": "Open-access, double-blind peer-reviewed research in economics",
                "uz": "Ochiq kirishli, ikki tomonlama yashirin taqrizdan oʻtadigan iqtisodiy tadqiqotlar",
                "ru": "Исследования по экономике в открытом доступе с двойным слепым рецензированием",
            },
        )
        set_translated(
            site,
            "publisher_name",
            {
                "en": "Founder organisation (to be confirmed)",
                "uz": "Muassis tashkilot (tasdiqlanishi kerak)",
                "ru": "Организация-учредитель (подлежит уточнению)",
            },
        )
        set_translated(
            site,
            "publisher_address",
            {
                "en": "Editorial office, Tashkent, Uzbekistan\n(postal address to be confirmed)",
                "uz": "Tahririyat, Toshkent, Oʻzbekiston\n(pochta manzili tasdiqlanishi kerak)",
                "ru": "Редакция, Ташкент, Узбекистан\n(почтовый адрес подлежит уточнению)",
            },
        )
        set_translated(
            site,
            "contact_address",
            {
                "en": "Editorial office, Tashkent, Uzbekistan",
                "uz": "Tahririyat, Toshkent, Oʻzbekiston",
                "ru": "Редакция, Ташкент, Узбекистан",
            },
        )
        set_translated(
            site,
            "frequency_text",
            {
                "en": "Monthly — 12 issues per year, plus Online First",
                "uz": "Oyiga bir marta — yiliga 12 son va Online First",
                "ru": "Ежемесячно — 12 выпусков в год и Online First",
            },
        )
        set_translated(
            site,
            "registration_authority",
            {
                "en": "Registration authority (to be confirmed)",
                "uz": "Roʻyxatga oluvchi organ (tasdiqlanishi kerak)",
                "ru": "Регистрирующий орган (подлежит уточнению)",
            },
        )
        site.short_code = "ARER"
        site.founded_year = 2026
        site.contact_email = "editor@algorithm-journal.uz"
        site.similarity_threshold = 20
        site.show_online_first = True
        site.social_links = {"telegram": "", "linkedin": ""}
        site.save()
        self.stdout.write("  site settings")

    # --------------------------------------------------------------- licences
    def seed_licenses(self) -> None:
        """Create the CC licences."""
        for row in content_seed.LICENSES:
            License.objects.update_or_create(
                code=row["code"],
                defaults={"name": row["name"], "url": row["url"], "is_default": row["is_default"]},
            )
        self.stdout.write(f"  {len(content_seed.LICENSES)} licences")

    # --------------------------------------------------------------- sections
    def seed_sections(self) -> None:
        """Create the nine journal sections in four languages."""
        for row in content_seed.SECTIONS:
            section, _created = Section.objects.get_or_create(slug=row["slug"])
            set_translated(section, "name", row["name"])
            set_translated(section, "description", row["description"])
            section.order = row["order"]
            section.is_research = row["is_research"]
            section.is_active = True
            section.default_jel_prefixes = row["jel"]
            section.save()
        self.stdout.write(f"  {len(content_seed.SECTIONS)} sections")

    # -------------------------------------------------------------------- JEL
    def seed_jel(self) -> None:
        """Load the JEL classification tree."""
        count = load_jel()
        self.stdout.write(f"  {count} JEL codes")

    # --------------------------------------------------------------- indexing
    def seed_indexing(self) -> None:
        """Create indexing services; only real ones are active."""
        site = SiteSettings.load()
        active = []
        for row in content_seed.INDEXING_SERVICES:
            service, _created = IndexingService.objects.get_or_create(slug=row["slug"])
            service.name = row["name"]
            service.url = row["url"]
            service.is_active = row["is_active"]
            service.order = row["order"]
            set_translated(service, "note", row["note"])
            service.save()
            if service.is_active:
                active.append(service)
        site.indexing_badges.set(active)
        self.stdout.write(f"  {len(content_seed.INDEXING_SERVICES)} indexing services")

    # ------------------------------------------------------------------ pages
    def seed_pages(self) -> None:
        """Create every CMS page in four languages."""
        for row in content_seed.PAGES:
            page, _created = Page.objects.get_or_create(slug=row["slug"])
            set_translated(page, "title", row["title"])
            set_translated(page, "body", row["body"])
            set_translated(page, "seo_description", row["seo"])
            page.menu_group = row["menu_group"]
            page.menu_order = row["order"]
            page.is_published = True
            page.needs_editorial_review = True
            page.save()
        self.stdout.write(f"  {len(content_seed.PAGES)} CMS pages")

    # -------------------------------------------------------- email templates
    def seed_email_templates(self) -> None:
        """Create the editable transactional e-mail templates."""
        for row in content_seed.EMAIL_TEMPLATES:
            template, _created = EmailTemplate.objects.get_or_create(event=row["event"])
            set_translated(template, "subject", row["subject"])
            set_translated(template, "body", row["body"])
            template.placeholders = row["placeholders"]
            template.is_active = True
            template.save()
        self.stdout.write(f"  {len(content_seed.EMAIL_TEMPLATES)} e-mail templates")

    # ---------------------------------------------------------- announcements
    def seed_announcements(self) -> None:
        """Create the demonstration announcements."""
        now = timezone.now()
        for row in content_seed.ANNOUNCEMENTS:
            announcement, _created = Announcement.objects.get_or_create(slug=row["slug"])
            set_translated(announcement, "title", row["title"])
            set_translated(announcement, "body", row["body"])
            announcement.published_at = now - dt.timedelta(days=row["days_ago"])
            announcement.is_pinned = row["is_pinned"]
            announcement.save()
        self.stdout.write(f"  {len(content_seed.ANNOUNCEMENTS)} announcements")

    # ------------------------------------------------------------------ users
    def seed_users(self) -> dict[str, User]:
        """Create the demo accounts and their role groups."""
        groups = {role: Group.objects.get_or_create(name=role)[0] for role, _ in Role.choices}

        definitions = [
            ("admin", "Aziza", "Tursunova", [Role.ADMIN], True, True),
            ("eic", "Nodira", "Rakhimova", [Role.EDITOR_IN_CHIEF], True, False),
            ("editor", "Kamola", "Yusupova", [Role.SECTION_EDITOR], True, False),
            ("production", "Jasur", "Qodirov", [Role.PRODUCTION_EDITOR], True, False),
            ("reviewer1", "Aziz", "Karimov", [Role.REVIEWER], False, False),
            ("reviewer2", "Elena", "Sokolova", [Role.REVIEWER], False, False),
            ("reviewer3", "Ayse", "Demir", [Role.REVIEWER], False, False),
            ("author", "Bekzod", "Toshmatov", [Role.AUTHOR], False, False),
        ]

        users: dict[str, User] = {}
        for key, first, last, roles, is_staff, is_superuser in definitions:
            email = f"{key}@algorithm-journal.uz"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                    "is_active": True,
                },
            )
            if created or not user.has_usable_password():
                user.set_password(DEMO_PASSWORD)
            user.first_name = first
            user.last_name = last
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.is_reviewer = Role.REVIEWER in roles
            user.must_enroll_2fa = is_staff
            user.preferred_language = "uz" if key in {"author", "editor"} else "en"
            user.save()
            user.groups.set([groups[r] for r in roles] + [groups[Role.AUTHOR]])
            self._profile_for(user, key)
            users[key] = user

        # The section editor handles sections 2 and 3.
        for slug in ("macroeconomics-monetary-fiscal-policy", "public-finance-taxation-customs"):
            section = Section.objects.filter(slug=slug).first()
            if section is not None:
                section.editors.add(users["editor"])

        self.stdout.write(f"  {len(users)} demo users (password: {DEMO_PASSWORD})")
        return users

    def _profile_for(self, user: User, key: str) -> None:
        """Fill a demo profile with affiliation, ORCID and expertise."""
        profile, _created = Profile.objects.get_or_create(user=user)
        data = {
            "admin": ("Editorial office", "UZ", "0000-0002-2000-0001", "Systems administration"),
            "eic": ("Institute of Economic Research", "UZ", "0000-0002-2000-0002", "Macroeconomic policy, structural reform"),
            "editor": ("Institute of Economic Research", "UZ", "0000-0002-2000-0003", "Public finance, taxation, fiscal policy"),
            "production": ("Editorial office", "UZ", "0000-0002-2000-0004", "Production and typesetting"),
            "reviewer1": ("Banking and Finance Academy", "UZ", "0000-0002-2000-0005", "Banking, credit markets, financial inclusion"),
            "reviewer2": ("Graduate School of Economics", "KZ", "0000-0002-2000-0006", "International trade, gravity models, integration"),
            "reviewer3": ("Middle East Technical University", "TR", "0000-0002-2000-0007", "Monetary policy, inflation, emerging markets"),
            "author": ("Centre for Regional Studies", "UZ", "0000-0002-2000-0008", "Regional development, agriculture, water economics"),
        }[key]
        profile.affiliation, profile.country, profile.orcid, profile.expertise = data
        profile.city = "Tashkent"
        profile.academic_degree = "PhD in Economics"
        profile.accepts_review_invitations = True
        profile.save()

    # ------------------------------------------------------------------ board
    def seed_board(self, users: dict[str, User]) -> None:
        """Create the twelve demonstration board members."""
        sections = {s.slug: s for s in Section.objects.all()}
        eic_member = None
        for row in content_seed.BOARD:
            member, _created = EditorialBoardMember.objects.get_or_create(
                full_name_en=row["name"], role=row["role"]
            )
            set_translated(member, "full_name", {code: row["name"] for code in LANGS})
            set_translated(member, "degree", row["degree"])
            set_translated(member, "academic_title", row["title"])
            set_translated(member, "affiliation", row["affiliation"])
            set_translated(member, "expertise", row["expertise"])
            member.country = row["country"]
            member.orcid = row["orcid"]
            member.email = row.get("email", "")
            member.order = row["order"]
            member.is_active = True
            member.is_demo = True
            member.save()
            for slug in row.get("sections", []):
                if slug in sections:
                    member.sections.add(sections[slug])
            if row["role"] == "editor_in_chief":
                eic_member = member

        if eic_member is not None:
            site = SiteSettings.load()
            site.editor_in_chief = eic_member
            site.save()
        self.stdout.write(f"  {len(content_seed.BOARD)} editorial board members (DEMO)")

    # ----------------------------------------------------------------- issues
    def seed_issues(self) -> list[Issue]:
        """Create Volume 1 with issues 1–3 published (January–March 2026)."""
        volume, _created = Volume.objects.get_or_create(number=1, defaults={"year": 2026})
        volume.year = 2026
        set_translated(volume, "title", {"en": "", "uz": "", "ru": ""})
        volume.save()

        issues: list[Issue] = []
        for number, month in ((1, 1), (2, 2), (3, 3)):
            issue, _created = Issue.objects.get_or_create(volume=volume, number=number)
            issue.published_at = dt.date(2026, month, 28)
            issue.is_published = True
            issue.is_current = number == 3
            issue.pages_prefix = ""
            set_translated(
                issue,
                "description",
                {
                    "en": f"Issue {number} of Volume 1 brings together four peer-reviewed articles on the economics of transition, trade and public finance.",
                    "uz": f"1-jildning {number}-soni oʻtish davri iqtisodiyoti, savdo va davlat moliyasi boʻyicha toʻrtta taqrizdan oʻtgan maqolani jamlaydi.",
                    "ru": f"Выпуск {number} тома 1 объединяет четыре рецензированные статьи по экономике переходного периода, торговле и государственным финансам.",
                },
            )
            issue.save()
            issues.append(issue)

        # Issue 4 is created unpublished so the production dashboard has work to do.
        Issue.objects.get_or_create(volume=volume, number=4, defaults={"is_published": False})
        self.stdout.write("  volume 1 with issues 1–3 published and issue 4 in preparation")
        return issues

    # --------------------------------------------------------------- articles
    def seed_articles(self, issues: list[Issue]) -> None:
        """Create the twelve issue articles and two Online First articles."""
        sections = {s.slug: s for s in Section.objects.all()}
        jel_codes = {j.code: j for j in JELCode.objects.all()}
        license_obj = License.default()
        counters: dict[int | None, int] = {}

        for index, row in enumerate(article_seed.ARTICLES, start=1):
            issue = issues[row["issue"]] if row["issue"] is not None else None
            article, _created = Article.objects.get_or_create(
                title_en=row["title"]["en"], defaults={"section": sections[row["section"]]}
            )
            article.section = sections[row["section"]]
            article.license = license_obj
            article.language = "en"
            article.article_type = Article.ArticleType.RESEARCH
            set_translated(article, "title", row["title"])
            set_translated(article, "abstract", row["abstract"])
            set_translated(
                article,
                "funding_statement",
                {
                    "en": "This research received no specific grant from any funding agency in the public, commercial or not-for-profit sectors.",
                    "uz": "Ushbu tadqiqot davlat, tijorat yoki notijorat sektorlaridagi biror moliyalashtirish tashkilotidan maxsus grant olmagan.",
                    "ru": "Исследование не получало специальных грантов от финансирующих организаций государственного, коммерческого или некоммерческого секторов.",
                },
            )
            set_translated(
                article,
                "conflict_of_interest_statement",
                {
                    "en": "The authors declare no conflict of interest.",
                    "uz": "Mualliflar manfaatlar toʻqnashuvi yoʻqligini bildiradi.",
                    "ru": "Авторы заявляют об отсутствии конфликта интересов.",
                },
            )
            set_translated(
                article,
                "data_availability_statement",
                {
                    "en": "The data and replication code are available from the corresponding author on reasonable request.",
                    "uz": "Maʼlumot va takrorlash kodi asosli soʻrov boʻyicha masʼul muallifdan olinishi mumkin.",
                    "ru": "Данные и код воспроизведения доступны у корреспондирующего автора по обоснованному запросу.",
                },
            )
            set_translated(
                article,
                "ai_use_statement",
                {
                    "en": "No generative AI tools were used in the preparation of this article.",
                    "uz": "Ushbu maqolani tayyorlashda generativ sunʼiy intellekt vositalari ishlatilmagan.",
                    "ru": "При подготовке настоящей статьи инструменты генеративного искусственного интеллекта не использовались.",
                },
            )
            set_translated(
                article,
                "copyright_holder",
                {"en": "The Author(s)", "uz": "Muallif(lar)", "ru": "Автор(ы)"},
            )

            received = (issue.published_at if issue else dt.date(2026, 4, 10)) - dt.timedelta(days=150)
            article.received_at = received
            article.revised_at = received + dt.timedelta(days=64)
            article.accepted_at = received + dt.timedelta(days=95)
            if issue is not None:
                article.issue = issue
                article.status = Article.Status.PUBLISHED
                article.published_at = issue.published_at
                article.published_online_at = issue.published_at - dt.timedelta(days=18)
                number = counters.get(issue.pk, 0) + 1
                counters[issue.pk] = number
                article.article_number = number
                start = 1 + (number - 1) * 24
                article.pages_start = str(start)
                article.pages_end = str(start + self.rng.randint(16, 23))
            else:
                article.issue = None
                article.status = Article.Status.ONLINE_FIRST
                article.published_online_at = dt.date(2026, 4, 12)
                article.published_at = None
                article.article_number = None
            article.save()

            article.doi = f"10.00000/arer.2026.{article.pk:04d}"
            article.doi_status = Article.DOIStatus.REGISTERED
            article.save(update_fields=["doi", "doi_status", "updated_at"])

            self._seed_keywords(article, row["keywords"])
            article.jel_codes.set([jel_codes[c] for c in row["jel"] if c in jel_codes])
            self._seed_authors(article, row["authors"])
            self._seed_references(article, index)
            self._seed_galley(article)

        self.stdout.write(f"  {len(article_seed.ARTICLES)} articles with PDF galleys")

    def _seed_keywords(self, article: Article, keywords: dict[str, list[str]]) -> None:
        """Create keyword rows with a value in each language."""
        article.keywords.clear()
        english = keywords["en"]
        for position, name_en in enumerate(english):
            slug = slugify(name_en)[:130]
            keyword, _created = Keyword.objects.get_or_create(slug=slug)
            keyword.name_en = name_en
            for code in ("uz", "ru"):
                values = keywords.get(code, [])
                if position < len(values):
                    setattr(keyword, f"name_{code}", values[position])
            keyword.name = name_en
            keyword.save()
            article.keywords.add(keyword)

    def _seed_authors(self, article: Article, authors: list[dict[str, Any]]) -> None:
        """Create the authorship rows of an article."""
        article.authors.all().delete()
        for order, row in enumerate(authors, start=1):
            author = Author(
                article=article,
                order=order,
                given_name=row["given"],
                family_name=row["family"],
                email=f"{row['family'].lower()}@example.org",
                is_corresponding=row.get("corresponding", False),
                orcid=row["orcid"],
                orcid_verified=True,
                city=row["city"],
                country=row["country"],
                credit_roles=row.get("credit", []),
            )
            set_translated(author, "affiliation", row["affiliation"])
            author.save()

    def _seed_references(self, article: Article, index: int) -> None:
        """Attach 20–35 generated references to an article."""
        article.references.all().delete()
        count = self.rng.randint(21, 34)
        rows = article_seed.build_references(seed_value=1000 + index, count=count)
        Reference.objects.bulk_create(
            [Reference(article=article, order=i, raw_text=text) for i, text in enumerate(rows, 1)]
        )
        for reference in article.references.all():
            reference.save()  # triggers DOI auto-detection

    def _seed_galley(self, article: Article) -> None:
        """Generate and attach a real PDF galley."""
        if article.galleys.filter(is_primary=True).exists():
            return
        payload = build_article_pdf(article)
        galley = Galley(
            article=article,
            label=Galley.Label.PDF,
            language="en",
            mime="application/pdf",
            is_primary=True,
            order=1,
            size=len(payload),
        )
        galley.file.save(f"arer-{article.pk}.pdf", ContentFile(payload), save=False)
        galley.save()

    # ------------------------------------------------------------- statistics
    def seed_statistics(self) -> None:
        """Sprinkle plausible view and download counts over the last 90 days."""
        from apps.metrics.models import DailyArticleStat
        from apps.metrics.services import refresh_article_totals

        today = timezone.now().date()
        articles = list(Article.objects.public())
        DailyArticleStat.objects.filter(article__in=articles).delete()
        rows = []
        for article in articles:
            popularity = self.rng.uniform(0.4, 2.2)
            for offset in range(90):
                date = today - dt.timedelta(days=offset)
                if article.display_date and date < article.display_date:
                    continue
                decay = max(0.25, 1.6 - offset / 90)
                views = max(0, int(self.rng.gauss(6 * popularity * decay, 3)))
                downloads = max(0, int(views * self.rng.uniform(0.2, 0.5)))
                if views == 0 and downloads == 0:
                    continue
                rows.append(
                    DailyArticleStat(
                        article=article, date=date, views=views, downloads=downloads
                    )
                )
        DailyArticleStat.objects.bulk_create(rows, ignore_conflicts=True)
        refresh_article_totals()
        self.stdout.write(f"  usage statistics for {len(articles)} articles over 90 days")

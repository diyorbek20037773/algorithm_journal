"""Shared pytest fixtures for the ARER test suite."""

from __future__ import annotations

import datetime as dt
import os

import pytest
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.test import Client
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Profile, Role, User
from apps.core.models import Page, SiteSettings
from apps.journal.models import (
    Article,
    Author,
    Galley,
    Issue,
    JELCode,
    Keyword,
    License,
    Reference,
    Section,
    Volume,
)
from apps.submissions.models import Submission, SubmissionAuthor, SubmissionFile

# Playwright's synchronous API runs the test body inside a greenlet that owns a
# live asyncio loop.  Django sees the loop, decides it is in an async context
# and refuses ORM access — which breaks the ``django_db`` teardown of the
# browser test, not just the test body.  The suite only ever touches the
# throw-away test database, so the guard is safe to lift here.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

PASSWORD = "Algorithm2026!"


@pytest.fixture
def site_settings(db) -> SiteSettings:
    """The journal settings singleton with realistic identifiers."""
    site = SiteSettings.load()
    site.journal_name_en = "ALGORITHM: Review of Economic Research"
    site.journal_name = site.journal_name_en
    site.journal_subtitle_en = "Open-access research in economics"
    site.short_code = "ARER"
    site.eissn = "3060-1234"
    site.doi_prefix = "10.00000"
    site.publisher_name_en = "Founder organisation (to be confirmed)"
    site.publisher_name = site.publisher_name_en
    site.contact_email = "editor@example.org"
    site.save()
    return site


@pytest.fixture
def license_cc_by(db) -> License:
    """The default CC BY 4.0 licence."""
    return License.objects.create(
        code="CC-BY-4.0",
        name="Creative Commons Attribution 4.0 International",
        url="https://creativecommons.org/licenses/by/4.0/",
        is_default=True,
    )


@pytest.fixture
def section(db) -> Section:
    """A research section."""
    obj = Section.objects.create(slug="finance-banking-investment", order=5, is_research=True)
    obj.name_en = "Finance, Banking & Investment"
    obj.name_uz = "Moliya, bank ishi va investitsiyalar"
    obj.name_ru = "Финансы, банковское дело и инвестиции"
    obj.name = obj.name_en
    obj.save()
    return obj


@pytest.fixture
def jel_codes(db) -> list[JELCode]:
    """Three JEL codes at levels 1 and 3."""
    parent = JELCode.objects.create(
        code="G", level=1, label_en="Financial Economics", label="Financial Economics"
    )
    mid = JELCode.objects.create(
        code="G2",
        level=2,
        parent=parent,
        label_en="Financial Institutions",
        label="Financial Institutions",
    )
    leaf = JELCode.objects.create(code="G21", level=3, parent=mid, label_en="Banks", label="Banks")
    return [parent, mid, leaf]


@pytest.fixture
def groups(db) -> dict[str, Group]:
    """Every role group."""
    return {role: Group.objects.get_or_create(name=role)[0] for role, _ in Role.choices}


def _make_user(email: str, roles: list[str], groups: dict[str, Group], **extra) -> User:
    """Create an active user with the given role groups."""
    user = User.objects.create_user(email=email, password=PASSWORD, **extra)
    user.groups.set([groups[r] for r in roles])
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def author_user(db, groups) -> User:
    """A registered author."""
    return _make_user(
        "author@example.org", [Role.AUTHOR], groups, first_name="Ann", last_name="Author"
    )


@pytest.fixture
def editor_user(db, groups, section) -> User:
    """A section editor with a confirmed TOTP device."""
    user = _make_user(
        "editor@example.org", [Role.SECTION_EDITOR], groups, first_name="Ed", last_name="Editor"
    )
    section.editors.add(user)
    TOTPDevice.objects.create(user=user, name="test", confirmed=True)
    return user


@pytest.fixture
def eic_user(db, groups) -> User:
    """The editor-in-chief with a confirmed TOTP device."""
    user = _make_user(
        "eic@example.org", [Role.EDITOR_IN_CHIEF], groups, first_name="Eva", last_name="Chief"
    )
    TOTPDevice.objects.create(user=user, name="test", confirmed=True)
    return user


@pytest.fixture
def production_user(db, groups) -> User:
    """A production editor with a confirmed TOTP device."""
    user = _make_user(
        "production@example.org",
        [Role.PRODUCTION_EDITOR],
        groups,
        first_name="Pat",
        last_name="Press",
    )
    TOTPDevice.objects.create(user=user, name="test", confirmed=True)
    return user


@pytest.fixture
def reviewers(db, groups) -> list[User]:
    """Three reviewers."""
    out = []
    for index in range(1, 4):
        user = _make_user(
            f"reviewer{index}@example.org",
            [Role.REVIEWER],
            groups,
            first_name=f"Rev{index}",
            last_name="Viewer",
        )
        user.is_reviewer = True
        user.save()
        out.append(user)
    return out


@pytest.fixture
def volume(db) -> Volume:
    """Volume 1 (2026)."""
    return Volume.objects.create(number=1, year=2026)


@pytest.fixture
def issue(db, volume) -> Issue:
    """A published issue."""
    return Issue.objects.create(
        volume=volume,
        number=1,
        published_at=dt.date(2026, 1, 28),
        is_published=True,
        is_current=True,
    )


@pytest.fixture
def article(db, issue, section, license_cc_by, jel_codes, site_settings) -> Article:
    """A fully populated published article with authors, keywords and a galley."""
    obj = Article(
        issue=issue,
        section=section,
        license=license_cc_by,
        status=Article.Status.PUBLISHED,
        language="en",
        received_at=dt.date(2025, 9, 1),
        accepted_at=dt.date(2025, 12, 1),
        published_at=dt.date(2026, 1, 28),
        published_online_at=dt.date(2026, 1, 10),
        pages_start="1",
        pages_end="24",
        article_number=1,
        doi="10.00000/arer.2026.0001",
        doi_status=Article.DOIStatus.REGISTERED,
    )
    obj.title_en = "Bank Competition and the Cost of Credit for Small Firms"
    obj.title_uz = "Bank raqobati va kichik korxonalar uchun kredit narxi"
    obj.title_ru = "Банковская конкуренция и стоимость кредита для малых фирм"
    obj.title_uz_cyrl = "Банк рақобати ва кичик корхоналар учун кредит нархи"
    obj.title = obj.title_en
    obj.abstract_en = "We estimate the effect of local bank market concentration on the price of credit for small firms using loan-level data from eleven transition economies."
    obj.abstract_uz = "Oʻn bitta oʻtish davri iqtisodiyotidan olingan kredit maʼlumotlari asosida mahalliy bank bozori konsentratsiyasining kichik korxonalar uchun kredit narxiga taʼsirini baholaymiz."
    obj.abstract_ru = "Мы оцениваем влияние локальной концентрации банковского рынка на стоимость кредита для малых фирм по данным о кредитах из одиннадцати переходных экономик."
    obj.abstract_uz_cyrl = (
        "Ўн битта ўтиш даври иқтисодиётидан олинган кредит маълумотлари асосида таҳлил."
    )
    obj.abstract = obj.abstract_en
    obj.conflict_of_interest_statement = "The authors declare no conflict of interest."
    obj.ai_use_statement = "No generative AI tools were used in the preparation of this article."
    obj.save()

    Author.objects.create(
        article=obj,
        order=1,
        given_name="Aziz",
        family_name="Karimov",
        email="karimov@example.org",
        is_corresponding=True,
        orcid="0000-0002-1000-0031",
        orcid_verified=True,
        affiliation_en="Banking and Finance Academy",
        affiliation="Banking and Finance Academy",
        city="Tashkent",
        country="UZ",
        credit_roles=["Conceptualization", "Formal analysis"],
    )
    Author.objects.create(
        article=obj,
        order=2,
        given_name="Elena",
        family_name="Sokolova",
        email="sokolova@example.org",
        orcid="0000-0002-1000-0032",
        affiliation_en="Graduate School of Economics",
        affiliation="Graduate School of Economics",
        city="Almaty",
        country="KZ",
    )

    for index, name in enumerate(
        [
            "bank competition",
            "credit spreads",
            "small business lending",
            "collateral",
            "transition economies",
        ]
    ):
        keyword = Keyword.objects.create(slug=f"kw-{index}", name_en=name, name=name)
        obj.keywords.add(keyword)

    obj.jel_codes.set(jel_codes[2:])

    for order in range(1, 12):
        Reference.objects.create(
            article=obj,
            order=order,
            raw_text=(
                f"Author, A. ({2010 + order}). A study of credit markets. "
                f"*Journal of Banking & Finance*, {order}(2), 1–20. "
                f"https://doi.org/10.1016/example.{2010 + order}.{order:04d}"
            ),
        )

    galley = Galley(
        article=obj,
        label=Galley.Label.PDF,
        mime="application/pdf",
        is_primary=True,
        order=1,
    )
    payload = b"%PDF-1.4\n% test galley\n"
    galley.file.save("test.pdf", ContentFile(payload), save=False)
    galley.size = len(payload)
    galley.save()
    return obj


@pytest.fixture
def online_first_article(db, section, license_cc_by, site_settings) -> Article:
    """An article published ahead of an issue."""
    obj = Article(
        section=section,
        license=license_cc_by,
        status=Article.Status.ONLINE_FIRST,
        published_online_at=dt.date(2026, 4, 12),
        doi="10.00000/arer.2026.0002",
        doi_status=Article.DOIStatus.REGISTERED,
    )
    obj.title_en = "Digital Credit and Household Debt"
    obj.title = obj.title_en
    obj.abstract_en = "We study the welfare effects of mobile instalment credit."
    obj.abstract = obj.abstract_en
    obj.save()
    Author.objects.create(
        article=obj,
        order=1,
        given_name="Dilnoza",
        family_name="Yusupova",
        email="yusupova@example.org",
        is_corresponding=True,
        affiliation="Institute of Economic Research",
        city="Tashkent",
        country="UZ",
    )
    return obj


@pytest.fixture
def submission(db, author_user, section, jel_codes) -> Submission:
    """A draft submission ready to be moved through the workflow."""
    obj = Submission(
        submitter=author_user,
        section=section,
        status=Submission._meta.get_field("status").default,
        language="en",
        word_count=6200,
        anonymised_file_ok=True,
        author_declarations={
            "original": True,
            "not_under_consideration": True,
            "guidelines": True,
            "anonymised": True,
            "ethics": True,
            "license": True,
        },
        ai_use_statement="No generative AI tools were used.",
    )
    obj.cover_letter = (
        "Dear Editors, this cover letter mentions Qurbonniyozov and must never be "
        "shown to a reviewer."
    )
    obj.title_en = "Interbank Liquidity and Policy Rate Transmission"
    obj.title = obj.title_en
    obj.abstract_en = (
        "We study how interbank liquidity conditions shape the transmission of policy rates."
    )
    obj.abstract = obj.abstract_en
    obj.keywords_text = "liquidity, monetary policy, banks, transmission, money market"
    obj.metadata = {
        "title": {
            "en": obj.title_en,
            "uz": "Banklararo likvidlik",
            "ru": "Межбанковская ликвидность",
        },
        "abstract": {"en": obj.abstract_en, "uz": "Annotatsiya", "ru": "Аннотация"},
        "keywords": {
            "en": ["liquidity", "monetary policy", "banks", "transmission", "money market"],
            "uz": ["likvidlik", "pul siyosati", "banklar", "uzatish", "pul bozori"],
            "ru": ["ликвидность", "денежная политика", "банки", "трансмиссия", "денежный рынок"],
        },
        "references": [
            "Author, A. (2020). Liquidity and policy. *Journal of Banking & Finance*, 1(1), 1–10."
        ],
    }
    obj.save()
    obj.jel_codes.set(jel_codes[2:])

    # Deliberately distinctive values: the non-leakage tests assert that none of
    # them ever appears in a reviewer-facing page, so they must not collide with
    # ordinary interface wording such as "Author" or "Institute".
    SubmissionAuthor.objects.create(
        submission=obj,
        order=1,
        given_name="Xolmurod",
        family_name="Qurbonniyozov",
        email="xq-secret-address@example.org",
        is_corresponding=True,
        orcid="0000-0003-7777-8888",
        affiliation="Zarafshan Institute of Applied Economics",
        city="Navoiy",
        country="UZ",
    )
    for kind in (SubmissionFile.Kind.MANUSCRIPT_ANON, SubmissionFile.Kind.TITLE_PAGE):
        record = SubmissionFile(submission=obj, kind=kind, uploaded_by=author_user, version=1)
        record.file.save(f"{kind}.pdf", ContentFile(b"%PDF-1.4 test"), save=False)
        record.save()
    return obj


@pytest.fixture
def about_pages(db) -> list[Page]:
    """The CMS pages the public navigation links to."""
    pages = []
    definitions = [
        ("about", "about", "About the Journal"),
        ("aims-and-scope", "about", "Aims & Scope"),
        ("peer-review", "about", "Peer Review Process"),
        ("publication-ethics", "about", "Publication Ethics"),
        ("open-access", "about", "Open Access"),
        ("fees", "about", "Article Processing Charges"),
        ("archiving", "about", "Archiving Policy"),
        ("indexing", "about", "Indexing"),
        ("ai-policy", "about", "AI Policy"),
        ("privacy", "about", "Privacy Policy"),
        ("contact", "about", "Contact"),
        ("for-authors", "authors", "For Authors"),
        ("author-guidelines", "authors", "Author Guidelines"),
        ("submission-checklist", "authors", "Checklist"),
        ("manuscript-template", "authors", "Templates"),
        ("reviewer-guidelines", "reviewers", "Reviewer Guidelines"),
    ]
    for order, (slug, group, title) in enumerate(definitions, start=1):
        page = Page(slug=slug, menu_group=group, menu_order=order, is_published=True)
        page.title_en = title
        page.title = title
        page.body_en = f"# {title}\n\nDemonstration content for the {title} page."
        page.body = page.body_en
        page.save()
        pages.append(page)
    return pages


@pytest.fixture
def client_anon() -> Client:
    """An unauthenticated test client."""
    return Client()


@pytest.fixture
def client_author(author_user) -> Client:
    """A client signed in as the author."""
    client = Client()
    client.force_login(author_user)
    return client


@pytest.fixture
def client_editor(editor_user) -> Client:
    """A client signed in as the section editor."""
    client = Client()
    client.force_login(editor_user)
    return client


@pytest.fixture
def client_eic(eic_user) -> Client:
    """A client signed in as the editor-in-chief."""
    client = Client()
    client.force_login(eic_user)
    return client

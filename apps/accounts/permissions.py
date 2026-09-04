"""Permission mixins and helpers for role-gated views."""

from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from apps.accounts.models import Role


class RoleRequiredMixin(AccessMixin):
    """Class-based-view mixin requiring membership in one of ``required_roles``."""

    required_roles: Iterable[str] = ()

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reject anonymous users and users lacking every required role."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_roles and not request.user.has_role(*self.required_roles):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class EditorRequiredMixin(RoleRequiredMixin):
    """Section editors, the editor-in-chief and administrators."""

    required_roles = (Role.SECTION_EDITOR, Role.EDITOR_IN_CHIEF, Role.ADMIN)


class EICRequiredMixin(RoleRequiredMixin):
    """Editor-in-chief and administrators only."""

    required_roles = (Role.EDITOR_IN_CHIEF, Role.ADMIN)


class ProductionRequiredMixin(RoleRequiredMixin):
    """Production editors, the editor-in-chief and administrators."""

    required_roles = (Role.PRODUCTION_EDITOR, Role.EDITOR_IN_CHIEF, Role.ADMIN)


class ReviewerRequiredMixin(RoleRequiredMixin):
    """Users flagged as reviewers."""

    required_roles = (Role.REVIEWER,)


def user_can_edit_submission(user, submission) -> bool:
    """True when ``user`` may act on ``submission`` as an editor.

    Section editors are limited to their own sections; the EIC and
    administrators may act on everything.
    """
    if not user.is_authenticated:
        return False
    if user.has_role(Role.EDITOR_IN_CHIEF, Role.ADMIN) or user.is_superuser:
        return True
    if not user.has_role(Role.SECTION_EDITOR):
        return False
    if submission.assigned_editor_id == user.pk:
        return True
    return submission.section_id in set(
        user.edited_sections.values_list("id", flat=True)  # type: ignore[attr-defined]
    )


def user_can_view_submission(user, submission) -> bool:
    """True when ``user`` may open the submission detail page."""
    if not user.is_authenticated:
        return False
    if submission.submitter_id == user.pk:
        return True
    if user_can_edit_submission(user, submission):
        return True
    return submission.rounds.filter(assignments__reviewer=user).exists()

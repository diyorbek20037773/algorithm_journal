"""Account signal handlers: profile creation and authentication auditing."""

from __future__ import annotations

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Profile, User
from apps.core.models import AuditLog
from apps.core.services import log_action


@receiver(post_save, sender=User, dispatch_uid="accounts_create_profile")
def create_profile(sender, instance: User, created: bool, **kwargs) -> None:
    """Guarantee that every user owns exactly one profile row."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(user_logged_in, dispatch_uid="accounts_audit_login")
def audit_login(sender, request, user, **kwargs) -> None:
    """Record successful sign-ins."""
    log_action(AuditLog.Action.LOGIN, actor=user, target=str(user), request=request)


@receiver(user_logged_out, dispatch_uid="accounts_audit_logout")
def audit_logout(sender, request, user, **kwargs) -> None:
    """Record sign-outs."""
    if user is not None:
        log_action(AuditLog.Action.LOGOUT, actor=user, target=str(user), request=request)


@receiver(user_login_failed, dispatch_uid="accounts_audit_login_failed")
def audit_login_failed(sender, credentials, request=None, **kwargs) -> None:
    """Record failed sign-in attempts without storing the password."""
    log_action(
        AuditLog.Action.LOGIN_FAILED,
        target=str(credentials.get("username") or credentials.get("email") or "")[:255],
        request=request,
    )

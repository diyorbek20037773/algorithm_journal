"""Django project configuration package for MEZON: Review of Economic Research."""

from .celery import app as celery_app

__all__ = ("celery_app",)

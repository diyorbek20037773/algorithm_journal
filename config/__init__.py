"""Django project configuration package for ALGORITHM: Review of Economic Research."""

from .celery import app as celery_app

__all__ = ("celery_app",)

"""Fill ``Article.search_vector`` for rows that existed before the column did.

Imports the indexer rather than re-implementing it: the document it builds is
the one production maintains, so the two cannot drift. If the indexer's field
list changes in a way this historical schema lacks, ``rebuild_search_index``
recomputes everything anyway.
"""

from __future__ import annotations

from django.db import migrations


def forwards(apps, schema_editor):
    from apps.search.indexing import rebuild_all

    rebuild_all()


def backwards(apps, schema_editor):
    Article = apps.get_model("journal", "Article")
    Article.objects.update(search_vector=None)


class Migration(migrations.Migration):
    dependencies = [("journal", "0004_article_search_vector")]

    operations = [migrations.RunPython(forwards, backwards)]

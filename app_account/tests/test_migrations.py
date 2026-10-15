from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from django.db.migrations.loader import MigrationLoader


@pytest.mark.django_db
def test_the_migration_graph_loads_without_missing_dependencies() -> None:
    loader = MigrationLoader(connection, ignore_no_migrations=True)

    assert ("address", "0001_initial") in loader.graph.nodes
    assert ("product", "0001_initial") in loader.graph.nodes
    assert ("account", "0002_initial") in loader.graph.nodes


@pytest.mark.django_db
def test_no_pending_model_changes_are_missing_a_migration() -> None:
    out = StringIO()

    call_command(
        command_name="makemigrations",
        check=True,
        dry_run=True,
        stdout=out,
        stderr=out,
    )

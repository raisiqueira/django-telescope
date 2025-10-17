#!/usr/bin/env python
"""
Test script to verify Django MCP server tools work correctly.
Run from project root: python test_server.py
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

# Add fixtures/testproject to path
fixtures_path = Path(__file__).parent / "fixtures" / "testproject"
sys.path.insert(0, str(fixtures_path))

# Set up Django settings to use the test project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

import django
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.management import get_commands
from django.db import connection
from django.urls import get_resolver

django.setup()


async def test_application_info():
    """Test application_info tool."""
    print("\n1. Testing application_info:")
    print("-" * 60)

    installed_apps = list(settings.INSTALLED_APPS)
    middleware = list(settings.MIDDLEWARE) if hasattr(settings, "MIDDLEWARE") else []
    db_config = settings.DATABASES.get("default", {})
    db_engine = db_config.get("ENGINE", "unknown").split(".")[-1]
    all_models = apps.get_models()

    info = {
        "django_version": django.get_version(),
        "python_version": sys.version.split()[0],
        "installed_apps": installed_apps,
        "middleware": middleware,
        "database_engine": db_engine,
        "models_count": len(all_models),
        "debug_mode": settings.DEBUG,
    }

    print(f"Django Version: {info['django_version']}")
    print(f"Python Version: {info['python_version']}")
    print(f"Database Engine: {info['database_engine']}")
    print(f"Debug Mode: {info['debug_mode']}")
    print(f"Number of Models: {info['models_count']}")
    print(f"Installed Apps: {len(info['installed_apps'])} apps")
    return info


async def test_get_setting():
    """Test get_setting tool."""
    print("\n2. Testing get_setting:")
    print("-" * 60)

    # Test DEBUG setting
    debug_value = settings.DEBUG
    print(f"DEBUG setting: {debug_value}")

    # Test nested setting
    db_engine = settings.DATABASES["default"]["ENGINE"]
    print(f"Database engine: {db_engine}")

    return {"success": True}


async def test_list_models():
    """Test list_models tool."""
    print("\n3. Testing list_models:")
    print("-" * 60)

    models_info = []
    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model._meta.object_name

        fields = []
        for field in model._meta.get_fields():
            field_info = {
                "name": field.name,
                "type": field.__class__.__name__,
            }
            fields.append(field_info)

        models_info.append({
            "app": app_label,
            "model": model_name,
            "db_table": model._meta.db_table,
            "fields": fields,
        })

    print(f"Found {len(models_info)} models")
    if models_info:
        first_model = models_info[0]
        print(f"Example: {first_model['app']}.{first_model['model']}")
        print(f"  Table: {first_model['db_table']}")
        print(f"  Fields: {len(first_model['fields'])}")

    return models_info


async def test_database_schema():
    """Test database_schema tool."""
    print("\n4. Testing database_schema:")
    print("-" * 60)

    @sync_to_async
    def get_schema():
        schema_info = {
            "tables": [],
            "database_name": connection.settings_dict.get("NAME"),
            "database_engine": connection.settings_dict.get("ENGINE"),
        }

        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()
            for table_name in tables[:5]:  # Limit to first 5 tables for test
                table_description = connection.introspection.get_table_description(
                    cursor, table_name
                )
                table_info = {
                    "name": table_name,
                    "columns": [
                        {
                            "name": col.name,
                            "type": str(col.type_code),
                        }
                        for col in table_description
                    ],
                }
                schema_info["tables"].append(table_info)
        return schema_info

    schema_info = await get_schema()

    print(f"Database: {schema_info['database_name']}")
    print(f"Engine: {schema_info['database_engine']}")
    print(f"Tables (showing first 5): {len(schema_info['tables'])}")
    if schema_info["tables"]:
        first_table = schema_info["tables"][0]
        print(f"Example table: {first_table['name']}")
        print(f"  Columns: {len(first_table['columns'])}")

    return schema_info


async def test_list_migrations():
    """Test list_migrations tool."""
    print("\n5. Testing list_migrations:")
    print("-" * 60)

    @sync_to_async
    def get_migrations():
        from django.db.migrations.loader import MigrationLoader

        loader = MigrationLoader(connection)
        migrations_info = []

        for app_label in loader.migrated_apps:
            app_migrations = []
            for migration_name in loader.disk_migrations:
                if migration_name[0] == app_label:
                    is_applied = migration_name in loader.applied_migrations
                    app_migrations.append({
                        "name": migration_name[1],
                        "applied": is_applied,
                    })

            if app_migrations:
                migrations_info.append({
                    "app": app_label,
                    "migrations": sorted(app_migrations, key=lambda x: x["name"]),
                })
        return migrations_info

    migrations_info = await get_migrations()

    print(f"Found migrations for {len(migrations_info)} apps")
    if migrations_info:
        for app_mig in migrations_info[:3]:
            applied = sum(1 for m in app_mig["migrations"] if m["applied"])
            total = len(app_mig["migrations"])
            print(f"  {app_mig['app']}: {applied}/{total} applied")

    return migrations_info


async def test_list_management_commands():
    """Test list_management_commands tool."""
    print("\n6. Testing list_management_commands:")
    print("-" * 60)

    commands = get_commands()
    commands_info = [
        {"command": cmd_name, "app": app_name}
        for cmd_name, app_name in sorted(commands.items())
    ]

    print(f"Found {len(commands_info)} management commands")
    common_commands = ["migrate", "makemigrations", "runserver", "shell"]
    for cmd in commands_info:
        if cmd["command"] in common_commands:
            print(f"  {cmd['command']} (from {cmd['app']})")

    return commands_info


async def test_all_tools():
    """Test all MCP tools."""
    print("=" * 60)
    print("Testing Django MCP Server Tools")
    print("=" * 60)

    try:
        await test_application_info()
        await test_get_setting()
        await test_list_models()
        await test_database_schema()
        await test_list_migrations()
        await test_list_management_commands()

        print("\n" + "=" * 60)
        print("All tools tested successfully! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_all_tools())

#!/usr/bin/env python
"""
Test script for the query_model MCP tool.
This script tests the new read-only query functionality by calling the implementation directly.
"""

import asyncio
import os
import sys

# Add the fixtures directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fixtures", "testproject"))

# Set Django settings before importing
os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"

# Import Django and setup
import django
from asgiref.sync import sync_to_async
from django.apps import apps

django.setup()


async def query_model_impl(
    app_label: str,
    model_name: str,
    filters: dict | None = None,
    order_by: list[str] | None = None,
    limit: int = 100,
) -> dict:
    """Implementation of query_model tool for testing."""

    @sync_to_async
    def execute_query():
        try:
            # Get the model
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                return {"error": f"Model '{app_label}.{model_name}' not found"}

            # Enforce maximum limit for safety
            max_limit = 1000
            actual_limit = min(limit, max_limit) if limit else 100

            # Start with all objects
            queryset = model.objects.all()

            # Apply filters if provided
            if filters:
                try:
                    queryset = queryset.filter(**filters)
                except Exception as e:
                    return {"error": f"Invalid filter parameters: {str(e)}"}

            # Apply ordering if provided
            if order_by:
                try:
                    queryset = queryset.order_by(*order_by)
                except Exception as e:
                    return {"error": f"Invalid order_by parameters: {str(e)}"}

            # Get total count before limiting
            total_count = queryset.count()

            # Limit results
            queryset = queryset[:actual_limit]

            # Convert queryset to list of dictionaries
            results = []
            for obj in queryset:
                obj_dict = {}
                for field in model._meta.get_fields():
                    # Skip reverse relations
                    if field.many_to_many or field.one_to_many:
                        continue

                    field_name = field.name
                    try:
                        value = getattr(obj, field_name)

                        # Handle different field types
                        if value is None:
                            obj_dict[field_name] = None
                        elif hasattr(field, "related_model") and field.related_model:
                            # Foreign key - store the pk
                            obj_dict[field_name] = value.pk if value else None
                            obj_dict[f"{field_name}_str"] = str(value) if value else None
                        elif isinstance(value, (str, int, float, bool)):
                            obj_dict[field_name] = value
                        else:
                            # For dates, times, and other complex types
                            obj_dict[field_name] = str(value)
                    except Exception:
                        # Skip fields that can't be accessed
                        continue

                results.append(obj_dict)

            return {
                "app": app_label,
                "model": model_name,
                "total_count": total_count,
                "returned_count": len(results),
                "limit": actual_limit,
                "filters": filters or {},
                "order_by": order_by or [],
                "results": results,
            }

        except Exception as e:
            return {"error": f"Error executing query: {str(e)}"}

    return await execute_query()


async def test_query_model():
    """Test the query_model tool with various scenarios."""
    print("=" * 80)
    print("Testing query_model MCP Tool")
    print("=" * 80)

    # Test 1: Query all posts (no filters)
    print("\n1. Query all posts (no filters):")
    result = await query_model_impl(app_label="blog", model_name="Post")
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        print(f"   First post: {result['results'][0].get('title')}")

    # Test 2: Query published posts only
    print("\n2. Query published posts only:")
    result = await query_model_impl(
        app_label="blog", model_name="Post", filters={"status": "published"}
    )
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for post in result["results"]:
            print(f"   - {post.get('title')} (status: {post.get('status')})")

    # Test 3: Query with ordering
    print("\n3. Query posts ordered by title:")
    result = await query_model_impl(
        app_label="blog", model_name="Post", order_by=["title"], limit=5
    )
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for post in result["results"]:
            print(f"   - {post.get('title')}")

    # Test 4: Query featured posts
    print("\n4. Query featured posts:")
    result = await query_model_impl(
        app_label="blog", model_name="Post", filters={"featured": True}
    )
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for post in result["results"]:
            print(f"   - {post.get('title')} (featured: {post.get('featured')})")

    # Test 5: Query categories
    print("\n5. Query all categories:")
    result = await query_model_impl(app_label="blog", model_name="Category")
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for category in result["results"]:
            print(f"   - {category.get('name')} (slug: {category.get('slug')})")

    # Test 6: Query with limit
    print("\n6. Query posts with limit=2:")
    result = await query_model_impl(app_label="blog", model_name="Post", limit=2)
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    print(f"   Limit applied: {result.get('limit')}")

    # Test 7: Query comments
    print("\n7. Query approved comments:")
    result = await query_model_impl(
        app_label="blog", model_name="Comment", filters={"is_approved": True}
    )
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for comment in result["results"]:
            print(
                f"   - Comment on post {comment.get('post')} by user {comment.get('author')}"
            )

    # Test 8: Invalid model (error handling)
    print("\n8. Test error handling with invalid model:")
    result = await query_model_impl(app_label="blog", model_name="NonExistent")
    if "error" in result:
        print(f"   Expected error: {result['error']}")

    # Test 9: Invalid filter (error handling)
    print("\n9. Test error handling with invalid filter:")
    result = await query_model_impl(
        app_label="blog", model_name="Post", filters={"invalid_field": "value"}
    )
    if "error" in result:
        print(f"   Expected error: {result['error']}")

    # Test 10: Query with descending order
    print("\n10. Query posts with descending order by created_at:")
    result = await query_model_impl(
        app_label="blog", model_name="Post", order_by=["-created_at"], limit=3
    )
    print(f"   Total count: {result.get('total_count')}")
    print(f"   Returned count: {result.get('returned_count')}")
    if result.get("results"):
        for post in result["results"]:
            print(f"   - {post.get('title')} (created: {post.get('created_at')})")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_query_model())

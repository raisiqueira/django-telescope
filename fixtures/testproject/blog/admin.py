"""
Admin configuration for blog app.
"""

from django.contrib import admin

from .models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "status", "published_at", "view_count"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ["title"]}
    date_hierarchy = "published_at"
    raw_id_fields = ["author"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "created_at", "is_approved"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["content", "author__username"]
    raw_id_fields = ["post", "author"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]

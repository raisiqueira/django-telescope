"""
Views for blog app.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    """Display list of published posts."""
    posts = Post.objects.filter(status="published").select_related("author", "category")
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, pk):
    """Display a single post."""
    post = get_object_or_404(
        Post.objects.select_related("author", "category").prefetch_related("tags"),
        pk=pk,
        status="published",
    )
    # Increment view count
    post.view_count += 1
    post.save(update_fields=["view_count"])
    return render(request, "blog/post_detail.html", {"post": post})


def api_post_list(request):
    """API endpoint to list posts."""
    posts = Post.objects.filter(status="published").values(
        "id", "title", "slug", "excerpt", "published_at"
    )
    return JsonResponse({"posts": list(posts)})

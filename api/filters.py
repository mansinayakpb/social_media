from django_filters import rest_framework as filters

from .models import Comment, Post


class PostFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="created_at", lookup_expr="exact")
    category = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Post
        fields = ["date", "category"]


class CommentFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="created_at", lookup_expr="exact")

    class Meta:
        model = Comment
        fields = ["date"]

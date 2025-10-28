import django_filters

from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from blog.models import BlogPost

class BlogPostFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_by_keyword', label='Keyword')
    recent = django_filters.BooleanFilter(method='filter_recent', label='Recent')

    class Meta:
        model = BlogPost
        fields = ['category', 'title', 'keyword', 'recent']

    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(text__icontains=value)
        )

    def filter_recent(self, queryset, name, value):
        if value:
            last_week = timezone.now() - timedelta(days=5)
            return queryset.filter(created_at__gte=last_week)
        return queryset

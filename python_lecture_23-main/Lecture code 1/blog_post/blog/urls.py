from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog.views import (
    BlogPostListViewSet,
    BlogPostDetailViewSet,
    BlogPostCreateViewSet,
    BlogPostUpdateViewSet,
    BlogPostDeleteViewSet,
    BlogPostViewSet,
    AuthorViewSet
)


router = DefaultRouter()
router.register(r'blog_posts', BlogPostListViewSet, basename='blogpost-list')
router.register(r'blog_post_detail', BlogPostDetailViewSet, basename='blogpost-detail')
router.register(r'blog_post_update', BlogPostUpdateViewSet, basename='blogpost-update')
router.register(r'blog_post_delete', BlogPostDeleteViewSet, basename='blogpost-delete')
router.register(r'blog_post_create', BlogPostCreateViewSet, basename='blogpost-create')
router.register(r'blog_post', BlogPostViewSet, basename='blogpost')
router.register(r'author', AuthorViewSet, basename='author')

urlpatterns = [
    path('', include(router.urls)),
]

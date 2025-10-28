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
router.register(r'blog_posts', BlogPostListViewSet, basename='blog_posts')
router.register(r'blog_post', BlogPostDetailViewSet, basename='blog_post')
router.register(r'blog_post_create', BlogPostCreateViewSet, basename='blog_post_create')
router.register(r'blog_post_update', BlogPostUpdateViewSet, basename='blog_post_update')
router.register(r'blog_post_delete', BlogPostDeleteViewSet, basename='blog_post_delete')
router.register(r'blogpost', BlogPostViewSet, basename='blogpost')
router.register(r'author', AuthorViewSet, basename='author')


urlpatterns = [
    path('', include(router.urls) )
]

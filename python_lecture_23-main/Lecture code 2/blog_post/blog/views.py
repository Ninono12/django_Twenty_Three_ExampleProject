from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from blog.filtersets import BlogPostFilter
from blog.models import BlogPost, Author
from blog.pagination import BlogPostPagination
from blog.permissions import ReadOnlyOrAdmin, ReadOnlyOrIsOwnerOrAdmin
from blog.serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    AuthorSerializer,
    BlogPostReorderSerializer,
    BlogPostSendEmailSerializer,
    BlogPostCoverSerializer
)
from blog.tasks import (
    delete_inactive_blog_posts,
    reorder_blog_posts,
    send_blog_post_to_email,
    create_blog_post_cover
)

class BlogPostListViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostListSerializer
    pagination_class = BlogPostPagination
    filterset_class = BlogPostFilter
    permission_classes = [ReadOnlyOrAdmin]


class BlogPostDetailViewSet(mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostDetailSerializer


class BlogPostUpdateViewSet(mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostCreateUpdateSerializer


class BlogPostCreateViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostCreateUpdateSerializer


class  BlogPostDeleteViewSet(mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostListSerializer


class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    filterset_class = BlogPostFilter
    # permission_classes = [IsAuthenticated, ReadOnlyOrIsOwnerOrAdmin]

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list' or self.action == 'archived_posts':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, ReadOnlyOrIsOwnerOrAdmin]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        elif self.action == 'create' or self.action == 'update':
            return BlogPostCreateUpdateSerializer
        elif self.action == 'publish':
            return  BlogPostListSerializer
        elif self.action == 'reorder_blog_posts':
            return BlogPostReorderSerializer
        elif self.action == 'send_blog_post_to_email':
            return BlogPostSendEmailSerializer
        elif self.action == 'create_blog_post_cover':
            return BlogPostCoverSerializer
        else:
            return BlogPostListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "total_products": queryset.count(),
                "paginated_results": serializer.data
            })
        # If pagination is not used
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "total_products": queryset.count(),
            "paginated_results": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])  # for detail route
    def publish(self, request, pk=None):
        with transaction.atomic():
            obj = self.get_object()
            obj.published = True
            obj.save(update_fields=['published'])
        return Response({'status': 'published'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])  # for detail route
    def archive(self, request, pk=None):
        with transaction.atomic():
            obj = self.get_object()
            obj.archived = True
            obj.save(update_fields=['archived'])
        return Response({'status': 'archived'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def archived_posts(self, request):
        archived_posts = BlogPost.objects.filter(archived=True)
        serializer = self.get_serializer(archived_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def published_posts(self, request):
        published_posts = BlogPost.objects.filter(published=True)
        serializer = self.get_serializer(published_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def delete_inactive_blog_posts(self, request):
        delete_inactive_blog_posts.delay()
        return Response({'Process started successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reorder_blog_posts(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reorder_blog_posts.delay(**serializer.validated_data)
        return Response({'Process started successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def send_blog_post_to_email(self, request, pk=None):
        blop_post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_blog_post_to_email.delay(email=serializer.validated_data['email'], blog_post_id=blop_post.id)
        return Response({'Process started successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def create_blog_post_cover(self, request, pk=None):
        blop_post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data.get('image')
        file_path = default_storage.save(f"blog_post_covers/{image.name}", ContentFile(image.read()))

        create_blog_post_cover.delay(image_url=file_path, blog_post_id=blop_post.id)
        return Response({'Process started successfully'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        # code
        return self.update(request, *args, **kwargs)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            kwargs['fields'] = ('first_name', 'last_name')
        elif self.action == 'update':
            kwargs['fields'] = ('first_name', 'last_name', 'email')
        return super().get_serializer(*args, **kwargs)

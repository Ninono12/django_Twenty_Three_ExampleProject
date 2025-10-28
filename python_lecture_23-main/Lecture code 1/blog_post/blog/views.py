from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from blog.filter_set import BlogPostFilter
from blog.tasks import delete_blog_post, reorder_blog_post, add_banner_image, send_blog_post_to_email
from blog.models import BlogPost, Author
from blog.pagination import BlogPostPagination, BlogPostCursorPagination
from blog.permissions import ReadOnlyOrAdminOrOwner
from blog.serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    AuthorSerializer,
    BlogPostNotPublishedListSerializer,
    ReorderBlogPostSerializer,
    BlogPostBannerSerializer,
    SendBlogPostEmailSerializer
)


class BlogPostListViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostListSerializer
    pagination_class = BlogPostCursorPagination

    @action(detail=True, methods=['post', 'put', 'patch'])
    def archive(self, request, pk=None):
        obj = self.get_object()
        obj.archived = True
        obj.save(update_fields=['archived'])
        return Response({'status': 'archived'}, status=status.HTTP_200_OK)


class BlogPostCreateViewSet(mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class BlogPostDetailViewSet(mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostDetailSerializer


class BlogPostUpdateViewSet(mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class BlogPostDeleteViewSet(mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    serializer_class = BlogPostListSerializer
    permission_classes = [IsAuthenticated]


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.filter(deleted=False)
    pagination_class = BlogPostPagination
    filterset_class = BlogPostFilter

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, ReadOnlyOrAdminOrOwner]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return BlogPostCreateUpdateSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        elif self.action == 'not_published':
            return BlogPostNotPublishedListSerializer
        elif self.action == 'reorder_blog_post':
            return ReorderBlogPostSerializer
        elif self.action == 'add_banner_image':
            return BlogPostBannerSerializer
        elif self.action == 'send_blog_post_to_email':
            return SendBlogPostEmailSerializer
        return BlogPostListSerializer

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        res.data = {
            "count": self.get_queryset().count(),
            "deleted_count": BlogPost.objects.filter(deleted=True).count(),
            "results": res.data,
        }
        return res

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

    @action(detail=True, methods=['post', 'put', 'patch'])  # for collection route
    def archive(self, request, pk=None):
        with transaction.atomic():
            obj = self.get_object()
            obj.archived = True
            obj.save(update_fields=['archived'])
        return Response({'status': 'archived'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'post'])
    def not_published(self, request):
        blog_posts = BlogPost.objects.filter(published=False)
        serializer = self.get_serializer(blog_posts, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        # code here
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def delete_blog_post(self, request):
        delete_blog_post.delay()
        return Response(data={'proces successfully started'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reorder_blog_post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        reorder_blog_post.delay(**serializer.validated_data)
        return Response(data={'proces successfully started'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_banner_image(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data.get('image')
        file_path = default_storage.save(f"banner_image/{image.name}", ContentFile(image.read()))

        add_banner_image.delay(image_url=file_path,
                               blog_post_id=self.get_object().id)
        return Response(
            {'status': 'banner image successfully created'},
            status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def send_blog_post_to_email(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_blog_post_to_email.delay(
            email=serializer.validated_data['email'], blog_post_id=self.get_object().id)
        return Response(data={f'email sent to {serializer.data['email']}'}, status=status.HTTP_200_OK)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            kwargs['fields'] = ('first_name', 'last_name')
        elif self.action == 'update':
            kwargs['fields'] = ('first_name', 'last_name', 'email')
        return super().get_serializer(*args, **kwargs)

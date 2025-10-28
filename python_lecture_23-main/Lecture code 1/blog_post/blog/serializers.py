from rest_framework import serializers
from blog.models import BlogPost, BannerImage, Author


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class AuthorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'email']


class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ['id', 'image']

class BlogPostListSerializer(serializers.ModelSerializer):
    banner_image = BannerImageSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'category', 'banner_image']


class BlogPostDetailSerializer(BlogPostListSerializer):

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'category', 'banner_image', 'text', 'website', 'create_date']


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    banner_image = serializers.ImageField(required=False)

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'text', 'website', 'banner_image']

    def create(self, validated_data):
        banner_image = validated_data.pop('banner_image', None)
        validated_data['owner'] = self.context['request'].user
        blog_post = BlogPost.objects.create(**validated_data)
        if banner_image:
            BannerImage.objects.create(blog_post=blog_post, image=banner_image)
        return blog_post

    def update(self, instance, validated_data):
        banner_image = validated_data.pop('banner_image', None)
        BlogPost.objects.filter(id=instance.id).update(**validated_data)
        if banner_image:
            if BannerImage.objects.filter(blog_post=instance).exists():
                instance.banner_image.image = banner_image
                instance.banner_image.save()
            else:
                BannerImage.objects.create(blog_post=instance, image=banner_image)
        return instance

class BlogPostNotPublishedListSerializer(BlogPostListSerializer):

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'category']

class ReorderBlogPostSerializer(serializers.Serializer):
    sort_field = serializers.CharField(label='Sort field', required=True)
    asc_desc = serializers.CharField(label='Asc-Desc', required=True)


class BlogPostBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ['image']

class SendBlogPostEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email", required=True)

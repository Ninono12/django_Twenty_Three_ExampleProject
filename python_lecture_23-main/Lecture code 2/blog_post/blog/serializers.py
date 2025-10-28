from rest_framework import serializers
from blog.models import BlogPost, BlogPostCover, Author


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
    full_name = serializers.SerializerMethodField()

    @staticmethod
    def get_full_name(obj):
        return f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Author
        fields = ['id', 'full_name', 'first_name', 'last_name', 'email', 'birth_date', 'age']


class BlogPostListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True, fields=('id', 'first_name', 'last_name'))

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'created_at', 'category', 'authors']


class BlogPostDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'text', 'created_at', 'category', 'website', 'document', 'authors']


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    cover = serializers.ImageField(required=False)

    class Meta:
        model = BlogPost
        fields = ['title', 'text', 'category', 'website', 'document', 'cover']

    def create(self, validated_data):
        cover = validated_data.pop('cover', None)
        validated_data['owner'] = self.context['request'].user
        blog_post = BlogPost.objects.create(**validated_data)
        if cover:
            BlogPostCover.objects.create(blog_post=blog_post, image=cover)
        return blog_post

    def update(self, instance, validated_data):
        cover = validated_data.pop('cover', None)
        BlogPost.objects.filter(id=instance.id).update(**validated_data)
        blog_post_cover = BlogPostCover.objects.filter(blog_post=instance)
        if blog_post_cover.exists():
            cover_instance = blog_post_cover.first()
            cover_instance.image = cover
            cover_instance.save()
        else:
            BlogPostCover.objects.create(blog_post=instance, image=cover)
        return instance


class BlogPostReorderSerializer(serializers.Serializer):
    sort_field = serializers.CharField(label='Sort field', required=True)
    asc_des = serializers.CharField(label='Asc_Des', required=True)


class BlogPostSendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label='Email address', required=True)


class BlogPostCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostCover
        fields = ['image']

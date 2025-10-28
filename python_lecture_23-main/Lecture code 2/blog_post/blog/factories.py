import factory
from factory import fuzzy
from django.utils import timezone
from blog.models import BlogPost, BlogPostImage
from user.models import CustomUser
from blog.models import Author


class CustomUserFactory(factory.django.DjangoModelFactory):
    full_name = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = CustomUser


class AuthorFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("name")
    last_name = factory.Faker("name")
    email = factory.Faker("email")

    class Meta:
        model = Author


class BlogPostFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(CustomUserFactory)
    title = factory.Faker("sentence", nb_words=4)
    text = factory.Faker("paragraph", nb_sentences=3)
    is_active = True
    published = factory.Faker("boolean", chance_of_getting_true=60)
    archived = factory.Faker("boolean", chance_of_getting_true=20)
    website = factory.Faker("url")
    category = fuzzy.FuzzyChoice([1, 2, 3, 4, 5])
    order = factory.Sequence(lambda n: n)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    class Meta:
        model = BlogPost
        django_get_or_create = ("title",)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for author in extracted:
                self.authors.add(author)
        else:
            # create 1–3 random authors
            authors = AuthorFactory.create_batch(factory.random.randgen.randint(1, 3))
            for author in authors:
                self.authors.add(author)


class BlogPostImageFactory(factory.django.DjangoModelFactory):
    blog_post = factory.SubFactory(BlogPostFactory)
    image = factory.django.ImageField(filename='test_image.jpg')

    class Meta:
        model = BlogPostImage

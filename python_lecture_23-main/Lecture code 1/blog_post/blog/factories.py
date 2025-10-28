import factory
import random

from factory import Faker, SubFactory, post_generation
from blog.models import BlogPost, Author
from user.models import CustomUser
from django.core.files.base import ContentFile


class CustomUserFactory(factory.django.DjangoModelFactory):
    email = Faker("email")
    full_name = Faker("name")

    class Meta:
        model = CustomUser


class AuthorFactory(factory.django.DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")

    class Meta:
        model = Author


class BlogPostFactory(factory.django.DjangoModelFactory):
    owner = SubFactory(CustomUserFactory)
    title = Faker("sentence", nb_words=4)
    text = Faker("paragraph", nb_sentences=5)
    active = True
    published = Faker("boolean", chance_of_getting_true=70)
    archived = Faker("boolean", chance_of_getting_true=10)
    website = Faker("url")
    category = factory.LazyFunction(lambda: random.choice([1, 2, 3]))
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = BlogPost

    @factory.lazy_attribute
    def document(self):
        # Creates a fake file-like object (optional)
        file_content = b"Sample blog post document."
        return ContentFile(file_content, f"blog_doc_{self.title.replace(' ', '_')}.txt")

    @post_generation
    def authors(self, create, extracted, **kwargs):
        """Assign authors (or create some if none provided)."""
        if not create:
            return
        if extracted:
            for author in extracted:
                self.authors.add(author)
        else:
            self.authors.add(AuthorFactory())

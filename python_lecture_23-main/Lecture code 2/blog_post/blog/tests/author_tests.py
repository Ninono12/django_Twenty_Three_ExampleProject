from datetime import date
from django.test import TestCase
from blog.models import Author

class AuthorModelTest(TestCase):
    def test_author_age_property(self):
        author = Author.objects.create(
            first_name='Mariam',
            last_name='Kipshidze',
            birth_date=date(2000, 10, 10)
        )
        self.assertIsInstance(author.age, int)
        self.assertGreater(author.age, 0)

    def test_string_representation(self):
        author = Author(first_name='Ana', last_name='Smith')
        self.assertEqual(str(author), 'Ana - Smith')

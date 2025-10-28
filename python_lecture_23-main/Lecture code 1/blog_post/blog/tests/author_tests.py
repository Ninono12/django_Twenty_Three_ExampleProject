from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

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
        self.assertEqual(str(author), 'Ana Smith')


class AuthorAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author1 = Author.objects.create(first_name="Mariam", last_name="Kipshidze")
        self.author2 = Author.objects.create(first_name="Ana", last_name="Smith")

    def test_list_authors(self):
        response = self.client.get('/blog/author/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['first_name'] for item in response.data['results']]
        self.assertIn("Mariam", names)
        self.assertIn("Ana", names)

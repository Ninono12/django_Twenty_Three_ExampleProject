from django.test import TestCase, Client

class SimpleTest(TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)

class ClientTest(TestCase):
    def test_homepage(self):
        client = Client()
        response = client.get('/blog/')
        self.assertEqual(response.status_code, 200)

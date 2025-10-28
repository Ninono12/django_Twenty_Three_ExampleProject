from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from blog.factories import BlogPostFactory, AuthorFactory
from blog.models import BlogPost, Author
from user.models import CustomUser


class BlogPostModelTest(TestCase):
    def test_blogpost_str_method(self):
        post = BlogPost(title='My First Post', text='Hello world!')
        self.assertEqual(str(post), 'My First Post')


class BlogPostViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = CustomUser.objects.create_user(
            email='admin@example.com',
            password='pass'
        )
        self.user.is_staff = True
        self.user.save()

        # Create authors
        self.author = Author.objects.create(first_name="Mariam", last_name="Kipshidze")

        # Create blog posts
        self.post1 = BlogPost.objects.create(title="Published Post", text="Content 1",
                                             active=True, published=True, owner=self.user)
        self.post2 = BlogPost.objects.create(title="Unpublished Post", text="Content 2",
                                             active=True, published=False, owner=self.user)
        self.post1.authors.add(self.author)

    def test_list_published_posts(self):
        url = reverse('blogpost-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']['results']
        self.assertIsInstance(results, list)

        self.assertEqual(len(results), 2)

        titles = [item['title'] for item in results]
        self.assertIn("Published Post", titles)
        self.assertIn("Unpublished Post", titles)

    def test_retrieve_blog_post_detail(self):
        url = reverse('blogpost-detail', kwargs={'pk': self.post1.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Published Post")
        self.assertEqual(response.data['text'], "Content 1")
        self.assertIn('category', response.data)
        self.assertIn('banner_image', response.data)
        self.assertIn('website', response.data)
        self.assertIn('create_date', response.data)

    def test_create_blog_post_requires_auth(self):
        url = reverse('blogpost-list')
        data = {"title": "New Post", "text": "Some content"}

        # unauthenticated
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Changed to 403

        # authenticated
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Post")
        self.assertEqual(response.data['text'], "Some content")

    def test_update_blog_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('blogpost-detail', kwargs={'pk': self.post1.id})
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "Updated Title")

    def test_destroy_blog_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('blogpost-detail', kwargs={'pk': self.post1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.deleted)

    def test_publish_blog_post_action(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('blogpost-publish', kwargs={'pk': self.post2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post2.refresh_from_db()
        self.assertTrue(self.post2.published)

    def test_archive_blog_post_action(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('blogpost-archive', kwargs={'pk': self.post1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.archived)

    def test_not_published_list_action(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('blogpost-not-published')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item['title'] for item in response.data]
        self.assertIn("Unpublished Post", titles)
        self.assertNotIn("Published Post", titles)


class BlogPostFactoryTests(TestCase):
    def test_blog_post_creation(self):
        """Basic creation test — ensure factory creates an active post."""
        post = BlogPostFactory()
        self.assertTrue(post.active)
        self.assertIsInstance(post, BlogPost)
        self.assertIsNotNone(post.title)
        self.assertIsNotNone(post.text)

    def test_blog_post_owner_created(self):
        """Ensure owner (CustomUser) is automatically created."""
        post = BlogPostFactory()
        self.assertIsInstance(post.owner, CustomUser)
        self.assertTrue(hasattr(post.owner, "email"))

    def test_blog_post_with_authors(self):
        """Ensure author(s) are correctly assigned."""
        author1 = AuthorFactory()
        author2 = AuthorFactory()
        post = BlogPostFactory(authors=[author1, author2])

        self.assertEqual(post.authors.count(), 2)
        self.assertIn(author1, post.authors.all())
        self.assertIn(author2, post.authors.all())

    def test_blog_post_auto_creates_author_if_none_given(self):
        """Factory should create one author automatically if not provided."""
        post = BlogPostFactory()
        self.assertGreater(post.authors.count(), 0)
        self.assertIsInstance(post.authors.first(), Author)

    def test_blog_post_document_field(self):
        """Ensure document file is correctly created."""
        post = BlogPostFactory()
        self.assertTrue(post.document.name.startswith("blog_document/blog_doc_"))
        self.assertTrue(post.document.name.startswith("blog_document/blog_doc_"))
        self.assertTrue(post.document.name.endswith(".txt"))
        self.assertTrue(post.document.size > 0)

    def test_blog_post_category_in_range(self):
        """Category should be within expected random choices."""
        post = BlogPostFactory()
        self.assertIn(post.category, [1, 2, 3])

    def test_blog_post_order_is_sequential(self):
        """Order should increase with each new factory instance."""
        p1 = BlogPostFactory()
        p2 = BlogPostFactory()
        self.assertTrue(p2.order > p1.order)

    def test_blog_post_website_field(self):
        """Website field should contain a valid-looking URL."""
        post = BlogPostFactory()
        self.assertTrue(post.website.startswith("http"))

    def test_blog_post_published_flag(self):
        """Published field should be a boolean."""
        post = BlogPostFactory()
        self.assertIsInstance(post.published, bool)

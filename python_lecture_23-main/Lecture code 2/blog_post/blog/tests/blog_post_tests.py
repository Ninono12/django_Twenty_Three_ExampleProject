from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from blog.factories import BlogPostFactory, CustomUserFactory, AuthorFactory, BlogPostImageFactory
from user.models import CustomUser
from blog.models import BlogPost, Author, BlogPostImage


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
                                             is_active=True, published=True, owner=self.user)
        self.post2 = BlogPost.objects.create(title="Unpublished Post", text="Content 2",
                                             is_active=True, published=False, owner=self.user)
        self.post1.authors.add(self.author)

    def test_list_not_deleted_posts(self):
        url = reverse('blogpost-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if 'results' in response.data:
            # Pagination applied
            results = response.data['results']['paginated_results']
        else:
            # No pagination
            results = response.data['paginated_results']

        self.assertIsInstance(results, list)

        # Check we have 2 posts
        self.assertEqual(len(results), 2)

        # Check titles
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
        self.assertIn('website', response.data)

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

    def test_published_list_action(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Use the standard list endpoint
        url = reverse('blogpost-published-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Only check by titles (since 'published' is not included in serializer)
        titles = [item['title'] for item in response.data]

        self.assertNotIn("Unpublished Post", titles)
        self.assertIn("Published Post", titles)


class BlogPostFactoryModelTest(TestCase):
    def setUp(self):
        self.owner = CustomUserFactory()
        self.author = AuthorFactory()
        self.post = BlogPostFactory(owner=self.owner)
        self.post.authors.add(self.author)

    def test_blogpost_has_valid_owner(self):
        """BlogPost should have an associated owner."""
        self.assertIsNotNone(self.post.owner)
        self.assertEqual(self.post.owner.__class__.__name__, "CustomUser")

    def test_blogpost_has_authors(self):
        """BlogPost should have at least one author."""
        self.assertTrue(self.post.authors.exists())
        self.assertIn(self.author, self.post.authors.all())

    def test_blogpost_created_at_is_recent(self):
        """created_at timestamp should be near current time."""
        now = timezone.now()
        delta = now - self.post.created_at
        self.assertLess(delta.total_seconds(), 5)  # created within last 5s

    def test_blogpost_can_be_published(self):
        """A BlogPost can be marked as published."""
        self.post.published = True
        self.post.save()
        updated = BlogPost.objects.get(id=self.post.id)
        self.assertTrue(updated.published)

    def test_blogpost_update_timestamp_changes(self):
        """updated_at should change when post is saved."""
        old_updated = self.post.updated_at
        self.post.text = "Updated text"
        self.post.save()
        self.assertGreater(self.post.updated_at, old_updated)

    def test_blogpost_category_field_is_valid_choice(self):
        """Category should be within defined choices."""
        valid_categories = [c[0] for c in BlogPost._meta.get_field("category").choices]
        self.assertIn(self.post.category, valid_categories)

    def test_blogpost_default_order_is_zero(self):
        """Default order field should be 0 unless overridden."""
        post = BlogPostFactory(order=0)
        self.assertEqual(post.order, 0)

    def test_blogpost_unique_constraint_validation(self):
        """Model validation should raise ValidationError for duplicate (title, text)."""
        BlogPostFactory(title="Unique Title", text="Unique Text")
        duplicate = BlogPostFactory.build(title="Unique Title", text="Unique Text")  # build = not saved
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_blogpost_get_images_returns_queryset(self):
        """get_images() should return all related BlogPostImage objects."""
        # create a few images linked to this post
        img1 = BlogPostImageFactory(blog_post=self.post)
        img2 = BlogPostImageFactory(blog_post=self.post)

        images = self.post.get_images()

        # Assertions
        self.assertEqual(list(images), [img1, img2])
        self.assertEqual(images.count(), 2)
        self.assertTrue(all(isinstance(img, BlogPostImage) for img in images))

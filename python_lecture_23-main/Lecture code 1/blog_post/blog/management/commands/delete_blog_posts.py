from django.core.management.base import BaseCommand
from blog.models import BlogPost  # Replace with your actual app and model

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        blog_post_count = BlogPost.objects.filter(active=False).count()
        BlogPost.objects.filter(active=False).update(deleted=True)

        self.stdout.write(self.style.SUCCESS(
            f"Updated Blog posts: {blog_post_count}"
        ))


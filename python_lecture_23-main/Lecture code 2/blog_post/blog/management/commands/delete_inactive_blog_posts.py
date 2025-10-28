from django.core.management.base import BaseCommand
from blog.models import BlogPost

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        blog_posts_count = BlogPost.objects.filter(is_active=False).count()
        BlogPost.objects.filter(is_active=False).update(deleted=True)

        self.stdout.write(self.style.SUCCESS(
            f"Updated {blog_posts_count} blog posts"
        ))

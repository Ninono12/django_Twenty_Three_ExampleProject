from django.core.management.base import BaseCommand
from blog.models import BlogPost

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'sort_field',
            type=str,
            help='Field to sort by, e.g., "id", "title"'
        )
        parser.add_argument(
            'asc_des',
            type=str,
            help='Field to sort by, e.g., "-id", "title"'
        )

    def handle(self, *args, **kwargs):
        sort_field = kwargs['sort_field']
        asc_des = kwargs['asc_des']
        if asc_des == 'des':
            sort_field = f'-{sort_field}'
        blog_posts = BlogPost.objects.order_by(sort_field)

        for index, blog_post in enumerate(blog_posts, start=1):
            blog_post.order = index
            blog_post.save(update_fields=['order'])

        self.stdout.write(self.style.SUCCESS(
            f"Updated order for {blog_posts.count()} blog posts."
        ))

from django.core.management.base import BaseCommand
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Sorts Blog posts by a given field and updates the "order" field sequentially'

    def add_arguments(self, parser):
        parser.add_argument(
            'sort_field',
            type=str,
            help='Field to sort by, e.g., "-id", "title"'
        )
        parser.add_argument(
            'asc_desc',
            type=str
        )

    def handle(self, *args, **options):
        sort_field = options['sort_field']
        asc_desc = options['asc_desc']
        if asc_desc=='asc':
            blog_posts = BlogPost.objects.order_by(sort_field)
        else:
            blog_posts = BlogPost.objects.order_by(f'-{sort_field}')

        for index, blog_post in enumerate(blog_posts, start=1):
            blog_post.order = index
            blog_post.save(update_fields=['order'])

        self.stdout.write(self.style.SUCCESS(
            f"Updated order for {blog_posts.count()} blog posts"
        ))

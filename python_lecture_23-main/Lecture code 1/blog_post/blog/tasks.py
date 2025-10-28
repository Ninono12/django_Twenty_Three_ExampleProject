from celery import shared_task
from django.core.mail import send_mail

from blog.models import BlogPost, BannerImage
from blog_post import settings


@shared_task
def send_email_task(email: str):
    print(f"Sending email to {email}")

@shared_task
def delete_blog_post():
    blog_post_count = BlogPost.objects.filter(active=False).count()
    BlogPost.objects.filter(active=False).update(deleted=True)
    print(f"Updated Blog posts: {blog_post_count}")

@shared_task
def reorder_blog_post(sort_field: str, asc_desc: str):
    if asc_desc == 'asc':
        blog_posts = BlogPost.objects.order_by(sort_field)
    else:
        blog_posts = BlogPost.objects.order_by(f'-{sort_field}')

    for index, blog_post in enumerate(blog_posts, start=1):
        blog_post.order = index
        blog_post.save(update_fields=['order'])
    print(f"Updated order for {blog_posts.count()} blog posts")

@shared_task
def add_banner_image(image_url, blog_post_id: int):
    try:
        blog_post = BlogPost.objects.get(id=blog_post_id)
        BannerImage.objects.create(blog_post=blog_post, image=image_url)
        return f"Banner image created"
    except BlogPost.DoesNotExist:
        return f"Blog Post with ID {blog_post_id} not found."

@shared_task
def send_blog_post_to_email(email: str, blog_post_id: int):
    try:
        blog_post = BlogPost.objects.get(id=blog_post_id)
        send_mail(
            subject=f"{blog_post.title}",
            message=f"{blog_post.title} - {blog_post.text} - {blog_post.get_category_display()}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return f"Email sent to {blog_post.title}"
    except BlogPost.DoesNotExist:
        return f"Order with ID {blog_post_id} not found."

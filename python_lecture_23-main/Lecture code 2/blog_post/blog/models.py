from datetime import date
from django.db import models

from blog.choices import CATEGORY_CHOICES


class Author(models.Model):
    first_name = models.CharField(verbose_name='First name', max_length=100)
    last_name = models.CharField(verbose_name='Last name', max_length=100)
    email = models.EmailField(verbose_name='Email')
    birth_date = models.DateField(verbose_name='Birth date', null=True)

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


class BlogPostAuthorThroughTable(models.Model):
    authors = models.ForeignKey(to='Author', on_delete=models.CASCADE, verbose_name='Authors')
    blog_post = models.ForeignKey(to='BlogPost', on_delete=models.CASCADE, verbose_name='BlogPost')
    date = models.DateField(verbose_name='Date')

    class Meta:
        verbose_name = "Blog Post author through table"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.blog_post.title


class BlogPost(models.Model):
    owner = models.ForeignKey(
        to='user.CustomUser',
        on_delete=models.CASCADE,
        verbose_name='Owner',
        null=True
    )
    authors = models.ManyToManyField(
        to="Author",
        related_name='blog_posts',
        verbose_name='Authors'
    )
    authors_2 = models.ManyToManyField(
        to="Author",
        related_name='blog_posts_2',
        verbose_name='Authors 2',
        through='BlogPostAuthorThroughTable',
    )
    title = models.CharField(verbose_name='სათაური', max_length=255)
    text = models.TextField(verbose_name='ტექსტი')
    is_active = models.BooleanField(verbose_name='აქტიურია', default=True)
    created_at = models.DateTimeField(
        verbose_name='შექმნის თარიღი', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(
        verbose_name='განახლების თარიღი', auto_now=True, null=True)
    website = models.URLField(verbose_name='ვებ მისამართი', null=True)
    document = models.FileField(upload_to='blog_post_documents/', null=True)

    category = models.IntegerField(verbose_name='Category', choices=CATEGORY_CHOICES, null=True)
    deleted = models.BooleanField(verbose_name="Deleted", default=False)
    order = models.IntegerField(verbose_name="Order", default=0)

    published = models.BooleanField(verbose_name="Published", default=False)
    archived = models.BooleanField(verbose_name="Archived", default=False)

    def get_images(self):
        return self.images.all()

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['order']
        unique_together = [['title', 'text']]

    def __str__(self):
        return self.title


class BlogPostCover(models.Model):
    blog_post = models.OneToOneField(
        to="BlogPost",
        verbose_name='Blog Post',
        related_name='cover',
        on_delete=models.CASCADE
    )
    image = models.ImageField(verbose_name="Image", upload_to='blog_post_covers/')

    class Meta:
        verbose_name = "Blog Post Cover"
        verbose_name_plural = "Blog Post Covers"

    def __str__(self):
        return f"{self.blog_post.title} - Cover id: {self.id}"


class BlogPostImage(models.Model):
    blog_post = models.ForeignKey(
        to="BlogPost",
        related_name='images',
        verbose_name='Blog Post',
        on_delete=models.CASCADE
    )
    image = models.ImageField(verbose_name="Image", upload_to='blog_post_images/')

    class Meta:
        verbose_name = "Blog Post Image"
        verbose_name_plural = "Blog Post Images"

    def __str__(self):
        return f"{self.blog_post.title} - {self.id}"

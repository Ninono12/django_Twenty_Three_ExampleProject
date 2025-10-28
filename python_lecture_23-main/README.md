# Django Tests

- **Overview of Tests** - https://docs.djangoproject.com/en/5.1/topics/testing/:
  - Understand the importance of testing in Django applications and familiarize yourself with the Django testing framework.
- **Writing Tests** - https://docs.djangoproject.com/en/5.1/topics/testing/overview/:
  - Learn how to write unit tests and integration tests for your Django applications, ensuring that your code functions correctly and as expected.
- **Factory boy** - https://github.com/BTU-Women-in-AI-Python-course-2025/python_lecture_23/blob/main/Additional%20resources/factory_boy.md
- **Swagger** - https://github.com/BTU-Women-in-AI-Python-course-2025/python_lecture_23/blob/main/Additional%20resources/swagger.md
  
## 📝 Exercise: Write Unit and View Tests for a Simple Blog App

### Setup

You already have this model:

```python
# models.py
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def short_title(self):
        return self.title[:10] + "..." if len(self.title) > 10 else self.title
```

And this view:

```python
# views.py
from django.shortcuts import render
from .models import BlogPost

def post_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'posts/list.html', {'posts': posts})
```

### ✅ Your Task

1. **Model Test**

   * Write a test for `short_title()`:

     * If title is less than 10 characters → returns full title.
     * If more → returns first 10 characters plus "...".

2. **View Test**

   * Write a test that checks:

     * The `/posts/` page returns status code 200.
     * It contains the title of a blog post you've created in test setup.

---

### 💡 Hint

Use `self.client.get()` and `assertContains()` in the view test.

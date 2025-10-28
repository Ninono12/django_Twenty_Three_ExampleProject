# Django REST Framework Swagger — Full Documentation

## Overview

**Django REST Framework Swagger** (now commonly provided via **drf-yasg**) is a tool that **automatically generates interactive API documentation** for your Django REST Framework (DRF) APIs using the **OpenAPI/Swagger** specification.

It helps developers:

* Visualize all available API endpoints
* Test endpoints directly from the browser
* Share consistent API documentation with frontend or third-party teams

---

## Installation

You can use **`drf-yasg`** (a maintained alternative for Swagger integration):

```bash
pip install drf-yasg
```

> ⚠️ Note: The original `django-rest-swagger` package is deprecated.
> Use `drf-yasg` or `drf-spectacular` for modern Django projects.

---

## Basic Setup

### 1. Add to Installed Apps

In your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'drf_yasg',
]
```

---

### 2. Define Your Schema View

In your `urls.py` (usually at project level):

```python
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation for my project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
```

---

### 3. Add Swagger URLs

Still in your `urls.py`:

```python
from django.urls import path, re_path

urlpatterns = [
    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc UI (alternative)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

---

## Running the Server

Start your Django development server:

```bash
python manage.py runserver
```

Then visit:

* **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
* **ReDoc UI:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
* **Raw Schema (JSON):** [http://127.0.0.1:8000/swagger.json](http://127.0.0.1:8000/swagger.json)

---

## Example API View

Let’s say you have a simple DRF view:

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"})
```

Add it to your URLs:

```python
from django.urls import path
from .views import HelloWorldView

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello'),
]
```

Now it automatically appears in your Swagger documentation.

---

## Customizing Endpoints

You can customize documentation with the **`swagger_auto_schema`** decorator:

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response

class GreetingView(APIView):
    @swagger_auto_schema(
        operation_description="Get a greeting message",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Your name", type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response('OK', examples={'application/json': {'message': 'Hello, John!'}})}
    )
    def get(self, request):
        name = request.GET.get('name', 'World')
        return Response({'message': f'Hello, {name}!'})
```

---

## Authentication Integration

If your project uses **Token** or **JWT authentication**, Swagger can include an “Authorize” button.

In your `settings.py`:

```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}
```

Then Swagger will display an authentication input for bearer tokens.

---

## Example with ViewSets and Routers

```python
from rest_framework import viewsets, routers
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
```

All CRUD routes (`GET`, `POST`, `PUT`, `DELETE`) are auto-documented.

---

## YAML or JSON Export

You can export your API schema as OpenAPI JSON or YAML:

* `/swagger.json`
* `/swagger.yaml`

These can be used for integration with:

* Postman
* API Gateway tools
* CI/CD documentation pipelines

---

## Advanced Configuration

**Hide specific views:**

```python
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(auto_schema=None)
def hidden_view(request):
    ...
```

**Custom tags for grouping endpoints:**

```python
@swagger_auto_schema(tags=['Users'])
def get(self, request):
    ...
```

---

## Alternatives

If you want OpenAPI 3.0 support and more flexibility:

* **[`drf-spectacular`](https://github.com/tfranzel/drf-spectacular)** — actively maintained and OpenAPI 3 compliant.

---

## Common Issues

| Problem                    | Solution                                                                |
| -------------------------- | ----------------------------------------------------------------------- |
| `No module named drf_yasg` | Run `pip install drf-yasg`                                              |
| Blank Swagger page         | Ensure `rest_framework` and `drf_yasg` are in `INSTALLED_APPS`          |
| Missing endpoints          | Confirm your views use DRF’s APIView or ViewSet, not plain Django views |

---

## References

* [drf-yasg on PyPI](https://pypi.org/project/drf-yasg/)
* [drf-yasg GitHub Repository](https://github.com/axnsan12/drf-yasg)
* [OpenAPI Specification](https://swagger.io/specification/)

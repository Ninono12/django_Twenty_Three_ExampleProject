# factory_boy — Django Testing with a Product Model

**factory_boy** is a library that helps you easily and reliably create test data.
It’s perfect for Django applications — instead of manually setting up `Product` objects in every test, you define factories that can quickly generate them with realistic data.

---

## 📦 Installation

```bash
pip install factory_boy
```

For realistic fake data, also install **Faker** (factory_boy integrates with it automatically):

```bash
pip install Faker
```

---

## 🧩 Basic Concept

A **factory** defines how to create instances of your Django models.
You typically create one factory per model — for example, for a `Product` model.

### Example `Product` Model

```python
# shop/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
```

---

## 🧰 Creating a Product Factory

```python
# shop/factories.py
import factory
from shop.models import Product

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    description = factory.Faker("sentence")
    sku = factory.Sequence(lambda n: f"SKU-{1000 + n}")
    is_active = True
```

Now you can easily create test data:

```python
product = ProductFactory()          # creates and saves a Product instance
product_unsaved = ProductFactory.build()  # creates but doesn’t save
```

---

## ⚙️ Django Integration

`factory_boy` provides `DjangoModelFactory`, which integrates seamlessly with Django ORM.

When you call `ProductFactory()`, it automatically saves the object to the database.
When you call `.build()`, it just returns an unsaved instance.

---

## 🧰 Common Methods

| Method             | Description                                          |
| ------------------ | ---------------------------------------------------- |
| `.build()`         | Create an unsaved object                             |
| `.create()`        | Create and save to DB                                |
| `.build_batch(n)`  | Build n unsaved objects                              |
| `.create_batch(n)` | Create n saved objects                               |
| `.stub()`          | Create a simple object with attributes only (no ORM) |
| `.generate()`      | Low-level manual control                             |

Example:

```python
ProductFactory.create_batch(5)
```

This creates and saves 5 products.

---

## 🧠 Using in Django Tests

You can use factories inside Django’s `TestCase` or `pytest` tests.

### Example with Django `TestCase`

```python
# shop/tests/test_models.py
from django.test import TestCase
from shop.factories import ProductFactory

class ProductTests(TestCase):
    def test_product_creation(self):
        product = ProductFactory()
        self.assertTrue(product.pk)
        self.assertTrue(product.name)
        self.assertGreater(product.price, 0)
```

### Example with pytest

```python
# shop/tests/test_product.py
def test_product_active(db):
    product = ProductFactory(is_active=True)
    assert product.is_active
```

---

## 🧩 Sequences

`factory.Sequence` helps create unique fields like SKUs or slugs.

```python
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "shop.Product"

    name = factory.Faker("word")
    sku = factory.Sequence(lambda n: f"PROD-{n}")
```

Each product will get a unique SKU like `PROD-0`, `PROD-1`, etc.

---

## 🧠 Lazy Attributes

`factory.LazyAttribute` lets you define computed fields based on other attributes.

```python
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "shop.Product"

    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    sku = factory.LazyAttribute(lambda o: f"{o.name[:3].upper()}-{o.price}")
```

---

## 🧩 SubFactory for Relationships

If `Product` has related models, such as `Category`, you can use `SubFactory` to automatically create related objects.

### Example

```python
# shop/models.py
class Category(models.Model):
    title = models.CharField(max_length=100)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

```python
# shop/factories.py
class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "shop.Category"

    title = factory.Faker("word")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "shop.Product"

    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2)
```

This automatically creates a `Category` whenever you make a `Product`, unless you pass one explicitly:

```python
ProductFactory(category=my_existing_category)
```

---

## 🧩 Traits

Traits define variations of a factory — like “discounted” or “inactive” products.

```python
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "shop.Product"

    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2)
    is_active = True

    class Params:
        discounted = factory.Trait(
            price=factory.Faker("pydecimal", left_digits=2, right_digits=2)
        )
        inactive = factory.Trait(
            is_active=False
        )
```

Usage:

```python
cheap_product = ProductFactory(discounted=True)
inactive_product = ProductFactory(inactive=True)
```

---

## 🧰 Faker Integration

factory_boy uses **Faker** to populate fields with random data.

Some useful Faker providers for product-like data:

```python
factory.Faker("word")            # product name
factory.Faker("sentence")        # description
factory.Faker("pydecimal")       # price
factory.Faker("ean8")            # barcode
factory.Faker("text")            # long description
factory.Faker("boolean")         # stock status
```

You can also set locale globally:

```python
factory.Faker._DEFAULT_LOCALE = "en_US"
```

---

## 🧹 Resetting Sequences Between Tests

If you use sequences and want to reset them between tests:

```python
factory.Sequence.reset()
```

Django’s `TestCase` does this automatically when rolling back transactions.

---

## 🧪 Full Example

**models.py**

```python
from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

**factories.py**

```python
import factory
from shop.models import Category, Product

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Faker("word")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker("word")
    sku = factory.Sequence(lambda n: f"SKU-{1000 + n}")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2)
    description = factory.Faker("sentence")
    is_active = True
```

**tests.py**

```python
from django.test import TestCase
from shop.factories import ProductFactory

class ProductFactoryTests(TestCase):
    def test_creates_product(self):
        product = ProductFactory()
        self.assertTrue(product.pk)
        self.assertTrue(product.category)
        self.assertIn("SKU-", product.sku)
        self.assertGreater(product.price, 0)
```

---

## 🧾 References

* **Official Documentation:**
  🔗 [https://factoryboy.readthedocs.io/en/stable/](https://factoryboy.readthedocs.io/en/stable/)

* **GitHub Repository:**
  🔗 [https://github.com/FactoryBoy/factory_boy](https://github.com/FactoryBoy/factory_boy)


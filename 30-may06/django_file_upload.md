# Django File Handling: Upload Images from File or URL

A step-by-step guide to building a Django app that demonstrates file upload from a local disk or a remote URL, using generic class-based views and standard HTML forms.

---

## Project Overview

- **One model:** `Product` with `name`, `description`, `price`, `picture_1`, `picture_2`
- **CRUD:** List, Detail, Create, Update, Delete — all via Django generic CBVs
- **File handling:** Upload from local file or remote URL, saved to disk
- **No CSS styling** — pure semantic HTML

---

## 1. Project Setup

```bash
django-admin startproject fileproject
cd fileproject
python manage.py startapp catalog
```

Install dependencies:

```bash
pip install django requests pillow
```

In `fileproject/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'catalog',
]

import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## 2. The Model

`catalog/models.py`

```python
from django.db import models


class Product(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    picture_1   = models.ImageField(upload_to='products/', blank=True, null=True)
    picture_2   = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

> **Key point:** `ImageField` stores the *relative path* to the file inside `MEDIA_ROOT`. Django never stores binary data in the database.

---

## 3. The Form — Supporting Both File Upload and URL

`catalog/forms.py`

```python
from django import forms
from .models import Product
import requests
from django.core.files.base import ContentFile
import os


class ProductForm(forms.ModelForm):
    # Extra URL fields — not model fields, handled manually in save()
    picture_1_url = forms.URLField(required=False, label='Picture 1 — paste a URL')
    picture_2_url = forms.URLField(required=False, label='Picture 2 — paste a URL')

    class Meta:
        model  = Product
        fields = ['name', 'description', 'price', 'picture_1', 'picture_2']
        labels = {
            'picture_1': 'Picture 1 — upload a file',
            'picture_2': 'Picture 2 — upload a file',
        }

    def _download_from_url(self, url):
        """Fetch a remote image and return a ContentFile."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        filename = os.path.basename(url.split('?')[0]) or 'downloaded_image.jpg'
        return ContentFile(response.content, name=filename)

    def save(self, commit=True):
        instance = super().save(commit=False)

        for field in ('picture_1', 'picture_2'):
            url           = self.cleaned_data.get(f'{field}_url')
            uploaded_file = self.cleaned_data.get(field)

            if uploaded_file:
                setattr(instance, field, uploaded_file)        # file upload wins
            elif url:
                setattr(instance, field, self._download_from_url(url))

        if commit:
            instance.save()
        return instance
```

> **How it works:** Each picture has two inputs — a file picker and a URL text box. A file upload takes priority; if only a URL is given the form fetches the remote image with `requests` and saves it locally as a `ContentFile`, exactly as if the user had uploaded it directly.

---

## 4. URLs

`fileproject/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`catalog/urls.py`

```python
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('',                         views.ProductListView.as_view(),   name='list'),
    path('product/<int:pk>/',        views.ProductDetailView.as_view(), name='detail'),
    path('product/add/',             views.ProductCreateView.as_view(), name='create'),
    path('product/<int:pk>/edit/',   views.ProductUpdateView.as_view(), name='update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete'),
]
```

---

## 5. Views

`catalog/views.py`

```python
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .forms import ProductForm
from .models import Product


class ProductListView(ListView):
    model               = Product
    template_name       = 'catalog/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model         = Product
    template_name = 'catalog/product_detail.html'


class ProductCreateView(CreateView):
    model         = Product
    form_class    = ProductForm
    template_name = 'catalog/product_form.html'
    success_url   = reverse_lazy('catalog:list')


class ProductUpdateView(UpdateView):
    model         = Product
    form_class    = ProductForm
    template_name = 'catalog/product_form.html'
    success_url   = reverse_lazy('catalog:list')


class ProductDeleteView(DeleteView):
    model         = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url   = reverse_lazy('catalog:list')
```

---

## 6. Templates

### Base template

`catalog/templates/catalog/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Product Catalog{% endblock %}</title>
</head>
<body>

<nav>
    <a href="{% url 'catalog:list' %}">All Products</a> |
    <a href="{% url 'catalog:create' %}">Add Product</a>
</nav>

<hr>

{% block content %}{% endblock %}

</body>
</html>
```

---

### Product list

`catalog/templates/catalog/product_list.html`

```html
{% extends "catalog/base.html" %}

{% block title %}Products{% endblock %}

{% block content %}
<h1>Products</h1>

{% if products %}
    {% for product in products %}
        <div>
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            <p><strong>Price:</strong> ${{ product.price }}</p>

            {% if product.picture_1 %}
                <img src="{{ product.picture_1.url }}" alt="Picture 1 of {{ product.name }}" width="200">
            {% endif %}
            {% if product.picture_2 %}
                <img src="{{ product.picture_2.url }}" alt="Picture 2 of {{ product.name }}" width="200">
            {% endif %}

            <p>
                <a href="{% url 'catalog:detail' product.pk %}">View</a> |
                <a href="{% url 'catalog:update' product.pk %}">Edit</a> |
                <a href="{% url 'catalog:delete' product.pk %}">Delete</a>
            </p>
        </div>
        <hr>
    {% endfor %}
{% else %}
    <p>No products yet. <a href="{% url 'catalog:create' %}">Add one.</a></p>
{% endif %}
{% endblock %}
```

---

### Product detail

`catalog/templates/catalog/product_detail.html`

```html
{% extends "catalog/base.html" %}

{% block title %}{{ product.name }}{% endblock %}

{% block content %}
<h1>{{ product.name }}</h1>

<p>{{ product.description }}</p>
<p><strong>Price:</strong> ${{ product.price }}</p>

{% if product.picture_1 %}
    <h3>Picture 1</h3>
    <img src="{{ product.picture_1.url }}" alt="Picture 1 of {{ product.name }}" width="300">
{% endif %}

{% if product.picture_2 %}
    <h3>Picture 2</h3>
    <img src="{{ product.picture_2.url }}" alt="Picture 2 of {{ product.name }}" width="300">
{% endif %}

<p>
    <a href="{% url 'catalog:update' product.pk %}">Edit</a> |
    <a href="{% url 'catalog:delete' product.pk %}">Delete</a> |
    <a href="{% url 'catalog:list' %}">Back to list</a>
</p>
{% endblock %}
```

---

### Product form (create & update)

`catalog/templates/catalog/product_form.html`

```html
{% extends "catalog/base.html" %}

{% block title %}{% if object %}Edit{% else %}Add{% endif %} Product{% endblock %}

{% block content %}
<h1>{% if object %}Edit {{ object.name }}{% else %}Add Product{% endif %}</h1>

<!--
    enctype="multipart/form-data" is REQUIRED whenever a form includes file inputs.
    Without it the browser sends only the filename string, not the file bytes,
    and request.FILES will be empty on the server side.
-->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}

    <p>
        <label for="{{ form.name.id_for_label }}">Name</label><br>
        {{ form.name }}
        {{ form.name.errors }}
    </p>

    <p>
        <label for="{{ form.description.id_for_label }}">Description</label><br>
        {{ form.description }}
        {{ form.description.errors }}
    </p>

    <p>
        <label for="{{ form.price.id_for_label }}">Price</label><br>
        {{ form.price }}
        {{ form.price.errors }}
    </p>

    <fieldset>
        <legend>Picture 1</legend>
        <p>
            <label for="{{ form.picture_1.id_for_label }}">Upload a file</label><br>
            {{ form.picture_1 }}
            {{ form.picture_1.errors }}
        </p>
        <p>
            <label for="{{ form.picture_1_url.id_for_label }}">— or paste a URL</label><br>
            {{ form.picture_1_url }}
            {{ form.picture_1_url.errors }}
        </p>
        {% if object.picture_1 %}
            <p>Current:<br>
            <img src="{{ object.picture_1.url }}" width="100" alt="current picture 1"></p>
        {% endif %}
    </fieldset>

    <fieldset>
        <legend>Picture 2</legend>
        <p>
            <label for="{{ form.picture_2.id_for_label }}">Upload a file</label><br>
            {{ form.picture_2 }}
            {{ form.picture_2.errors }}
        </p>
        <p>
            <label for="{{ form.picture_2_url.id_for_label }}">— or paste a URL</label><br>
            {{ form.picture_2_url }}
            {{ form.picture_2_url.errors }}
        </p>
        {% if object.picture_2 %}
            <p>Current:<br>
            <img src="{{ object.picture_2.url }}" width="100" alt="current picture 2"></p>
        {% endif %}
    </fieldset>

    <p>
        <button type="submit">Save</button>
        <a href="{% url 'catalog:list' %}">Cancel</a>
    </p>
</form>
{% endblock %}
```

---

### Delete confirmation

`catalog/templates/catalog/product_confirm_delete.html`

```html
{% extends "catalog/base.html" %}

{% block title %}Delete {{ object.name }}{% endblock %}

{% block content %}
<h1>Delete {{ object.name }}?</h1>
<p>This action cannot be undone.</p>

<form method="post">
    {% csrf_token %}
    <button type="submit">Yes, delete</button>
    <a href="{% url 'catalog:list' %}">Cancel</a>
</form>
{% endblock %}
```

---

## 7. Serving Media Files in Development

Django does **not** serve user-uploaded files in production (use a dedicated file server or cloud storage there). During development the `static()` helper added to `urls.py` in section 4 handles this automatically:

```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

This line has no effect when `DEBUG = False`, so it is safe to leave in place.

---

## 8. How Django Handles File Uploads — Conceptual Summary

```
Browser                          Django
───────                          ──────
[file input]  ──multipart──▶    request.FILES['picture_1']   ← UploadedFile object
                                         │
                                    form.save()
                                         │
                                ImageField.save(name, file)
                                         │
                                MEDIA_ROOT/products/photo.jpg  ← file written to disk
                                DB stores: "products/photo.jpg" ← relative path string
```

- `request.FILES` holds uploaded files as `InMemoryUploadedFile` or `TemporaryUploadedFile` objects. Django picks based on file size (configurable via `FILE_UPLOAD_HANDLERS`).
- `ImageField` delegates storage to a **storage backend**. The default is `FileSystemStorage`, which writes to `MEDIA_ROOT`.
- The database column stores only the *relative path string* (`products/photo.jpg`), never raw bytes.
- `instance.picture_1.url` reconstructs the full URL: `MEDIA_URL + stored_path`.
- `instance.picture_1.path` gives the absolute filesystem path for reading the file server-side.

---

## 9. Run the Project

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — you should see the product list. Use **Add Product** to create your first product, uploading an image from disk or by pasting a remote URL.

---

## 10. Key Django File Concepts Demonstrated

| Concept | Where it appears |
|---|---|
| `enctype="multipart/form-data"` | `product_form.html` — required for file inputs |
| `request.FILES` | Handled automatically by `ModelForm` |
| `ImageField(upload_to=...)` | `models.py` — subdirectory inside `MEDIA_ROOT` |
| `MEDIA_ROOT` / `MEDIA_URL` | `settings.py` — filesystem path vs. URL prefix |
| Fetching a remote URL as a file | `ProductForm.save()` — `requests.get` + `ContentFile` |
| Serving media in development | `urls.py` — `static(MEDIA_URL, document_root=MEDIA_ROOT)` |

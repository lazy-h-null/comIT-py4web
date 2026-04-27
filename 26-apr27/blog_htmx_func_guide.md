# Django Blog App with HTMX — Step-by-Step Instructions

A single-page blog app using Django, plain HTML, no CSS, and HTMX for all CRUD operations plus search. Each section (Create, Read, Update, Delete, Search) is separated by an `<hr>` tag on the page.

---

## 1. Project Setup

```bash
pip install django
django-admin startproject blog_project
cd blog_project
python manage.py startapp blog
```

---

## 2. Settings

In `blog_project/settings.py`, add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'blog',
]
```

---

## 3. Model

In `blog/models.py`:

```python
from django.db import models

class Post(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 4. URLs

In `blog_project/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]
```

Create `blog/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/update/', views.post_update, name='post_update'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('posts/search/', views.post_search, name='post_search'),
]
```

---

## 5. Views

In `blog/views.py`:

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post


def index(request):
    posts = Post.objects.all().order_by('-date_created')
    return render(request, 'blog/index.html', {'posts': posts})


def post_list(request):
    posts = Post.objects.all().order_by('-date_created')
    return render(request, 'blog/partials/post_list.html', {'posts': posts})


def post_create(request):
    if request.method == 'POST':
        author = request.POST.get('author')
        title = request.POST.get('title')
        content = request.POST.get('content')
        if author and title and content:
            Post.objects.create(author=author, title=title, content=content)
        posts = Post.objects.all().order_by('-date_created')
        return render(request, 'blog/partials/post_list.html', {'posts': posts})
    return HttpResponse(status=405)


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/partials/post_edit_form.html', {'post': post})


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.author = request.POST.get('author', post.author)
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.save()
    return render(request, 'blog/partials/post_item.html', {'post': post})


from django.views.decorators.http import require_POST

@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return HttpResponse('')


def post_search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(title__icontains=query) | \
            Post.objects.filter(author__icontains=query) | \
            Post.objects.filter(content__icontains=query)
    posts = posts.order_by('-date_created')
    return render(request, 'blog/partials/post_list.html', {'posts': posts})
```

---

## 6. Templates

Create the following folder structure:

```
blog/
  templates/
    blog/
      index.html
      partials/
        post_list.html
        post_item.html
        post_edit_form.html
```

---

### `blog/templates/blog/index.html`

This is the single-page template. HTMX is loaded from CDN — no other assets needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog</title>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body>

<h1>Blog</h1>

<hr>

<h2>Create New Post</h2>
<form hx-post="/posts/create/"
      hx-target="#post-list"
      hx-swap="innerHTML"
      hx-on::after-request="this.reset()">
    {% csrf_token %}
    <p>
        <label>Author:<br>
        <input type="text" name="author" required></label>
    </p>
    <p>
        <label>Title:<br>
        <input type="text" name="title" required></label>
    </p>
    <p>
        <label>Content:<br>
        <textarea name="content" rows="4" cols="50" required></textarea></label>
    </p>
    <button type="submit">Create Post</button>
</form>

<hr>

<h2>Search Posts</h2>
<input type="search"
       name="q"
       placeholder="Search by title, author, or content..."
       hx-get="/posts/search/"
       hx-trigger="input changed delay:300ms, search"
       hx-target="#post-list"
       hx-swap="innerHTML">

<hr>

<h2>All Posts</h2>
<div id="post-list">
    {% include "blog/partials/post_list.html" %}
</div>

</body>
</html>
```

---

### `blog/templates/blog/partials/post_list.html`

```html
{% for post in posts %}
    {% include "blog/partials/post_item.html" %}
{% empty %}
    <p>No posts found.</p>
{% endfor %}
```

---

### `blog/templates/blog/partials/post_item.html`

```html
<div id="post-{{ post.pk }}">
    <h3>{{ post.title }}</h3>
    <p><strong>Author:</strong> {{ post.author }}</p>
    <p><strong>Date:</strong> {{ post.date_created|date:"Y-m-d H:i" }}</p>
    <p>{{ post.content }}</p>

    <button hx-get="/posts/{{ post.pk }}/edit/"
            hx-target="#post-{{ post.pk }}"
            hx-swap="outerHTML">
        Edit
    </button>

    <form hx-post="/posts/{{ post.pk }}/delete/"
          hx-target="#post-{{ post.pk }}"
          hx-swap="outerHTML"
          hx-confirm="Delete this post?"
          style="display:inline;">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>

    <hr>
</div>
```

---

### `blog/templates/blog/partials/post_edit_form.html`

```html
<div id="post-{{ post.pk }}">
    <form hx-post="/posts/{{ post.pk }}/update/"
          hx-target="#post-{{ post.pk }}"
          hx-swap="outerHTML">
        {% csrf_token %}
        <p>
            <label>Author:<br>
            <input type="text" name="author" value="{{ post.author }}" required></label>
        </p>
        <p>
            <label>Title:<br>
            <input type="text" name="title" value="{{ post.title }}" required></label>
        </p>
        <p>
            <label>Content:<br>
            <textarea name="content" rows="4" cols="50" required>{{ post.content }}</textarea></label>
        </p>
        <button type="submit">Save</button>
        <button type="button"
                hx-get="/posts/"
                hx-target="#post-list"
                hx-swap="innerHTML">
            Cancel
        </button>
    </form>

    <hr>
</div>
```

---

## 7. HTMX CSRF Setup

Django requires CSRF tokens for POST/DELETE requests. HTMX needs a small script to attach the token automatically. Add this inside `<head>` in `index.html`, after the HTMX script tag:

```html
<script>
    document.body.addEventListener('htmx:configRequest', function(evt) {
        evt.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
    });
</script>
```

---

## 8. Run the App

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## How It Works — CRUD Summary

| Operation | HTMX Trigger | Endpoint | Target |
|-----------|-------------|----------|--------|
| **Create** | `hx-post` on form submit | `POST /posts/create/` | `#post-list` — refreshes full list |
| **Read** | Page load / cancel | `GET /posts/` | `#post-list` |
| **Edit form** | `hx-get` on Edit button | `GET /posts/<pk>/edit/` | `#post-<pk>` — swaps post with inline form |
| **Update** | `hx-post` on edit form submit | `POST /posts/<pk>/update/` | `#post-<pk>` — swaps back to post view |
| **Delete** | `hx-delete` on Delete button | `DELETE /posts/<pk>/delete/` | `#post-<pk>` — removes element |
| **Search** | `hx-get` on input with 300ms debounce | `GET /posts/search/?q=` | `#post-list` — filters results live |

Each post block on the page ends with an `<hr>` tag, and each major section (Create, Search, All Posts) is also separated by `<hr>` tags in `index.html`.

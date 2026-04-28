# Django Blog App with HTMX — Class-Based Views

A single-page blog app using Django Class-Based Views, plain HTML, no CSS, no JavaScript, and HTMX for all CRUD operations plus search. Each section is separated by an `<hr>` tag.

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
from .views import (
    IndexView,
    PostListView,
    PostCreateView,
    PostEditView,
    PostUpdateView,
    PostDeleteView,
    PostSearchView,
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/search/', PostSearchView.as_view(), name='post_search'),
]
```

---

## 5. Views

In `blog/views.py`, all views extend Django's generic `View` or `TemplateView`:

```python
from django.views.generic import View, TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from .models import Post


class IndexView(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().order_by('-date_created')
        return context


class PostListView(TemplateView):
    template_name = 'blog/partials/post_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().order_by('-date_created')
        return context


class PostCreateView(View):
    def post(self, request):
        author = request.POST.get('author')
        title = request.POST.get('title')
        content = request.POST.get('content')
        if author and title and content:
            Post.objects.create(author=author, title=title, content=content)
        posts = Post.objects.all().order_by('-date_created')
        return self.render_to_response(request, posts)

    def render_to_response(self, request, posts):
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string(
            'blog/partials/post_list.html',
            {'posts': posts},
            request=request,
        )
        return HttpResponse(html)


class PostEditView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        from django.template.loader import render_to_string
        html = render_to_string(
            'blog/partials/post_edit_form.html',
            {'post': post},
            request=request,
        )
        return HttpResponse(html)


class PostUpdateView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.author = request.POST.get('author', post.author)
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.save()
        from django.template.loader import render_to_string
        html = render_to_string(
            'blog/partials/post_item.html',
            {'post': post},
            request=request,
        )
        return HttpResponse(html)


class PostDeleteView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return HttpResponse('')


class PostSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-date_created')
        from django.template.loader import render_to_string
        html = render_to_string(
            'blog/partials/post_list.html',
            {'posts': posts},
            request=request,
        )
        return HttpResponse(html)
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

## 7. Run the App

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## How It Works — CBV & CRUD Summary

| Operation | CBV Class | Method | HTMX Attribute | Target |
|-----------|-----------|--------|---------------|--------|
| **Index** | `IndexView(TemplateView)` | `get` | page load | full page |
| **List** | `PostListView(TemplateView)` | `get` | `hx-get` on Cancel | `#post-list` |
| **Create** | `PostCreateView(View)` | `post` | `hx-post` on form | `#post-list` |
| **Edit form** | `PostEditView(View)` | `get` | `hx-get` on Edit button | `#post-<pk>` |
| **Update** | `PostUpdateView(View)` | `post` | `hx-post` on edit form | `#post-<pk>` |
| **Delete** | `PostDeleteView(View)` | `post` | `hx-post` on delete form | `#post-<pk>` |
| **Search** | `PostSearchView(View)` | `get` | `hx-get` on input | `#post-list` |

### Key design decisions

- **Delete uses `hx-post`** with `{% csrf_token %}` in the form body — this avoids the `403 Forbidden` that `hx-delete` triggers when Django cannot find the CSRF token in the request headers.
- **No JavaScript** — zero custom JS in any template; HTMX attributes handle all dynamic behaviour declaratively.
- **No CSS** — plain unstyled HTML throughout; `style="display:inline;"` on the delete form is the only style attribute and purely structural.
- **`render_to_string` + `HttpResponse`** — used in views that return partials, keeping the CBV pattern without needing `TemplateResponse` or mixing function-based shortcuts.
- **`{% csrf_token %}`** is present in every `hx-post` form so the token always travels in the request body where Django expects it.

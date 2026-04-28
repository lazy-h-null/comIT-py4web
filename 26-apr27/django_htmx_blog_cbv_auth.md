# Django Blog App with HTMX — Class-Based Views + Authentication

A single-page blog app using Django Class-Based Views, plain HTML, no CSS, no JavaScript, and HTMX for all CRUD operations plus search. Authentication (login, logout, register) is also handled with generic CBVs. Each section is separated by an `<hr>` tag.

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

In `blog_project/settings.py`, add the app to `INSTALLED_APPS` and configure auth redirects:

```python
INSTALLED_APPS = [
    ...
    'blog',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
```

---

## 3. Model

In `blog/models.py`, link each post to Django's built-in `User`:

```python
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

## 4. Forms

Create `blog/forms.py` to hold the registration form:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
```

---

## 5. URLs

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
    RegisterView,
    CustomLoginView,
    CustomLogoutView,
)

urlpatterns = [
    # Auth
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Blog
    path('', IndexView.as_view(), name='index'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/search/', PostSearchView.as_view(), name='post_search'),
    path('posts/<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]
```

> **Note:** `posts/search/` must be declared before `posts/<int:pk>/...` to avoid the word `search` being matched as a `pk`.

---

## 6. Views

In `blog/views.py`:

- Auth views use Django's built-in `LoginView`, `LogoutView`, and the generic `FormView`.
- Blog views use `LoginRequiredMixin` to protect every route.
- Post ownership is enforced on edit, update, and delete so users can only modify their own posts.

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.views.generic import View, TemplateView, FormView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .models import Post
from .forms import RegisterForm


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

class CustomLoginView(LoginView):
    template_name = 'blog/login.html'


class CustomLogoutView(LogoutView):
    # LogoutView handles GET and POST; LOGOUT_REDIRECT_URL in settings
    # controls where the user lands after logging out.
    # def get(self, request, *args, **kwargs):
    #     logout(request)
    #     return redirect('login')
    pass


class RegisterView(FormView):
    template_name = 'blog/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Blog views — all protected with LoginRequiredMixin
# ---------------------------------------------------------------------------

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().order_by('-date_created')
        return context


class PostListView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/partials/post_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().order_by('-date_created')
        return context


class PostCreateView(LoginRequiredMixin, View):
    def post(self, request):
        author = request.POST.get('author')
        title = request.POST.get('title')
        content = request.POST.get('content')
        if author and title and content:
            Post.objects.create(
                user=request.user,
                author=author,
                title=title,
                content=content,
            )
        posts = Post.objects.all().order_by('-date_created')
        html = render_to_string(
            'blog/partials/post_list.html',
            {'posts': posts},
            request=request,
        )
        return HttpResponse(html)


class PostEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user != request.user:
            raise Http404
        html = render_to_string(
            'blog/partials/post_edit_form.html',
            {'post': post},
            request=request,
        )
        return HttpResponse(html)


class PostUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user != request.user:
            raise Http404
        post.author = request.POST.get('author', post.author)
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.save()
        html = render_to_string(
            'blog/partials/post_item.html',
            {'post': post},
            request=request,
        )
        return HttpResponse(html)


class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user != request.user:
            raise Http404
        post.delete()
        return HttpResponse('')


class PostSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-date_created')
        html = render_to_string(
            'blog/partials/post_list.html',
            {'posts': posts},
            request=request,
        )
        return HttpResponse(html)
```

---

## 7. Templates

Create the following folder structure:

```
blog/
  templates/
    blog/
      login.html
      register.html
      index.html
      partials/
        post_list.html
        post_item.html
        post_edit_form.html
```

---

### `blog/templates/blog/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>

<h1>Login</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
</form>

<hr>

<p>Don't have an account? <a href="/register/">Register</a></p>

</body>
</html>
```

---

### `blog/templates/blog/register.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Register</title>
</head>
<body>

<h1>Register</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Create Account</button>
</form>

<hr>

<p>Already have an account? <a href="/login/">Login</a></p>

</body>
</html>
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

<p>
    Logged in as <strong>{{ request.user.username }}</strong> |
    <a href=""
       hx-post ="/logout/"
       hx-include="[name=csrfmiddlewaretoken]">Logout</a>
    <!--<form method="post" action="/logout/" style="display:inline;">
    {% csrf_token %}
    <button type="submit">Logout</button>
    </form>-->
</p>

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

Edit and Delete buttons are only shown to the post's owner.

```html
<div id="post-{{ post.pk }}">
    <h3>{{ post.title }}</h3>
    <p><strong>Author:</strong> {{ post.author }}</p>
    <p><strong>Date:</strong> {{ post.date_created|date:"Y-m-d H:i" }}</p>
    <p>{{ post.content }}</p>

    {% if request.user == post.user %}
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
    {% endif %}

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

## 8. Run the App

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — unauthenticated users are redirected to `/login/` automatically.

---

## How It Works — Full CBV & Auth Summary

| View Class | Extends | Route | Purpose |
|---|---|---|---|
| `CustomLoginView` | `LoginView` | `GET/POST /login/` | Django's built-in login, custom template |
| `CustomLogoutView` | `LogoutView` | `POST /logout/` | Django's built-in logout |
| `RegisterView` | `FormView` | `GET/POST /register/` | Register + auto-login on success |
| `IndexView` | `LoginRequiredMixin, TemplateView` | `GET /` | Main page with all posts |
| `PostListView` | `LoginRequiredMixin, TemplateView` | `GET /posts/` | Partial — full post list (used by Cancel) |
| `PostCreateView` | `LoginRequiredMixin, View` | `POST /posts/create/` | Create post, returns updated list partial |
| `PostEditView` | `LoginRequiredMixin, View` | `GET /posts/<pk>/edit/` | Returns inline edit form partial |
| `PostUpdateView` | `LoginRequiredMixin, View` | `POST /posts/<pk>/update/` | Saves edits, returns post item partial |
| `PostDeleteView` | `LoginRequiredMixin, View` | `POST /posts/<pk>/delete/` | Deletes post, returns empty response |
| `PostSearchView` | `LoginRequiredMixin, View` | `GET /posts/search/` | Returns filtered post list partial |

### Key design decisions

- **`LoginRequiredMixin`** is the leftmost base class on all blog views — Django requires it before `View` or `TemplateView` so the redirect check runs first.
- **`LoginView` / `LogoutView`** are used directly from `django.contrib.auth.views` with only `template_name` overridden — no logic is duplicated.
- **`FormView`** drives registration: `form_valid` saves the user and calls `login()` to create the session, then `super().form_valid()` handles the redirect to `success_url`.
- **Ownership check** (`post.user != request.user`) in Edit, Update, and Delete raises `Http404` so no information is leaked about posts belonging to other users.
- **Template-level ownership** — the Edit and Delete controls are wrapped in `{% if request.user == post.user %}` so they never render for other users' posts.
- **Delete uses `hx-post`** with `{% csrf_token %}` in the form body — avoids the `403 Forbidden` that `hx-delete` triggers when Django cannot find the CSRF token in headers.
- **No JavaScript, no CSS** — login, register, and blog pages are all plain unstyled HTML; `style="display:inline;"` on the delete form is the only style attribute and is purely structural.
- **`posts/search/` URL order** — declared before `posts/<int:pk>/...` in `urls.py` so the literal word `search` is never interpreted as a primary key.

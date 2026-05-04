# Django + HTMX + DaisyUI
## Car Dealership App with Tailwind CSS, Auth Modal & Toast Notifications

---

## Table of Contents

1. [What Changes From the Plain HTML Version](#1-what-changes-from-the-plain-html-version)
2. [Setup — Tailwind CSS & DaisyUI](#2-setup--tailwind-css--daisyui)
3. [Settings](#3-settings)
4. [URLs](#4-urls)
5. [Forms](#5-forms)
6. [Views](#6-views)
7. [Django Messages + Toast System](#7-django-messages--toast-system)
8. [base.html — Navbar, Footer, Toast & Modal Shell](#8-basehtml--navbar-footer-toast--modal-shell)
9. [auth/modal.html — Login & Register Modal](#9-authmodalhtml--login--register-modal)
10. [landing.html — Public Home Page](#10-landinghtml--public-home-page)
11. [branch_list.html](#11-branch_listhtml)
12. [branch_detail.html](#12-branch_detailhtml)
13. [car_list.html](#13-car_listhtml)
14. [partials/car_table.html](#14-partialscar_tablehtml)
15. [car_form.html](#15-car_formhtml)
16. [car_confirm_delete.html](#16-car_confirm_deletehtml)
17. [seller_list.html](#17-seller_listhtml)
18. [partials/seller_cards.html](#18-partialsseller_cardshtml)
19. [seller_detail.html](#19-seller_detailhtml)
20. [seller_form.html](#20-seller_formhtml)
21. [seller_confirm_delete.html](#21-seller_confirm_deletehtml)
22. [Template File Structure & Checklist](#22-template-file-structure--checklist)

---

## 1. What Changes From the Plain HTML Version

The models stay **exactly the same**. What changes:

| Was | Now |
|---|---|
| No CSS | Tailwind CSS + DaisyUI via CDN |
| Plain `<nav>` | DaisyUI `navbar` with dropdowns |
| No footer | DaisyUI `footer` |
| Login/register on separate pages | DaisyUI `modal` with tabs, opened from the navbar |
| Root `/` required login | Public landing page showing branches and cars |
| No feedback after CRUD actions | Django `messages` rendered as DaisyUI colour-coded toasts |
| Plain `<button>` inline delete | HTMX `hx-delete` with `hx-confirm` |
| `LoginView` imported in `views.py` | `LoginView` / `LogoutView` imported only in `urls.py` |
| Logout via GET link | Logout via POST form (required since Django 5.0) |
| `CarInlineDeleteView` used `form_valid` | Uses `delete()` override to avoid missing `success_url` crash |

---

## 2. Setup — Tailwind CSS & DaisyUI

No build step needed. Both libraries load from CDN.

Add to `<head>` in `base.html`:

```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- DaisyUI (must come after Tailwind) -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"
      rel="stylesheet">
```

Set the DaisyUI theme on the `<html>` tag:

```html
<html lang="en" data-theme="night">
```

Other themes to try: `light`, `dark`, `cupcake`, `business`, `dracula`, `forest`, `luxury`.

---

## 3. Settings

`dealership/settings.py` — three auth redirects and the messages framework:

```python
# Where unauthenticated users are sent when hitting a protected page
LOGIN_URL = '/login/'

# Where users land after a successful login
LOGIN_REDIRECT_URL = '/'

# Where users land after logout — send to landing page, NOT /login/
LOGOUT_REDIRECT_URL = '/'

# django.contrib.messages is already in INSTALLED_APPS and MIDDLEWARE by default.
# Add MESSAGE_TAGS so Django's level names map cleanly to DaisyUI alert classes.
from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG:   'alert-info',
    message_constants.INFO:    'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR:   'alert-error',
}
```

---

## 4. URLs

`showroom/urls.py` — complete file.

Key points:
- `LoginView` and `LogoutView` are imported here, **not** in `views.py`
- The root path `/` points to the public `LandingView`
- `/branches/` is the authenticated branch list (root is no longer `BranchListView`)

```python
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [

    # ── Public ────────────────────────────────────────────────────────────
    path('', views.LandingView.as_view(), name='landing'),

    # ── Auth ──────────────────────────────────────────────────────────────
    path('login/',
         LoginView.as_view(template_name='showroom/auth/login.html'),
         name='login'),
    path('logout/',  LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # ── Branches ──────────────────────────────────────────────────────────
    path('branches/',            views.BranchListView.as_view(),   name='branch-list'),
    path('branches/<int:pk>/',   views.BranchDetailView.as_view(), name='branch-detail'),

    # ── Cars ──────────────────────────────────────────────────────────────
    path('cars/',                        views.CarListView.as_view(),          name='car-list'),
    path('cars/add/',                    views.CarCreateView.as_view(),        name='car-create'),
    path('cars/search/',                 views.CarSearchView.as_view(),        name='car-search'),
    path('cars/<int:pk>/edit/',          views.CarUpdateView.as_view(),        name='car-update'),
    path('cars/<int:pk>/delete/',        views.CarDeleteView.as_view(),        name='car-delete'),
    path('cars/<int:pk>/inline-delete/', views.CarInlineDeleteView.as_view(),  name='car-inline-delete'),

    # ── Sellers ───────────────────────────────────────────────────────────
    path('sellers/',                     views.SellerListView.as_view(),   name='seller-list'),
    path('sellers/add/',                 views.SellerCreateView.as_view(), name='seller-create'),
    path('sellers/search/',              views.SellerSearchView.as_view(), name='seller-search'),
    path('sellers/<int:pk>/',            views.SellerDetailView.as_view(), name='seller-detail'),
    path('sellers/<int:pk>/edit/',       views.SellerUpdateView.as_view(), name='seller-update'),
    path('sellers/<int:pk>/delete/',     views.SellerDeleteView.as_view(), name='seller-delete'),
]
```

`dealership/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('showroom.urls')),
]
```

---

## 5. Forms

`showroom/forms.py` — no changes from the base tutorial.

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car, Seller


class CarForm(forms.ModelForm):
    class Meta:
        model  = Car
        fields = ['make', 'model', 'year', 'price',
                  'transmission', 'branch', 'seller']


class SellerForm(forms.ModelForm):
    class Meta:
        model  = Seller
        fields = ['first_name', 'last_name', 'branches', 'is_active']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']
```

---

## 6. Views

`showroom/views.py` — complete file with all fixes applied:

- `LoginView` / `LogoutView` are **not** imported here (they live in `urls.py`)
- `login` (the function) **is** imported for use inside `RegisterView`
- `CarInlineDeleteView` overrides `delete()` instead of `form_valid()` to avoid the missing `success_url` crash
- The name string is captured **before** `.delete()` is called
- `LandingView` has no `LoginRequiredMixin` — it is public

```python
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Branch, Seller, Car
from .forms  import CarForm, SellerForm, RegisterForm


# ── Public ─────────────────────────────────────────────────────────────────

class LandingView(ListView):
    model               = Branch
    template_name       = 'showroom/landing.html'
    context_object_name = 'branches'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cars'] = Car.objects.select_related('branch', 'seller').order_by('-id')[:12]
        return ctx


# ── Auth ───────────────────────────────────────────────────────────────────
# LoginView and LogoutView are Django built-ins wired directly in urls.py.
# We only need RegisterView here.

class RegisterView(CreateView):
    form_class    = RegisterForm
    template_name = 'showroom/auth/register.html'
    success_url   = reverse_lazy('landing')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request,
            f'Welcome, {self.object.username}! Your account has been created.')
        return response


# ── Branches ───────────────────────────────────────────────────────────────

class BranchListView(LoginRequiredMixin, ListView):
    model               = Branch
    template_name       = 'showroom/branch_list.html'
    context_object_name = 'branches'


class BranchDetailView(LoginRequiredMixin, DetailView):
    model               = Branch
    template_name       = 'showroom/branch_detail.html'
    context_object_name = 'branch'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cars']    = self.object.cars.select_related('seller')
        ctx['sellers'] = self.object.sellers.filter(is_active=True)
        messages.info(self.request, f'Viewing {self.object.name} branch.')
        return ctx


# ── Cars ───────────────────────────────────────────────────────────────────

class CarListView(LoginRequiredMixin, ListView):
    model               = Car
    template_name       = 'showroom/car_list.html'
    context_object_name = 'cars'
    queryset            = Car.objects.select_related('branch', 'seller')


class CarCreateView(LoginRequiredMixin, CreateView):
    model         = Car
    form_class    = CarForm
    template_name = 'showroom/car_form.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request,
            f'{self.object} has been added to the inventory.')
        return response


class CarUpdateView(LoginRequiredMixin, UpdateView):
    model         = Car
    form_class    = CarForm
    template_name = 'showroom/car_form.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, f'{self.object} has been updated.')
        return response


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model         = Car
    template_name = 'showroom/car_confirm_delete.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        # Capture name BEFORE deletion — self.object won't exist after
        name = str(self.object)
        response = super().form_valid(form)
        messages.error(self.request, f'{name} has been deleted.')
        return response


class CarSearchView(LoginRequiredMixin, ListView):
    model               = Car
    template_name       = 'showroom/partials/car_table.html'
    context_object_name = 'cars'

    def get_queryset(self):
        q  = self.request.GET.get('q', '')
        qs = Car.objects.select_related('branch', 'seller')
        if q:
            qs = qs.filter(
                Q(make__icontains=q)  |
                Q(model__icontains=q) |
                Q(branch__name__icontains=q)
            )
        return qs


class CarInlineDeleteView(LoginRequiredMixin, DeleteView):
    """
    HTMX inline delete — returns an empty 200 response so HTMX removes the row.

    We override delete() instead of form_valid() because DeleteView calls
    get_success_url() before form_valid() runs, and with no success_url set
    it raises ImproperlyConfigured before we ever get a chance to return.
    """
    model = Car

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = str(self.object)      # capture before deletion
        self.object.delete()
        messages.error(request, f'{name} has been deleted.')
        return HttpResponse('')      # HTMX swaps this (empty) into the row


# ── Sellers ────────────────────────────────────────────────────────────────

class SellerListView(LoginRequiredMixin, ListView):
    model               = Seller
    template_name       = 'showroom/seller_list.html'
    context_object_name = 'sellers'
    queryset            = Seller.objects.prefetch_related('branches')


class SellerDetailView(LoginRequiredMixin, DetailView):
    model               = Seller
    template_name       = 'showroom/seller_detail.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cars'] = self.object.cars.select_related('branch')
        messages.info(self.request, f'Viewing seller {self.object}.')
        return ctx


class SellerCreateView(LoginRequiredMixin, CreateView):
    model         = Seller
    form_class    = SellerForm
    template_name = 'showroom/seller_form.html'
    success_url   = reverse_lazy('seller-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'{self.object} has been added.')
        return response


class SellerUpdateView(LoginRequiredMixin, UpdateView):
    model         = Seller
    form_class    = SellerForm
    template_name = 'showroom/seller_form.html'
    success_url   = reverse_lazy('seller-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, f'{self.object} has been updated.')
        return response


class SellerDeleteView(LoginRequiredMixin, DeleteView):
    model         = Seller
    template_name = 'showroom/seller_confirm_delete.html'
    success_url   = reverse_lazy('seller-list')

    def form_valid(self, form):
        name = str(self.object)
        response = super().form_valid(form)
        messages.error(self.request, f'{name} has been deleted.')
        return response


class SellerSearchView(LoginRequiredMixin, ListView):
    model               = Seller
    template_name       = 'showroom/partials/seller_cards.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        q  = self.request.GET.get('q', '')
        qs = Seller.objects.prefetch_related('branches')
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)  |
                Q(branches__name__icontains=q)
            ).distinct()
        return qs
```

---

## 7. Django Messages + Toast System

### Message level → DaisyUI colour mapping

| Action | View method | Django level | DaisyUI class | Colour |
|---|---|---|---|---|
| Create | `form_valid` on CreateView | `messages.success` | `alert-success` | 🟢 Green |
| Read | `get_context_data` on DetailView | `messages.info` | `alert-info` | 🔵 Blue |
| Update | `form_valid` on UpdateView | `messages.warning` | `alert-warning` | 🟡 Yellow |
| Delete | `form_valid` / `delete()` | `messages.error` | `alert-error` | 🔴 Red |

### How toasts are rendered

The toast block in `base.html` reads from Django's `messages` context variable and maps each message's `tags` string (set by `MESSAGE_TAGS` in settings) to the matching DaisyUI alert class. A small script auto-dismisses them after 3 seconds.

---

## 8. base.html — Navbar, Footer, Toast & Modal Shell

`showroom/templates/showroom/base.html`

```html
<!DOCTYPE html>
<html lang="en" data-theme="night">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}AutoHub{% endblock %} — AutoHub Dealerships</title>

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- DaisyUI (after Tailwind) -->
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"
        rel="stylesheet">

  <!-- HTMX -->
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>

<!--
  hx-headers sends the Django CSRF token with every HTMX request.
  This is required for hx-delete to work without a 403 Forbidden.
-->
<body class="min-h-screen flex flex-col bg-base-100"
      hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>


  <!-- ═══════════════════════════════ NAVBAR ══════════════════════════════ -->
  <div class="navbar bg-base-300 shadow-lg px-4">

    <!-- Brand -->
    <div class="navbar-start">
      <a href="{% url 'landing' %}"
         class="btn btn-ghost text-xl font-bold tracking-wide">
        🚗 AutoHub
      </a>
    </div>

    <!-- Desktop nav links -->
    <div class="navbar-center hidden lg:flex gap-1">
      {% if user.is_authenticated %}
        <a href="{% url 'branch-list' %}" class="btn btn-ghost btn-sm">Branches</a>
        <a href="{% url 'car-list' %}"    class="btn btn-ghost btn-sm">Cars</a>
        <a href="{% url 'seller-list' %}" class="btn btn-ghost btn-sm">Sellers</a>
      {% endif %}
    </div>

    <!-- Right side -->
    <div class="navbar-end gap-2">
      {% if user.is_authenticated %}

        <!-- Mobile hamburger -->
        <div class="dropdown dropdown-end lg:hidden">
          <label tabindex="0" class="btn btn-ghost btn-circle">
            <svg class="w-5 h-5" fill="none" stroke="currentColor"
                 viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round"
                    stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </label>
          <ul tabindex="0"
              class="menu menu-sm dropdown-content bg-base-200 rounded-box
                     z-50 mt-3 w-52 p-2 shadow">
            <li><a href="{% url 'branch-list' %}">Branches</a></li>
            <li><a href="{% url 'car-list' %}">Cars</a></li>
            <li><a href="{% url 'seller-list' %}">Sellers</a></li>
          </ul>
        </div>

        <!-- User avatar dropdown -->
        <div class="dropdown dropdown-end">
          <label tabindex="0"
                 class="btn btn-ghost btn-circle avatar placeholder">
            <div class="bg-primary text-primary-content rounded-full w-9">
              <span class="text-sm font-bold">
                {{ user.username|first|upper }}
              </span>
            </div>
          </label>
          <ul tabindex="0"
              class="menu menu-sm dropdown-content bg-base-200 rounded-box
                     z-50 mt-3 w-48 p-2 shadow">
            <li class="menu-title px-4 py-2 text-xs opacity-60">
              {{ user.username }}
            </li>
            <li>
              <!--
                Logout MUST be a POST form — Django 5+ rejects GET /logout/
                with 405 Method Not Allowed.
              -->
              <form method="post" action="{% url 'logout' %}">
                {% csrf_token %}
                <button type="submit" class="w-full text-left text-error">
                  Logout
                </button>
              </form>
            </li>
          </ul>
        </div>

      {% else %}
        <!-- Opens the auth modal defined below -->
        <button onclick="auth_modal.showModal()"
                class="btn btn-primary btn-sm">
          Login / Register
        </button>
      {% endif %}
    </div>
  </div><!-- /navbar -->


  <!-- ═══════════════════════════ MAIN CONTENT ════════════════════════════ -->
  <main class="flex-1 container mx-auto px-4 py-8 max-w-6xl">
    {% block content %}{% endblock %}
  </main>


  <!-- ══════════════════════════════ FOOTER ═══════════════════════════════ -->
  <footer class="footer footer-center bg-base-300 text-base-content p-6 mt-auto">
    <aside>
      <p class="font-bold text-lg">🚗 AutoHub Dealerships</p>
      <p class="text-sm opacity-60">
        4 branches &mdash; Toronto, Mississauga &amp; Scarborough
      </p>
      <p class="text-xs opacity-40 mt-1">
        &copy; {% now "Y" %} AutoHub. Built with Django + HTMX + DaisyUI.
      </p>
    </aside>
  </footer>


  <!-- ══════════════════════════ TOAST CONTAINER ══════════════════════════
       Always rendered (even when empty) so that HTMX OOB swaps from
       CarInlineDeleteView always have a valid #toast-container target.
  ════════════════════════════════════════════════════════════════════════ -->
  <div id="toast-container" class="toast toast-end toast-bottom z-50">
    {% for message in messages %}
      <div class="alert {{ message.tags }} shadow-lg">
        <span>{{ message }}</span>
      </div>
    {% endfor %}
  </div>


  <!-- ════════════════════════════ AUTH MODAL ═════════════════════════════ -->
  {% include 'showroom/auth/modal.html' %}


  <!-- Auto-dismiss toasts after 3 seconds -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        document.querySelectorAll('#toast-container .alert').forEach(el => {
          el.style.transition = 'opacity 0.5s ease';
          el.style.opacity = '0';
          setTimeout(() => el.remove(), 500);
        });
      }, 3000);
    });
  </script>

</body>
</html>
```

> 💡 `{{ message.tags }}` outputs the DaisyUI class directly (e.g. `alert-success`) because we mapped it in `MESSAGE_TAGS` in `settings.py`. No `{% if %}` chain needed in the template.

---

## 9. auth/modal.html — Login & Register Modal

`showroom/templates/showroom/auth/modal.html`

This file is included by `base.html` and is therefore available on every page.

```html
<!-- Native <dialog> element styled by DaisyUI -->
<dialog id="auth_modal" class="modal modal-bottom sm:modal-middle">
  <div class="modal-box w-full max-w-md">

    <!-- Close button (top-right) -->
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3">
        ✕
      </button>
    </form>

    <h2 class="text-2xl font-bold mb-6 text-center">Welcome to AutoHub</h2>

    <!-- Tabs: Login | Register -->
    <div role="tablist" class="tabs tabs-bordered mb-6">

      <!-- ── LOGIN TAB ─────────────────────────────────────────── -->
      <input type="radio" name="auth_tabs" role="tab"
             class="tab" aria-label="Login" checked>
      <div role="tabpanel" class="tab-content pt-4">

        <form method="post" action="{% url 'login' %}">
          {% csrf_token %}
          <!-- Redirect back to the page the user was on -->
          <input type="hidden" name="next" value="{{ request.path }}">

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Username</span>
            </label>
            <input type="text" name="username" required
                   placeholder="your username"
                   class="input input-bordered w-full">
          </div>

          <div class="form-control mb-6">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input type="password" name="password" required
                   placeholder="••••••••"
                   class="input input-bordered w-full">
          </div>

          <button type="submit" class="btn btn-primary w-full">
            Log in
          </button>
        </form>

      </div><!-- /login tab -->

      <!-- ── REGISTER TAB ──────────────────────────────────────── -->
      <input type="radio" name="auth_tabs" role="tab"
             class="tab" aria-label="Register">
      <div role="tabpanel" class="tab-content pt-4">

        <form method="post" action="{% url 'register' %}">
          {% csrf_token %}

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Username</span>
            </label>
            <input type="text" name="username" required
                   placeholder="choose a username"
                   class="input input-bordered w-full">
          </div>

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">
                Email
                <span class="opacity-50 text-xs">(optional)</span>
              </span>
            </label>
            <input type="email" name="email"
                   placeholder="you@example.com"
                   class="input input-bordered w-full">
          </div>

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input type="password" name="password1" required
                   placeholder="••••••••"
                   class="input input-bordered w-full">
          </div>

          <div class="form-control mb-6">
            <label class="label">
              <span class="label-text">Confirm Password</span>
            </label>
            <input type="password" name="password2" required
                   placeholder="••••••••"
                   class="input input-bordered w-full">
          </div>

          <button type="submit" class="btn btn-success w-full">
            Create Account
          </button>
        </form>

      </div><!-- /register tab -->

    </div><!-- /tabs -->
  </div>

  <!-- Click the backdrop to close -->
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

---

## 10. landing.html — Public Home Page

`showroom/templates/showroom/landing.html`

No login required. Shows all branches and the 12 most recent cars.

```html
{% extends 'showroom/base.html' %}
{% block title %}Welcome{% endblock %}

{% block content %}

<!-- Hero -->
<div class="hero min-h-[40vh] bg-base-200 rounded-2xl mb-12">
  <div class="hero-content text-center">
    <div>
      <h1 class="text-5xl font-bold mb-4">Find Your Next Car</h1>
      <p class="text-lg text-base-content/60 max-w-md mx-auto mb-6">
        Browse our inventory across {{ branches|length }} branch{{ branches|length|pluralize:"es" }}.
        Log in to manage listings.
      </p>
      {% if user.is_authenticated %}
        <a href="{% url 'car-list' %}" class="btn btn-primary btn-lg">
          Go to Dashboard →
        </a>
      {% else %}
        <button onclick="auth_modal.showModal()"
                class="btn btn-primary btn-lg">
          Login to Manage Inventory
        </button>
      {% endif %}
    </div>
  </div>
</div>

<!-- Branches -->
<h2 class="text-2xl font-bold mb-4">Our Branches</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-12">
  {% for branch in branches %}
  <div class="card bg-base-200 shadow">
    <div class="card-body p-4">
      <h3 class="card-title text-base">{{ branch.name }}</h3>
      <p class="text-sm text-base-content/60">{{ branch.city }}</p>
      <div class="flex gap-2 mt-2">
        <div class="badge badge-ghost badge-sm">
          🚗 {{ branch.cars.count }} car{{ branch.cars.count|pluralize }}
        </div>
      </div>
    </div>
  </div>
  {% empty %}
  <div class="col-span-4">
    <div class="alert alert-info">
      <span>No branches yet. Run <code>python manage.py seed</code>.</span>
    </div>
  </div>
  {% endfor %}
</div>

<!-- Latest Cars -->
<h2 class="text-2xl font-bold mb-4">Latest Listings</h2>
{% if cars %}
<div class="overflow-x-auto rounded-lg shadow">
  <table class="table table-zebra w-full">
    <thead class="bg-base-300">
      <tr>
        <th>Car</th>
        <th>Year</th>
        <th>Price</th>
        <th>Transmission</th>
        <th>Branch</th>
      </tr>
    </thead>
    <tbody>
      {% for car in cars %}
      <tr class="hover">
        <td class="font-semibold">{{ car.make }} {{ car.model }}</td>
        <td>{{ car.year }}</td>
        <td class="text-success font-semibold">
          ${{ car.price|floatformat:0 }}
        </td>
        <td>
          <div class="badge badge-ghost badge-sm">
            {{ car.get_transmission_display }}
          </div>
        </td>
        <td class="text-sm">{{ car.branch.name }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="alert alert-info">
  <span>No cars listed yet.</span>
</div>
{% endif %}

{% endblock %}
```

---

## 11. branch_list.html

`showroom/templates/showroom/branch_list.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}Branches{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-8">
  <div>
    <h1 class="text-3xl font-bold">Our Branches</h1>
    <p class="text-base-content/60 mt-1">
      {{ branches|length }} location{{ branches|length|pluralize }} across the city
    </p>
  </div>
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
  {% for branch in branches %}
  <div class="card bg-base-200 shadow-md hover:shadow-xl transition-shadow duration-200">
    <div class="card-body">

      <h2 class="card-title text-lg">
        {{ branch.name }}
        <div class="badge badge-primary badge-outline text-xs">
          {{ branch.city }}
        </div>
      </h2>

      <p class="text-sm text-base-content/60">
        Open since {{ branch.opened_date|date:"M Y" }}
      </p>

      {% if branch.notes %}
      <p class="text-sm mt-2 line-clamp-2">{{ branch.notes }}</p>
      {% endif %}

      <div class="flex gap-4 mt-3 text-sm">
        <span class="badge badge-ghost">
          🚗 {{ branch.cars.count }} cars
        </span>
        <span class="badge badge-ghost">
          👤 {{ branch.sellers.count }} sellers
        </span>
      </div>

      <div class="card-actions justify-end mt-4">
        <a href="{% url 'branch-detail' branch.pk %}"
           class="btn btn-primary btn-sm">
          View Branch →
        </a>
      </div>

    </div>
  </div>
  {% empty %}
  <div class="col-span-4">
    <div class="alert alert-info">
      <span>No branches found. Run <code>python manage.py seed</code>.</span>
    </div>
  </div>
  {% endfor %}
</div>
{% endblock %}
```

---

## 12. branch_detail.html

`showroom/templates/showroom/branch_detail.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}{{ branch.name }}{% endblock %}

{% block content %}

<div class="breadcrumbs text-sm mb-6">
  <ul>
    <li><a href="{% url 'branch-list' %}">Branches</a></li>
    <li>{{ branch.name }}</li>
  </ul>
</div>

<!-- Header card -->
<div class="card bg-base-200 shadow mb-8">
  <div class="card-body">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold">{{ branch.name }}</h1>
        <div class="flex flex-wrap gap-2 mt-2">
          <div class="badge badge-primary">{{ branch.city }}</div>
          <div class="badge badge-ghost">
            Open since {{ branch.opened_date|date:"F j, Y" }}
          </div>
        </div>
        {% if branch.notes %}
        <p class="mt-3 text-base-content/70 max-w-lg">{{ branch.notes }}</p>
        {% endif %}
      </div>
      <div class="stats stats-vertical lg:stats-horizontal shadow">
        <div class="stat">
          <div class="stat-title">Cars</div>
          <div class="stat-value text-primary">{{ cars|length }}</div>
        </div>
        <div class="stat">
          <div class="stat-title">Sellers</div>
          <div class="stat-value text-secondary">{{ sellers|length }}</div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

  <!-- Active sellers -->
  <div>
    <h2 class="text-xl font-bold mb-4">Active Sellers</h2>
    <div class="flex flex-col gap-3">
      {% for seller in sellers %}
      <div class="card bg-base-200 shadow-sm">
        <div class="card-body p-4 flex-row items-center gap-3">
          <div class="avatar placeholder">
            <div class="bg-secondary text-secondary-content rounded-full w-10">
              <span>{{ seller.first_name|first }}{{ seller.last_name|first }}</span>
            </div>
          </div>
          <div class="flex-1">
            <p class="font-semibold text-sm">{{ seller }}</p>
            <div class="badge badge-success badge-sm">Active</div>
          </div>
          <a href="{% url 'seller-detail' seller.pk %}"
             class="btn btn-ghost btn-xs">→</a>
        </div>
      </div>
      {% empty %}
      <p class="text-base-content/50 text-sm">No active sellers.</p>
      {% endfor %}
    </div>
  </div>

  <!-- Cars (spans 2 cols) -->
  <div class="lg:col-span-2">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">Cars at this Branch</h2>
      <a href="{% url 'car-create' %}" class="btn btn-primary btn-sm">+ Add Car</a>
    </div>

    <div class="overflow-x-auto rounded-lg shadow">
      <table class="table table-zebra w-full">
        <thead class="bg-base-300">
          <tr>
            <th>Car</th>
            <th>Year</th>
            <th>Price</th>
            <th>Trans.</th>
            <th>Seller</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {% for car in cars %}
          <tr id="car-{{ car.pk }}" class="hover">
            <td class="font-medium">{{ car.make }} {{ car.model }}</td>
            <td>{{ car.year }}</td>
            <td class="font-semibold text-success">
              ${{ car.price|floatformat:0 }}
            </td>
            <td>
              <div class="badge badge-ghost badge-sm">
                {{ car.get_transmission_display }}
              </div>
            </td>
            <td class="text-sm">{{ car.seller }}</td>
            <td class="text-right">
              <div class="join">
                <a href="{% url 'car-update' car.pk %}"
                   class="btn btn-warning btn-xs join-item">Edit</a>
                <button
                  hx-delete="{% url 'car-inline-delete' car.pk %}"
                  hx-target="#car-{{ car.pk }}"
                  hx-swap="outerHTML"
                  hx-confirm="Permanently delete {{ car }}?"
                  class="btn btn-error btn-xs join-item">
                  Delete
                </button>
              </div>
            </td>
          </tr>
          {% empty %}
          <tr>
            <td colspan="6"
                class="text-center text-base-content/50 py-8">
              No cars at this branch yet.
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

</div>
{% endblock %}
```

---

## 13. car_list.html

`showroom/templates/showroom/car_list.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}Cars{% endblock %}

{% block content %}
<div class="flex flex-wrap items-center justify-between gap-4 mb-8">
  <div>
    <h1 class="text-3xl font-bold">Car Inventory</h1>
    <p class="text-base-content/60 mt-1">All vehicles across all branches</p>
  </div>
  <a href="{% url 'car-create' %}" class="btn btn-primary">+ Add Car</a>
</div>

<!--
  HTMX live search:
  hx-get     → CarSearchView returns partials/car_table.html
  hx-trigger → fires 300 ms after the user stops typing
  hx-target  → swaps the content of #car-results
-->
<div class="form-control mb-6">
  <div class="join w-full max-w-md">
    <input
      type="search"
      name="q"
      placeholder="Search by make, model or branch…"
      hx-get="{% url 'car-search' %}"
      hx-trigger="keyup changed delay:300ms"
      hx-target="#car-results"
      hx-swap="innerHTML"
      class="input input-bordered join-item w-full"
    >
    <button class="btn join-item btn-neutral">🔍</button>
  </div>
</div>

<div id="car-results">
  {% include 'showroom/partials/car_table.html' %}
</div>
{% endblock %}
```

---

## 14. partials/car_table.html

`showroom/templates/showroom/partials/car_table.html`

> ⚠️ No `{% extends %}` — this is a fragment, not a full page.

```html
{# Fragment — returned by CarSearchView and included by car_list.html #}
{% if cars %}
<div class="overflow-x-auto rounded-lg shadow">
  <table class="table table-zebra w-full">
    <thead class="bg-base-300">
      <tr>
        <th>Car</th>
        <th>Year</th>
        <th>Price</th>
        <th>Transmission</th>
        <th>Branch</th>
        <th>Seller</th>
        <th class="text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for car in cars %}
      <tr id="car-{{ car.pk }}" class="hover">
        <td class="font-semibold">{{ car.make }} {{ car.model }}</td>
        <td>{{ car.year }}</td>
        <td class="font-semibold text-success">
          ${{ car.price|floatformat:0 }}
        </td>
        <td>
          <div class="badge badge-outline badge-sm">
            {{ car.get_transmission_display }}
          </div>
        </td>
        <td>
          <a href="{% url 'branch-detail' car.branch.pk %}"
             class="link link-hover link-primary text-sm">
            {{ car.branch.name }}
          </a>
        </td>
        <td class="text-sm">{{ car.seller }}</td>
        <td class="text-right">
          <div class="join">
            <a href="{% url 'car-update' car.pk %}"
               class="btn btn-warning btn-xs join-item">Edit</a>
            <button
              hx-delete="{% url 'car-inline-delete' car.pk %}"
              hx-target="#car-{{ car.pk }}"
              hx-swap="outerHTML"
              hx-confirm="Permanently delete {{ car }}?"
              class="btn btn-error btn-xs join-item">
              Delete
            </button>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="alert alert-info mt-4">
  <span>No cars found matching your search.</span>
</div>
{% endif %}
```

---

## 15. car_form.html

`showroom/templates/showroom/car_form.html`

Used for both create and update. `object` is set by Django only on update.

```html
{% extends 'showroom/base.html' %}
{% block title %}{% if object %}Edit Car{% else %}Add Car{% endif %}{% endblock %}

{% block content %}

<div class="breadcrumbs text-sm mb-6">
  <ul>
    <li><a href="{% url 'car-list' %}">Cars</a></li>
    <li>{% if object %}Edit {{ object }}{% else %}Add Car{% endif %}</li>
  </ul>
</div>

<div class="max-w-2xl mx-auto">
  <div class="card bg-base-200 shadow-lg">
    <div class="card-body">

      <h1 class="card-title text-2xl mb-4">
        {% if object %}✏️ Edit {{ object }}{% else %}🚗 Add a New Car{% endif %}
      </h1>

      <form method="post" novalidate>
        {% csrf_token %}

        <!-- Make -->
        <div class="form-control mb-4">
          <label class="label" for="id_make">
            <span class="label-text font-medium">Make</span>
          </label>
          <input type="text" name="make" id="id_make"
                 value="{{ form.make.value|default:'' }}"
                 placeholder="e.g. Toyota"
                 class="input input-bordered w-full
                   {% if form.make.errors %}input-error{% endif %}">
          {% for error in form.make.errors %}
            <label class="label">
              <span class="label-text-alt text-error">{{ error }}</span>
            </label>
          {% endfor %}
        </div>

        <!-- Model -->
        <div class="form-control mb-4">
          <label class="label" for="id_model">
            <span class="label-text font-medium">Model</span>
          </label>
          <input type="text" name="model" id="id_model"
                 value="{{ form.model.value|default:'' }}"
                 placeholder="e.g. Camry"
                 class="input input-bordered w-full
                   {% if form.model.errors %}input-error{% endif %}">
          {% for error in form.model.errors %}
            <label class="label">
              <span class="label-text-alt text-error">{{ error }}</span>
            </label>
          {% endfor %}
        </div>

        <!-- Year + Price -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="form-control">
            <label class="label" for="id_year">
              <span class="label-text font-medium">Year</span>
            </label>
            <input type="number" name="year" id="id_year"
                   value="{{ form.year.value|default:'' }}"
                   placeholder="2023"
                   class="input input-bordered w-full
                     {% if form.year.errors %}input-error{% endif %}">
            {% for error in form.year.errors %}
              <label class="label">
                <span class="label-text-alt text-error">{{ error }}</span>
              </label>
            {% endfor %}
          </div>

          <div class="form-control">
            <label class="label" for="id_price">
              <span class="label-text font-medium">Price ($)</span>
            </label>
            <input type="number" name="price" id="id_price"
                   step="0.01"
                   value="{{ form.price.value|default:'' }}"
                   placeholder="29999.99"
                   class="input input-bordered w-full
                     {% if form.price.errors %}input-error{% endif %}">
            {% for error in form.price.errors %}
              <label class="label">
                <span class="label-text-alt text-error">{{ error }}</span>
              </label>
            {% endfor %}
          </div>
        </div>

        <!-- Transmission -->
        <div class="form-control mb-4">
          <label class="label" for="id_transmission">
            <span class="label-text font-medium">Transmission</span>
          </label>
          <select name="transmission" id="id_transmission"
                  class="select select-bordered w-full">
            {% for value, label in form.fields.transmission.choices %}
              <option value="{{ value }}"
                {% if form.transmission.value == value %}selected{% endif %}>
                {{ label }}
              </option>
            {% endfor %}
          </select>
        </div>

        <!-- Branch -->
        <div class="form-control mb-4">
          <label class="label" for="id_branch">
            <span class="label-text font-medium">Branch</span>
          </label>
          <select name="branch" id="id_branch"
                  class="select select-bordered w-full
                    {% if form.branch.errors %}select-error{% endif %}">
            <option value="">— select a branch —</option>
            {% for value, label in form.fields.branch.choices %}
              {% if value %}
              <option value="{{ value }}"
                {% if form.branch.value|stringformat:"s" == value|stringformat:"s" %}
                  selected{% endif %}>
                {{ label }}
              </option>
              {% endif %}
            {% endfor %}
          </select>
          {% for error in form.branch.errors %}
            <label class="label">
              <span class="label-text-alt text-error">{{ error }}</span>
            </label>
          {% endfor %}
        </div>

        <!-- Seller -->
        <div class="form-control mb-6">
          <label class="label" for="id_seller">
            <span class="label-text font-medium">Seller</span>
          </label>
          <select name="seller" id="id_seller"
                  class="select select-bordered w-full">
            <option value="">— no seller assigned —</option>
            {% for value, label in form.fields.seller.choices %}
              {% if value %}
              <option value="{{ value }}"
                {% if form.seller.value|stringformat:"s" == value|stringformat:"s" %}
                  selected{% endif %}>
                {{ label }}
              </option>
              {% endif %}
            {% endfor %}
          </select>
        </div>

        <!-- Actions -->
        <div class="card-actions justify-end gap-2">
          <a href="{% url 'car-list' %}" class="btn btn-ghost">Cancel</a>
          <button type="submit"
                  class="btn {% if object %}btn-warning{% else %}btn-success{% endif %}">
            {% if object %}💾 Save Changes{% else %}➕ Add Car{% endif %}
          </button>
        </div>

      </form>
    </div>
  </div>
</div>
{% endblock %}
```

---

## 16. car_confirm_delete.html

`showroom/templates/showroom/car_confirm_delete.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}Delete Car{% endblock %}

{% block content %}
<div class="max-w-md mx-auto mt-16">
  <div class="card bg-base-200 shadow-lg border border-error/30">
    <div class="card-body text-center">

      <div class="text-6xl mb-2">🗑️</div>
      <h1 class="text-2xl font-bold text-error">Delete Car?</h1>
      <p class="text-base-content/70 mt-2">
        You are about to permanently delete
        <span class="font-bold text-base-content">{{ object }}</span>.
        This action cannot be undone.
      </p>

      <div class="card-actions justify-center gap-4 mt-6">
        <a href="{% url 'car-list' %}" class="btn btn-ghost btn-wide">
          Cancel
        </a>
        <form method="post">
          {% csrf_token %}
          <button type="submit" class="btn btn-error btn-wide">
            Yes, Delete
          </button>
        </form>
      </div>

    </div>
  </div>
</div>
{% endblock %}
```

---

## 17. seller_list.html

`showroom/templates/showroom/seller_list.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}Sellers{% endblock %}

{% block content %}
<div class="flex flex-wrap items-center justify-between gap-4 mb-8">
  <div>
    <h1 class="text-3xl font-bold">Sellers</h1>
    <p class="text-base-content/60 mt-1">All sales staff across all branches</p>
  </div>
  <a href="{% url 'seller-create' %}" class="btn btn-primary">+ Add Seller</a>
</div>

<!--
  HTMX live search — same pattern as car_list.html
  SellerSearchView returns partials/seller_cards.html
-->
<div class="form-control mb-6">
  <div class="join w-full max-w-md">
    <input
      type="search"
      name="q"
      placeholder="Search by name or branch…"
      hx-get="{% url 'seller-search' %}"
      hx-trigger="keyup changed delay:300ms"
      hx-target="#seller-results"
      hx-swap="innerHTML"
      class="input input-bordered join-item w-full"
    >
    <button class="btn join-item btn-neutral">🔍</button>
  </div>
</div>

<div id="seller-results">
  {% include 'showroom/partials/seller_cards.html' %}
</div>
{% endblock %}
```

---

## 18. partials/seller_cards.html

`showroom/templates/showroom/partials/seller_cards.html`

> ⚠️ No `{% extends %}` — this is a fragment.

```html
{# Fragment — returned by SellerSearchView and included by seller_list.html #}
{% if sellers %}
<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
  {% for seller in sellers %}
  <div id="seller-{{ seller.pk }}"
       class="card bg-base-200 shadow hover:shadow-lg transition-shadow duration-200">
    <div class="card-body p-5">

      <!-- Avatar + name -->
      <div class="flex items-center gap-3 mb-3">
        <div class="avatar placeholder">
          <div class="bg-secondary text-secondary-content rounded-full w-12">
            <span class="text-lg font-bold">
              {{ seller.first_name|first }}{{ seller.last_name|first }}
            </span>
          </div>
        </div>
        <div>
          <h3 class="font-bold text-base">
            <a href="{% url 'seller-detail' seller.pk %}"
               class="link link-hover">{{ seller }}</a>
          </h3>
          {% if seller.is_active %}
            <div class="badge badge-success badge-sm">Active</div>
          {% else %}
            <div class="badge badge-ghost badge-sm">Inactive</div>
          {% endif %}
        </div>
      </div>

      <!-- Branch badges -->
      <div class="flex flex-wrap gap-1 mb-4">
        {% for branch in seller.branches.all %}
          <a href="{% url 'branch-detail' branch.pk %}"
             class="badge badge-outline badge-primary badge-sm
                    hover:badge-primary transition-colors">
            {{ branch.name }}
          </a>
        {% empty %}
          <span class="text-xs text-base-content/40">No branches assigned</span>
        {% endfor %}
      </div>

      <!-- Actions -->
      <div class="card-actions justify-end">
        <a href="{% url 'seller-update' seller.pk %}"
           class="btn btn-warning btn-xs">Edit</a>
        <a href="{% url 'seller-delete' seller.pk %}"
           class="btn btn-error btn-xs">Delete</a>
      </div>

    </div>
  </div>
  {% endfor %}
</div>
{% else %}
<div class="alert alert-info mt-4">
  <span>No sellers found matching your search.</span>
</div>
{% endif %}
```

---

## 19. seller_detail.html

`showroom/templates/showroom/seller_detail.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}{{ seller }}{% endblock %}

{% block content %}

<div class="breadcrumbs text-sm mb-6">
  <ul>
    <li><a href="{% url 'seller-list' %}">Sellers</a></li>
    <li>{{ seller }}</li>
  </ul>
</div>

<!-- Profile card -->
<div class="card bg-base-200 shadow mb-8">
  <div class="card-body">
    <div class="flex flex-wrap items-start gap-6">

      <div class="avatar placeholder">
        <div class="bg-secondary text-secondary-content rounded-full w-20">
          <span class="text-3xl font-bold">
            {{ seller.first_name|first }}{{ seller.last_name|first }}
          </span>
        </div>
      </div>

      <div class="flex-1">
        <h1 class="text-3xl font-bold">{{ seller }}</h1>
        <div class="flex flex-wrap gap-2 mt-2">
          {% if seller.is_active %}
            <div class="badge badge-success">Active</div>
          {% else %}
            <div class="badge badge-ghost">Inactive</div>
          {% endif %}
          <div class="badge badge-neutral">
            {{ seller.cars.count }} car{{ seller.cars.count|pluralize }} managed
          </div>
        </div>

        <div class="mt-3">
          <p class="text-sm text-base-content/60 mb-1">Works at:</p>
          <div class="flex flex-wrap gap-2">
            {% for branch in seller.branches.all %}
              <a href="{% url 'branch-detail' branch.pk %}"
                 class="badge badge-primary badge-outline
                        hover:badge-primary transition-colors">
                {{ branch.name }} — {{ branch.city }}
              </a>
            {% empty %}
              <span class="text-sm text-base-content/40">No branches assigned</span>
            {% endfor %}
          </div>
        </div>
      </div>

      <a href="{% url 'seller-update' seller.pk %}"
         class="btn btn-warning btn-sm">✏️ Edit Seller</a>
    </div>
  </div>
</div>

<!-- Cars table -->
<h2 class="text-xl font-bold mb-4">
  Cars Managed by {{ seller.first_name }}
</h2>

{% if cars %}
<div class="overflow-x-auto rounded-lg shadow">
  <table class="table table-zebra w-full">
    <thead class="bg-base-300">
      <tr>
        <th>Car</th>
        <th>Year</th>
        <th>Price</th>
        <th>Branch</th>
        <th>Transmission</th>
        <th class="text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for car in cars %}
      <tr class="hover">
        <td class="font-semibold">{{ car.make }} {{ car.model }}</td>
        <td>{{ car.year }}</td>
        <td class="text-success font-semibold">
          ${{ car.price|floatformat:0 }}
        </td>
        <td>
          <a href="{% url 'branch-detail' car.branch.pk %}"
             class="link link-primary link-hover text-sm">
            {{ car.branch.name }}
          </a>
        </td>
        <td>
          <div class="badge badge-ghost badge-sm">
            {{ car.get_transmission_display }}
          </div>
        </td>
        <td class="text-right">
          <a href="{% url 'car-update' car.pk %}"
             class="btn btn-warning btn-xs">Edit</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="alert">
  <span>{{ seller.first_name }} has no cars assigned yet.</span>
</div>
{% endif %}

{% endblock %}
```

---

## 20. seller_form.html

`showroom/templates/showroom/seller_form.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}{% if object %}Edit Seller{% else %}Add Seller{% endif %}{% endblock %}

{% block content %}

<div class="breadcrumbs text-sm mb-6">
  <ul>
    <li><a href="{% url 'seller-list' %}">Sellers</a></li>
    <li>{% if object %}Edit {{ object }}{% else %}Add Seller{% endif %}</li>
  </ul>
</div>

<div class="max-w-xl mx-auto">
  <div class="card bg-base-200 shadow-lg">
    <div class="card-body">

      <h1 class="card-title text-2xl mb-4">
        {% if object %}✏️ Edit {{ object }}{% else %}👤 Add a Seller{% endif %}
      </h1>

      <form method="post" novalidate>
        {% csrf_token %}

        <!-- First name -->
        <div class="form-control mb-4">
          <label class="label" for="id_first_name">
            <span class="label-text font-medium">First Name</span>
          </label>
          <input type="text" name="first_name" id="id_first_name"
                 value="{{ form.first_name.value|default:'' }}"
                 class="input input-bordered w-full
                   {% if form.first_name.errors %}input-error{% endif %}">
          {% for error in form.first_name.errors %}
            <label class="label">
              <span class="label-text-alt text-error">{{ error }}</span>
            </label>
          {% endfor %}
        </div>

        <!-- Last name -->
        <div class="form-control mb-4">
          <label class="label" for="id_last_name">
            <span class="label-text font-medium">Last Name</span>
          </label>
          <input type="text" name="last_name" id="id_last_name"
                 value="{{ form.last_name.value|default:'' }}"
                 class="input input-bordered w-full
                   {% if form.last_name.errors %}input-error{% endif %}">
          {% for error in form.last_name.errors %}
            <label class="label">
              <span class="label-text-alt text-error">{{ error }}</span>
            </label>
          {% endfor %}
        </div>

        <!-- Branches (multi-select) -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">Branches</span>
            <span class="label-text-alt opacity-60">
              Hold Ctrl / Cmd to select multiple
            </span>
          </label>
          <select name="branches" id="id_branches" multiple
                  class="select select-bordered w-full h-32">
            {% for value, label in form.fields.branches.choices %}
            <option value="{{ value }}"
              {% if value in form.branches.value %}selected{% endif %}>
              {{ label }}
            </option>
            {% endfor %}
          </select>
        </div>

        <!-- Is active toggle -->
        <div class="form-control mb-6">
          <label class="label cursor-pointer justify-start gap-4">
            <input type="checkbox" name="is_active" id="id_is_active"
                   class="toggle toggle-success"
                   {% if form.is_active.value %}checked{% endif %}>
            <span class="label-text font-medium">Active seller</span>
          </label>
        </div>

        <!-- Actions -->
        <div class="card-actions justify-end gap-2">
          <a href="{% url 'seller-list' %}" class="btn btn-ghost">Cancel</a>
          <button type="submit"
                  class="btn {% if object %}btn-warning{% else %}btn-success{% endif %}">
            {% if object %}💾 Save Changes{% else %}➕ Add Seller{% endif %}
          </button>
        </div>

      </form>
    </div>
  </div>
</div>
{% endblock %}
```

---

## 21. seller_confirm_delete.html

`showroom/templates/showroom/seller_confirm_delete.html`

```html
{% extends 'showroom/base.html' %}
{% block title %}Delete Seller{% endblock %}

{% block content %}
<div class="max-w-md mx-auto mt-16">
  <div class="card bg-base-200 shadow-lg border border-error/30">
    <div class="card-body text-center">

      <div class="text-6xl mb-2">👤</div>
      <h1 class="text-2xl font-bold text-error">Delete Seller?</h1>
      <p class="text-base-content/70 mt-2">
        You are about to permanently remove
        <span class="font-bold text-base-content">{{ object }}</span>
        from the system. Their assigned cars will have the seller field
        cleared. This action cannot be undone.
      </p>

      <!-- Impact stats -->
      <div class="stats shadow mt-4 w-full">
        <div class="stat">
          <div class="stat-title">Cars assigned</div>
          <div class="stat-value text-error text-2xl">
            {{ object.cars.count }}
          </div>
          <div class="stat-desc">will lose their seller</div>
        </div>
        <div class="stat">
          <div class="stat-title">Branches</div>
          <div class="stat-value text-warning text-2xl">
            {{ object.branches.count }}
          </div>
          <div class="stat-desc">will lose this seller</div>
        </div>
      </div>

      <div class="card-actions justify-center gap-4 mt-6">
        <a href="{% url 'seller-list' %}" class="btn btn-ghost btn-wide">
          Cancel
        </a>
        <form method="post">
          {% csrf_token %}
          <button type="submit" class="btn btn-error btn-wide">
            Yes, Delete
          </button>
        </form>
      </div>

    </div>
  </div>
</div>
{% endblock %}
```

---

## 22. Template File Structure & Checklist

### Complete file tree

```
showroom/
└── templates/
    └── showroom/
        ├── base.html                     ← Section 8
        ├── landing.html                  ← Section 10  (public, no login needed)
        ├── auth/
        │   ├── modal.html                ← Section 9   (included by base.html)
        │   ├── login.html                ← used by LoginView in urls.py
        │   └── register.html             ← used by RegisterView
        ├── branch_list.html              ← Section 11
        ├── branch_detail.html            ← Section 12
        ├── car_list.html                 ← Section 13
        ├── car_form.html                 ← Section 15  (create + update)
        ├── car_confirm_delete.html       ← Section 16
        ├── seller_list.html              ← Section 17
        ├── seller_detail.html            ← Section 19
        ├── seller_form.html              ← Section 20  (create + update)
        ├── seller_confirm_delete.html    ← Section 21
        └── partials/
            ├── car_table.html            ← Section 14  (no {% extends %})
            └── seller_cards.html         ← Section 18  (no {% extends %})
```

### auth/login.html

This template is used by Django's built-in `LoginView`. Keep it minimal:

```html
{% extends 'showroom/base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<div class="max-w-sm mx-auto mt-20">
  <div class="card bg-base-200 shadow-lg">
    <div class="card-body">
      <h1 class="card-title text-2xl mb-4">Login</h1>
      {% if form.errors %}
        <div class="alert alert-error mb-4">
          <span>Username or password is incorrect.</span>
        </div>
      {% endif %}
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary w-full mt-4">
          Log in
        </button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

### auth/register.html

Fallback page used when JavaScript is disabled:

```html
{% extends 'showroom/base.html' %}
{% block title %}Register{% endblock %}
{% block content %}
<div class="max-w-sm mx-auto mt-20">
  <div class="card bg-base-200 shadow-lg">
    <div class="card-body">
      <h1 class="card-title text-2xl mb-4">Create Account</h1>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-success w-full mt-4">
          Register
        </button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

---

### Pre-flight checklist

- [ ] `settings.py` has `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL = '/'`
- [ ] `settings.py` has the `MESSAGE_TAGS` dict
- [ ] `urls.py` imports `LoginView` / `LogoutView` — they are **not** in `views.py`
- [ ] Root URL `/` points to `LandingView` (no `LoginRequiredMixin`)
- [ ] Authenticated branch list is at `/branches/` not `/`
- [ ] Logout is a `<form method="post">` everywhere — never an `<a href>`
- [ ] `CarInlineDeleteView` overrides `delete()`, not `form_valid()`
- [ ] `id="toast-container"` div is always present in `base.html` even when empty
- [ ] `{% include 'showroom/auth/modal.html' %}` is in `base.html`
- [ ] `partials/car_table.html` and `partials/seller_cards.html` have **no** `{% extends %}`
- [ ] Tailwind `<script>` comes before the DaisyUI `<link>` in `<head>`
- [ ] `data-theme="night"` is on the `<html>` tag

### DaisyUI component quick reference

| Component | Key classes | Used in |
|---|---|---|
| Navbar | `navbar navbar-start navbar-end` | base.html |
| Dropdown | `dropdown dropdown-end menu` | Nav menus |
| Modal | `modal modal-box modal-backdrop` | Auth modal |
| Tabs | `tabs tabs-bordered tab tab-content` | Auth modal |
| Hero | `hero hero-content` | landing.html |
| Card | `card card-body card-title card-actions` | Branches, forms |
| Table | `table table-zebra` | Cars, seller detail |
| Badge | `badge badge-primary badge-success` | Status, branch tags |
| Stats | `stats stat stat-value` | Branch detail, delete confirm |
| Avatar | `avatar placeholder` | Seller initials |
| Alert | `alert alert-success/info/warning/error` | Toasts, empty states |
| Toast | `toast toast-end toast-bottom` | Notification container |
| Button | `btn btn-primary btn-warning btn-error` | All actions |
| Input | `input input-bordered input-error` | Forms, search |
| Select | `select select-bordered` | Dropdowns |
| Toggle | `toggle toggle-success` | is_active field |
| Join | `join join-item` | Search bar, button groups |
| Breadcrumbs | `breadcrumbs` | Form and detail pages |
| Footer | `footer footer-center` | base.html |

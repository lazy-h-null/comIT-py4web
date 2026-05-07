# Modals, Django Messages & Toast Notifications
## A Practical Guide Using DaisyUI + Tailwind CSS in a Django App

---

## Table of Contents

1. [Background — Why These Three Things Work Together](#1-background--why-these-three-things-work-together)
2. [Tailwind CSS — Utility-First Styling](#2-tailwind-css--utility-first-styling)
3. [DaisyUI — Component Layer on Top of Tailwind](#3-daisyui--component-layer-on-top-of-tailwind)
4. [What is a Modal?](#4-what-is-a-modal)
5. [What is a Toast?](#5-what-is-a-toast)
6. [Django Messages Framework](#6-django-messages-framework)
7. [Wiring It All Together — Setup](#7-wiring-it-all-together--setup)
8. [Implementation — The Auth Modal](#8-implementation--the-auth-modal)
9. [Implementation — Django Messages as DaisyUI Toasts](#9-implementation--django-messages-as-daisyui-toasts)
10. [Implementation — CRUD Toasts in Views](#10-implementation--crud-toasts-in-views)
11. [Auto-Dismiss with JavaScript](#11-auto-dismiss-with-javascript)
12. [Complete base.html](#12-complete-basehtml)
13. [Common Mistakes & Fixes](#13-common-mistakes--fixes)

---

## 1. Background — Why These Three Things Work Together

When building a web application, three recurring UX challenges come up almost immediately:

**Challenge 1 — Forms that shouldn't break the page flow.**
A login form traditionally requires navigating to a separate `/login/` page, filling in the form, and being redirected back. For a car dealership dashboard where staff are already browsing inventory, that context switch is disruptive. A **modal** keeps the user on the same page and brings the form to them.

**Challenge 2 — Telling the user what just happened.**
After deleting a car, adding a seller, or saving an edit, the user needs immediate feedback. Reloading the whole page to show a message wastes a round-trip and loses scroll position. A **toast notification** appears briefly in a corner and disappears without disrupting the workflow.

**Challenge 3 — Managing those messages on the server.**
The server (Django) is the one that knows whether an action succeeded or failed. It needs a way to pass that information to the template that renders *after* a redirect, since data attached to a request is lost the moment you redirect. Django's **messages framework** solves this by persisting one-time notifications in the session across a single redirect.

These three things are designed to work together:

```
User clicks Delete
      ↓
Django view deletes the record
Django attaches a message to the session  ← messages framework
      ↓
Django redirects to the list page
      ↓
List page template renders
Template reads the message from the session ← message consumed (gone after this)
Template renders a DaisyUI toast           ← toast UI component
JavaScript removes the toast after 3s      ← auto-dismiss
```

---

## 2. Tailwind CSS — Utility-First Styling

### What it is

Tailwind CSS is a **utility-first CSS framework**. Instead of pre-built components like Bootstrap, Tailwind gives you small single-purpose CSS classes that you compose directly in your HTML.

```html
<!-- Traditional CSS approach -->
<button class="primary-button">Save</button>
<!-- requires a .primary-button rule in your CSS file -->

<!-- Tailwind approach -->
<button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  Save
</button>
<!-- all styling lives in the HTML — no separate CSS file needed -->
```

### Why we use it here

- **No context switching** between HTML and CSS files during development
- **CDN delivery** — a single `<script>` tag, no build step, no `npm`, perfect for learning
- Works as the **foundation** that DaisyUI builds on top of

### CDN setup

```html
<script src="https://cdn.tailwindcss.com"></script>
```

> 💡 The CDN build analyses your HTML at runtime and generates only the CSS you actually use. It is ideal for development. For production, use the PostCSS pipeline with PurgeCSS to strip unused styles and reduce file size.

### Key concepts you will see throughout this guide

| Class pattern | What it does | Example |
|---|---|---|
| `bg-base-100` | Background colour from DaisyUI theme | Page background |
| `text-error` | Text colour from DaisyUI theme | Error messages |
| `flex flex-col` | Flexbox layout | Page layout |
| `z-50` | Z-index (stacking order) | Toasts above everything |
| `fixed bottom-4 right-4` | Fixed positioning | Toast container |
| `transition opacity-0` | CSS transitions | Toast fade-out |
| `max-w-md mx-auto` | Centred container with max width | Modal, forms |

---

## 3. DaisyUI — Component Layer on Top of Tailwind

### What it is

DaisyUI adds **named component classes** on top of Tailwind. Where plain Tailwind requires ten classes to style a button, DaisyUI gives you `btn`. Where Tailwind needs thirty classes for a card, DaisyUI gives you `card card-body`.

```html
<!-- Plain Tailwind button -->
<button class="bg-blue-600 hover:bg-blue-700 text-white font-bold
               py-2 px-4 rounded transition-colors duration-200">
  Save
</button>

<!-- DaisyUI button -->
<button class="btn btn-primary">Save</button>
```

### Why we use it here

- Produces polished, consistent UI with minimal code
- Ships with **35 built-in themes** including a dark `night` theme
- The `modal`, `toast`, `alert`, and `navbar` components are exactly what we need for this guide
- Components are **semantic** — `alert-success` means green, `alert-error` means red, without memorising hex codes

### CDN setup

```html
<!-- Must come AFTER the Tailwind script -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"
      rel="stylesheet">
```

### Activating a theme

```html
<!-- Set on the <html> tag — applies the theme to the entire page -->
<html lang="en" data-theme="night">
```

The `night` theme gives us a dark blue-grey background with blue accents. Every DaisyUI colour class (`bg-base-100`, `text-primary`, `alert-success`) adapts automatically to the active theme.

### The components used in this guide

| Component | DaisyUI classes | Purpose |
|---|---|---|
| Modal | `modal`, `modal-box`, `modal-backdrop` | Auth login/register dialog |
| Tabs | `tabs`, `tab`, `tab-content` | Login vs Register inside the modal |
| Alert | `alert`, `alert-success`, `alert-info`, `alert-warning`, `alert-error` | Individual toast messages |
| Toast | `toast`, `toast-end`, `toast-bottom` | Positions the alert stack |
| Navbar | `navbar`, `navbar-start`, `navbar-end` | Site-wide navigation |
| Button | `btn`, `btn-primary`, `btn-error` | Action buttons |

---

## 4. What is a Modal?

### Definition

A **modal** (also called a dialog or overlay) is a UI pattern that displays content in a layer on top of the current page. The background page is dimmed and made non-interactive until the modal is closed.

```
┌─────────────────────────────────────────┐
│            (dimmed background)           │
│                                          │
│     ┌──────────────────────────┐         │
│     │        Modal Box         │         │
│     │                          │         │
│     │  [Login]  [Register]     │         │
│     │  ────────────────────    │         │
│     │  Username: [          ]  │         │
│     │  Password: [          ]  │         │
│     │                          │         │
│     │       [  Log in  ]       │         │
│     └──────────────────────────┘         │
│                                          │
└─────────────────────────────────────────┘
```

### When to use a modal

| Good use cases | Poor use cases |
|---|---|
| Login / register forms | Multi-step workflows |
| Quick confirmation ("Are you sure?") | Forms with many fields |
| Short contextual information | Content users need to reference |
| Alerts that require acknowledgment | Navigation menus |

In our dealership app we use a modal for login and registration because:
1. The user is already on a page (the landing page) and should not have to navigate away
2. The forms are short — just username and password fields
3. After submitting, they return to exactly where they were

### The HTML `<dialog>` element

Modern browsers have a native `<dialog>` HTML element. DaisyUI styles it. The browser provides the behaviour:

```html
<!-- The dialog element — hidden by default -->
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <p>Hello from the modal!</p>
    <form method="dialog">
      <!-- A form with method="dialog" closes the dialog on submit -->
      <button class="btn">Close</button>
    </form>
  </div>
</dialog>

<!-- Trigger — calls the native browser API -->
<button onclick="my_modal.showModal()">Open Modal</button>
```

Key browser APIs:
- `dialog.showModal()` — opens the dialog, dims the background, traps focus
- `dialog.close()` — closes it
- `<form method="dialog">` — any submit button inside closes the dialog

### DaisyUI modal anatomy

```html
<dialog id="auth_modal" class="modal modal-bottom sm:modal-middle">
  <!--
    modal              → base DaisyUI modal styles
    modal-bottom       → on mobile, slides up from the bottom
    sm:modal-middle    → on tablet+, appears in the centre
  -->

  <div class="modal-box">
    <!-- Content goes here -->
  </div>

  <form method="dialog" class="modal-backdrop">
    <!--
      modal-backdrop → covers the dimmed area behind the modal-box
      method="dialog" → clicking it closes the dialog (browser native)
    -->
    <button>close</button>
  </form>
</dialog>
```

---

## 5. What is a Toast?

### Definition

A **toast** (named after a toaster — it pops up and goes away) is a small non-blocking notification that appears briefly, usually in a corner of the screen, then disappears automatically. It does not require user interaction and does not block the page.

```
┌─────────────────────────────────────────────┐
│                                             │
│  Main page content                          │
│                                             │
│                                             │
│                          ┌───────────────┐  │
│                          │ ✓ Car saved!  │  │
│                          └───────────────┘  │
└─────────────────────────────────────────────┘
                            ↑ bottom-right corner
                            disappears after 3 seconds
```

### Toast vs Modal — choosing the right one

| | Toast | Modal |
|---|---|---|
| Blocks the page? | No | Yes |
| Requires user action? | No | Usually yes |
| Persists until dismissed? | No (auto-disappears) | Yes |
| Used for | Feedback after actions | Forms, confirmations |
| User attention required? | Low | High |

### DaisyUI toast anatomy

DaisyUI's toast system has two layers:

**Layer 1 — The container:** positions everything in the corner.

```html
<div class="toast toast-end toast-bottom z-50">
  <!--
    toast         → sets position: fixed
    toast-end     → aligns to the right
    toast-bottom  → aligns to the bottom
    z-50          → stacks above all other content
  -->
</div>
```

**Layer 2 — Individual alerts:** the actual notification cards inside the container.

```html
<div class="alert alert-success shadow-lg">
  <!--
    alert          → base card style
    alert-success  → green colour variant
    shadow-lg      → drop shadow
  -->
  <span>Car has been added successfully.</span>
</div>
```

Multiple alerts stack vertically inside the container:

```html
<div class="toast toast-end toast-bottom z-50">
  <div class="alert alert-success"><span>Car added.</span></div>
  <div class="alert alert-info"><span>Viewing North End branch.</span></div>
</div>
```

### The four alert colour variants

```html
<div class="alert alert-success"><!-- 🟢 Green — create actions --></div>
<div class="alert alert-info">   <!-- 🔵 Blue  — read/view actions --></div>
<div class="alert alert-warning"><!-- 🟡 Yellow — update actions --></div>
<div class="alert alert-error">  <!-- 🔴 Red   — delete actions --></div>
```

---

## 6. Django Messages Framework

### What it is

Django's messages framework is a **session-based one-time notification system** built into Django. A view attaches a message to the current request. That message is stored in the session, survives the redirect, is available exactly once in the next template, and is then automatically removed.

### Why "one-time"?

When you perform a CRUD action in Django, the pattern is:

```
POST /cars/add/ → success → redirect to /cars/
```

Data stored on the `request` object is gone after the redirect — the next request is a brand new GET to `/cars/`. The messages framework stores the notification in the **session** (server-side, keyed to the user's cookie) so it survives that redirect and appears on the destination page. After the template reads and renders it, it is deleted from the session automatically.

### The four built-in message levels

Django defines five levels. We use four:

```python
from django.contrib import messages

messages.debug(request,   "Debug info")    # level 10 — usually hidden
messages.info(request,    "FYI message")   # level 20 — blue
messages.success(request, "It worked!")    # level 25 — green
messages.warning(request, "Heads up")      # level 30 — yellow
messages.error(request,   "Something failed") # level 40 — red
```

### Where messages are stored

By default, Django uses a **fallback storage** that tries cookies first, then falls back to the session. The important thing for developers: you attach the message in the view, and read it in the template. Django handles everything in between.

### Setup — is it already on?

Yes. If you created your project with `django-admin startproject`, the messages framework is already enabled. Check that these lines are present (they are by default):

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'django.contrib.messages',   # ← must be here
]

MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',    # ← required
    'django.contrib.messages.middleware.MessageMiddleware',    # ← required
]

TEMPLATES = [{
    # ...
    'OPTIONS': {
        'context_processors': [
            # ...
            'django.contrib.messages.context_processors.messages',  # ← required
        ],
    },
}]
```

### The `message.tags` string

Each message has a `tags` attribute — a string containing the level name (e.g. `"success"`, `"error"`). This is what we use to pick the right DaisyUI class. By customising `MESSAGE_TAGS` in settings, we can make `message.tags` output the exact DaisyUI class name, eliminating the need for a chain of `{% if %}` checks in templates.

---

## 7. Wiring It All Together — Setup

### settings.py additions

```python
from django.contrib.messages import constants as message_constants

# ── Auth redirects ─────────────────────────────────────────────────────────
LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/'   # after login → landing page
LOGOUT_REDIRECT_URL = '/'   # after logout → landing page (not /login/)

# ── Map Django message levels to DaisyUI alert classes ────────────────────
# message.tags will now output the DaisyUI class directly.
# In the template: <div class="alert {{ message.tags }}"> — no {% if %} needed.
MESSAGE_TAGS = {
    message_constants.DEBUG:   'alert-info',
    message_constants.INFO:    'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR:   'alert-error',
}
```

### Why map MESSAGE_TAGS?

Without `MESSAGE_TAGS`, `message.tags` outputs the level name: `"success"`, `"error"`, etc. You would need this in the template:

```html
<!-- Without MESSAGE_TAGS — verbose and error-prone -->
<div class="alert
  {% if message.tags == 'success' %}alert-success
  {% elif message.tags == 'error' %}alert-error
  {% elif message.tags == 'warning' %}alert-warning
  {% else %}alert-info{% endif %}">
```

With `MESSAGE_TAGS` set correctly, `message.tags` is already `"alert-success"`:

```html
<!-- With MESSAGE_TAGS — clean and direct -->
<div class="alert {{ message.tags }}">
```

---

## 8. Implementation — The Auth Modal

### The trigger button (in the navbar)

The button lives in `base.html`. It calls the native browser API `showModal()` using the dialog's `id` as a global variable — a browser feature, not custom JavaScript.

```html
<!-- Only shown to unauthenticated users -->
{% if not user.is_authenticated %}
<button onclick="auth_modal.showModal()" class="btn btn-primary btn-sm">
  Login / Register
</button>
{% endif %}
```

### The modal file

`showroom/templates/showroom/auth/modal.html` — included in `base.html` with `{% include %}`:

```html
<dialog id="auth_modal" class="modal modal-bottom sm:modal-middle">
  <div class="modal-box w-full max-w-md">

    <!-- ── Close button ── -->
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3">
        ✕
      </button>
    </form>

    <h2 class="text-2xl font-bold mb-6 text-center">Welcome to AutoHub</h2>

    <!-- ── Tabs: Login | Register ── -->
    <div role="tablist" class="tabs tabs-bordered mb-6">

      <!-- Login tab -->
      <input type="radio" name="auth_tabs" role="tab"
             class="tab" aria-label="Login" checked>
      <div role="tabpanel" class="tab-content pt-4">
        <form method="post" action="{% url 'login' %}">
          {% csrf_token %}
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
      </div>

      <!-- Register tab -->
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
      </div>

    </div><!-- /tabs -->
  </div>

  <!-- Click outside to close -->
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

### How the tab mechanism works

DaisyUI tabs use **radio inputs** — when you click a tab label, the corresponding radio is checked, and CSS sibling selectors show the matching `tab-content` panel and hide the others. No JavaScript involved.

```
[radio: Login ●]  [radio: Register ○]   ← checking one hides the other's panel
─────────────────
  Login form visible
```

### The `name="next"` hidden field

```html
<input type="hidden" name="next" value="{{ request.path }}">
```

Django's `LoginView` looks for a `next` parameter in the POST data. If found, it redirects there after a successful login instead of going to `LOGIN_REDIRECT_URL`. This means if someone opens the modal on the branch detail page, they return to that same page after logging in.

### Logout — must be a POST form

Since Django 5.0, `LogoutView` only accepts POST. A plain `<a href="{% url 'logout' %}">` sends GET and returns `405 Method Not Allowed`. The logout must be a form:

```html
<!-- ✗ Wrong — sends GET, fails in Django 5+ -->
<a href="{% url 'logout' %}">Logout</a>

<!-- ✓ Correct — sends POST with CSRF token -->
<form method="post" action="{% url 'logout' %}">
  {% csrf_token %}
  <button type="submit" class="w-full text-left text-error">
    Logout
  </button>
</form>
```

---

## 9. Implementation — Django Messages as DaisyUI Toasts

### The toast block in base.html

This block goes near the bottom of `<body>`, before any scripts. It renders once per page load and is automatically populated by Django with whatever messages are in the session.

```html
<!--
  The container is always rendered, even when there are no messages.
  This matters for HTMX: inline-delete responses can use hx-swap-oob
  to inject new alerts into this container without a full page reload.
-->
<div id="toast-container" class="toast toast-end toast-bottom z-50">
  {% for message in messages %}
    <!--
      message.tags outputs the DaisyUI class directly (e.g. "alert-success")
      because we configured MESSAGE_TAGS in settings.py.
    -->
    <div class="alert {{ message.tags }} shadow-lg">
      <span>{{ message }}</span>
    </div>
  {% endfor %}
</div>
```

### Why always render the container?

If the `#toast-container` div only appears when there are messages, HTMX inline-delete responses that try to inject a toast via `hx-swap-oob="beforeend:#toast-container"` will silently fail because the target element does not exist in the DOM. Always rendering the empty container guarantees the target is always there.

### Reading messages in a template

The `{% for message in messages %}` loop is available in any template that extends `base.html` because `base.html` includes it. The messages context processor (registered in `settings.py` TEMPLATES) injects the `messages` variable automatically — you never pass it manually from views.

### What happens to messages after rendering

Once Django renders `{% for message in messages %}`, those messages are marked as used and removed from the session. They will not appear on the next page load. This is the "one-time" behaviour: produce the message in the view, consume it in the very next template, gone forever.

---

## 10. Implementation — CRUD Toasts in Views

### The colour convention

We follow a consistent colour coding across all CRUD operations:

| Operation | View method | Message level | Toast colour | Rationale |
|---|---|---|---|---|
| **C**reate | `form_valid` on `CreateView` | `messages.success` | 🟢 Green | Positive outcome |
| **R**ead | `get_context_data` on `DetailView` | `messages.info` | 🔵 Blue | Neutral information |
| **U**pdate | `form_valid` on `UpdateView` | `messages.warning` | 🟡 Yellow | Caution — data changed |
| **D**elete | `form_valid` on `DeleteView` | `messages.error` | 🔴 Red | Destructive action |

### CreateView — success toast

```python
class CarCreateView(LoginRequiredMixin, CreateView):
    model         = Car
    form_class    = CarForm
    template_name = 'showroom/car_form.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        # super().form_valid() saves the object and redirects.
        # self.object is available after super() returns.
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'{self.object} has been added to the inventory.'
        )
        return response
        # Message is now in the session.
        # The redirect sends the browser to /cars/.
        # /cars/ renders base.html which reads the message and shows the toast.
```

### UpdateView — warning toast

```python
class CarUpdateView(LoginRequiredMixin, UpdateView):
    model         = Car
    form_class    = CarForm
    template_name = 'showroom/car_form.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, f'{self.object} has been updated.')
        return response
```

### DeleteView — error toast

```python
class CarDeleteView(LoginRequiredMixin, DeleteView):
    model         = Car
    template_name = 'showroom/car_confirm_delete.html'
    success_url   = reverse_lazy('car-list')

    def form_valid(self, form):
        # ⚠️ Capture the name BEFORE deletion.
        # After super().form_valid() the record is gone from the database
        # and str(self.object) may raise an error.
        name = str(self.object)
        response = super().form_valid(form)
        messages.error(self.request, f'{name} has been deleted.')
        return response
```

### HTMX inline delete — special case

The inline delete (triggered by HTMX `hx-delete`) does **not** redirect. It returns an HTTP response directly to HTMX, which swaps it into the DOM. This means the normal message → redirect → render cycle does not apply.

The fix is to override `delete()` (not `form_valid()`) and return an empty `HttpResponse`. The toast cannot come from the session in this case — it either needs to be rendered directly in the response or handled client-side.

```python
class CarInlineDeleteView(LoginRequiredMixin, DeleteView):
    """
    Returns an empty 200 response so HTMX removes the table row.

    We override delete() instead of form_valid() because:
    - DeleteView.dispatch() calls get_success_url() before form_valid()
    - With no success_url defined, it raises ImproperlyConfigured
    - Overriding delete() bypasses that flow entirely
    """
    model = Car

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = str(self.object)     # capture before deletion
        self.object.delete()
        messages.error(request, f'{name} has been deleted.')
        # Return empty body — HTMX replaces the <tr> with nothing (removes it)
        return HttpResponse('')
```

> 💡 The `messages.error()` call here stores the message in the session even though we return an empty response. The message will appear the next time the user navigates to any page that renders `base.html` — which usually happens immediately if they stay on the car list. If you want the toast to appear instantly without a page transition, you would need to return the toast HTML directly in the response and use HTMX's `hx-swap-oob` to inject it into `#toast-container`.

### DetailView — info toast

```python
class BranchDetailView(LoginRequiredMixin, DetailView):
    model               = Branch
    template_name       = 'showroom/branch_detail.html'
    context_object_name = 'branch'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cars']    = self.object.cars.select_related('seller')
        ctx['sellers'] = self.object.sellers.filter(is_active=True)
        # Attach the info message — it renders immediately (no redirect)
        # so it appears on this very page load.
        messages.info(self.request, f'Viewing {self.object.name} branch.')
        return ctx
```

---

## 11. Auto-Dismiss with JavaScript

DaisyUI toasts do not disappear on their own — they are static HTML elements. A small script handles the fade-out.

```html
<script>
  document.addEventListener('DOMContentLoaded', () => {
    // Wait 3 seconds after the page loads, then fade each toast out.
    setTimeout(() => {
      document.querySelectorAll('#toast-container .alert').forEach(el => {
        // CSS transition for smooth fade
        el.style.transition = 'opacity 0.5s ease';
        el.style.opacity    = '0';
        // Remove from DOM after the fade completes (500ms)
        setTimeout(() => el.remove(), 500);
      });
    }, 3000);
  });
</script>
```

### Step-by-step breakdown

```
Page loads
  ↓
DOMContentLoaded fires
  ↓
setTimeout waits 3000ms (3 seconds)
  ↓
querySelectorAll finds every .alert inside #toast-container
  ↓
For each alert:
  - Set transition: opacity 0.5s ease  (tells browser to animate the next change)
  - Set opacity: 0                     (triggers the fade animation)
  ↓
After 500ms (animation complete):
  - el.remove() deletes the element from the DOM entirely
```

### Why remove from the DOM instead of just hiding?

Setting `opacity: 0` makes the element invisible but it still occupies space. `el.remove()` eliminates it entirely so it does not leave a gap in the toast stack.

---

## 12. Complete base.html

This is the full `base.html` with all concepts from this guide integrated. Every other template in the app extends this file.

`showroom/templates/showroom/base.html`:

```html
<!DOCTYPE html>
<html lang="en" data-theme="night">
  <!--
    data-theme="night" → activates DaisyUI's dark blue-grey theme.
    All colour classes (bg-base-100, text-primary, alert-success, etc.)
    resolve to the night theme's palette automatically.
  -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}AutoHub{% endblock %} — AutoHub Dealerships</title>

  <!-- 1. Tailwind CSS — must load first, DaisyUI depends on it -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- 2. DaisyUI — component classes built on top of Tailwind -->
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"
        rel="stylesheet">

  <!-- 3. HTMX — for live search and inline delete -->
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>

<!--
  hx-headers on <body>: every HTMX request (hx-get, hx-delete, etc.)
  automatically includes the Django CSRF token in its headers.
  Without this, hx-delete returns 403 Forbidden.
-->
<body class="min-h-screen flex flex-col bg-base-100"
      hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>


  <!-- ════════════════════════════ NAVBAR ════════════════════════════════ -->
  <div class="navbar bg-base-300 shadow-lg px-4">

    <div class="navbar-start">
      <a href="{% url 'landing' %}"
         class="btn btn-ghost text-xl font-bold tracking-wide">
        🚗 AutoHub
      </a>
    </div>

    <div class="navbar-center hidden lg:flex gap-1">
      {% if user.is_authenticated %}
        <a href="{% url 'branch-list' %}" class="btn btn-ghost btn-sm">Branches</a>
        <a href="{% url 'car-list' %}"    class="btn btn-ghost btn-sm">Cars</a>
        <a href="{% url 'seller-list' %}" class="btn btn-ghost btn-sm">Sellers</a>
      {% endif %}
    </div>

    <div class="navbar-end gap-2">
      {% if user.is_authenticated %}

        <!-- Mobile hamburger dropdown -->
        <div class="dropdown dropdown-end lg:hidden">
          <label tabindex="0" class="btn btn-ghost btn-circle">
            <svg class="w-5 h-5" fill="none" stroke="currentColor"
                 viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round"
                    stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </label>
          <ul tabindex="0"
              class="menu menu-sm dropdown-content bg-base-200
                     rounded-box z-50 mt-3 w-52 p-2 shadow">
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
              class="menu menu-sm dropdown-content bg-base-200
                     rounded-box z-50 mt-3 w-48 p-2 shadow">
            <li class="menu-title px-4 py-2 text-xs opacity-60">
              {{ user.username }}
            </li>
            <li>
              <!--
                Logout MUST be POST. Django 5+ rejects GET /logout/ with 405.
                A <form method="post"> with {% csrf_token %} is the correct approach.
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
        <!--
          Opens the auth modal.
          auth_modal is the <dialog id="auth_modal"> defined below.
          .showModal() is a native browser method — no custom JS needed.
        -->
        <button onclick="auth_modal.showModal()"
                class="btn btn-primary btn-sm">
          Login / Register
        </button>
      {% endif %}
    </div>
  </div><!-- /navbar -->


  <!-- ══════════════════════════ MAIN CONTENT ═════════════════════════════ -->
  <main class="flex-1 container mx-auto px-4 py-8 max-w-6xl">
    {% block content %}{% endblock %}
  </main>


  <!-- ════════════════════════════ FOOTER ════════════════════════════════ -->
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
       Always present in the DOM — even when empty — so that HTMX OOB swaps
       can inject new toasts without a full page reload.
       message.tags outputs the DaisyUI class (e.g. "alert-success") directly
       because of MESSAGE_TAGS in settings.py.
  ════════════════════════════════════════════════════════════════════════ -->
  <div id="toast-container" class="toast toast-end toast-bottom z-50">
    {% for message in messages %}
      <div class="alert {{ message.tags }} shadow-lg">
        <span>{{ message }}</span>
      </div>
    {% endfor %}
  </div>


  <!-- ═══════════════════════════ AUTH MODAL ══════════════════════════════
       Included as a separate file to keep base.html readable.
       The <dialog> is hidden by default — showModal() reveals it.
  ════════════════════════════════════════════════════════════════════════ -->
  {% include 'showroom/auth/modal.html' %}


  <!-- ══════════════════════════ TOAST DISMISS ════════════════════════════
       Auto-fades and removes toast alerts 3 seconds after page load.
  ════════════════════════════════════════════════════════════════════════ -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        document.querySelectorAll('#toast-container .alert').forEach(el => {
          el.style.transition = 'opacity 0.5s ease';
          el.style.opacity    = '0';
          setTimeout(() => el.remove(), 500);
        });
      }, 3000);
    });
  </script>

</body>
</html>
```

---

## 13. Common Mistakes & Fixes

### Modal does not open

**Symptom:** clicking "Login / Register" does nothing.

**Cause:** the `<dialog id="auth_modal">` is not in the DOM when the button is clicked. Usually because `{% include 'showroom/auth/modal.html' %}` is missing from `base.html`, or the template path is wrong.

**Fix:** confirm the include is present in `base.html` and the file exists at exactly `showroom/templates/showroom/auth/modal.html`.

---

### Logout returns 405 Method Not Allowed

**Symptom:** clicking logout shows "This page isn't working" in the browser.

**Cause:** the logout link sends a GET request. Django 5.0+ only accepts POST for logout.

**Fix:** replace the `<a>` tag with a `<form>`:

```html
<!-- ✗ -->
<a href="{% url 'logout' %}">Logout</a>

<!-- ✓ -->
<form method="post" action="{% url 'logout' %}">
  {% csrf_token %}
  <button type="submit">Logout</button>
</form>
```

---

### After logout, redirected to /accounts/profile/ (404)

**Cause:** `LOGOUT_REDIRECT_URL` is not set in `settings.py`. Django's default is `/accounts/profile/`.

**Fix:**
```python
LOGOUT_REDIRECT_URL = '/'
```

---

### Inline delete crashes with ImproperlyConfigured: No URL to redirect to

**Symptom:** `DELETE /cars/6/inline-delete/` returns a 500 error.

**Cause:** `CarInlineDeleteView` has no `success_url`. `DeleteView` calls `get_success_url()` before your `form_valid()` can run and return early.

**Fix:** override `delete()` instead of `form_valid()`:

```python
# ✗ — get_success_url() is called before this runs
def form_valid(self, form):
    self.object.delete()
    return HttpResponse('')

# ✓ — bypasses success_url entirely
def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    name = str(self.object)
    self.object.delete()
    messages.error(request, f'{name} has been deleted.')
    return HttpResponse('')
```

---

### Toasts show the wrong colour or show as plain text

**Symptom:** toasts appear but are unstyled, or the wrong colour variant is applied.

**Cause 1:** `MESSAGE_TAGS` is not set in `settings.py`. `message.tags` outputs `"success"` instead of `"alert-success"`, and `class="alert success"` is not a valid DaisyUI class.

**Fix:** add to `settings.py`:
```python
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.INFO:    'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR:   'alert-error',
}
```

**Cause 2:** DaisyUI's CSS did not load. Check that the `<link>` tag for DaisyUI comes **after** the Tailwind `<script>` tag in `<head>`.

---

### Toasts do not disappear

**Symptom:** toasts stay on screen permanently.

**Cause:** the auto-dismiss script is missing or runs before the DOM is ready.

**Fix:** make sure the script is inside `base.html` and wrapped in `DOMContentLoaded`:

```html
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
```

---

### Message from a deleted car does not appear after HTMX inline delete

**Symptom:** the row disappears correctly but no toast appears.

**Cause:** HTMX inline delete returns an empty `HttpResponse('')`. There is no page load after it, so the session message is not read until the user navigates somewhere. This is expected behaviour for the inline delete pattern.

**Options:**

Option A — accept it: the toast will appear on the next page navigation.

Option B — return the toast HTML directly in the response and use HTMX `hx-swap-oob` to insert it:

```python
def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    name = str(self.object)
    self.object.delete()
    toast_html = f'''
    <div hx-swap-oob="beforeend:#toast-container">
      <div class="alert alert-error shadow-lg">
        <span>{name} has been deleted.</span>
      </div>
    </div>
    '''
    return HttpResponse(toast_html)
```

`hx-swap-oob` tells HTMX to find `#toast-container` in the existing page DOM and append the alert to it, regardless of where HTMX's primary swap target is.

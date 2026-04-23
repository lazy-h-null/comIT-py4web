---
marp: true
html: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 20px;
    padding: 36px 56px;
    color: #1a1a2e;
  }
  h1 {
    color: #16213e;
    font-size: 1.8em;
    border-bottom: 3px solid #0f9b58;
    padding-bottom: 8px;
    margin-bottom: 12px;
    margin-top: 0;
  }
  h2 {
    color: #0f9b58;
    font-size: 1.3em;
    margin-bottom: 8px;
    margin-top: 0;
  }
  p { margin: 6px 0; }
  code {
    background: #f0f4f8;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.86em;
    color: #c0392b;
  }
  pre {
    background: #1e1e2e;
    color: #cdd6f4;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.74em;
    line-height: 1.45;
    margin: 8px 0;
  }
  pre code { background: none; color: inherit; padding: 0; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84em;
  }
  th {
    background: #0f9b58;
    color: white;
    padding: 6px 10px;
    text-align: left;
  }
  td { padding: 5px 10px; border-bottom: 1px solid #e0e0e0; }
  tr:nth-child(even) td { background: #f8fffe; }
  blockquote {
    margin: 8px 0;
    padding: 6px 14px;
    border-left: 4px solid #0f9b58;
    background: #f0faf5;
    font-size: 0.88em;
  }
  section.title-slide {
    background: linear-gradient(135deg, #16213e 0%, #0f9b58 100%);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  section.title-slide h1 {
    color: white;
    border-bottom: 3px solid rgba(255,255,255,0.4);
    font-size: 2.3em;
  }
  section.title-slide p { color: rgba(255,255,255,0.85); font-size: 1.1em; }
  section.section-divider {
    background: #16213e;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.section-divider h1 { color: #0f9b58; border-color: rgba(255,255,255,0.2); }
  section.section-divider p { color: rgba(255,255,255,0.75); }
  ul { padding-left: 1.2em; margin: 6px 0; }
  li { margin-bottom: 4px; }
---

<!-- _class: title-slide -->

# 🦁 Django Zoo App
## Building a Web App from Scratch

**A beginner-friendly guide to Django + Python**

*CRUD operations · Search · Class-Based Views · Templates*

---

# What is Django?

Django is a **Python web framework** that helps you build web applications quickly without reinventing the wheel.

**Django gives you out of the box:**
- A web server to handle requests
- A database layer (no SQL needed!)
- An admin panel
- A templating engine for HTML pages
- Form handling and validation

> 💡 **Think of it like this:** Django is the blueprint + toolkit for building a house. You bring the design, it handles the foundations.

---

# Our Project — Zoo Animal Manager 🐘

We will build an app to manage animals in a zoo.

**What users can do:**

| Action | Description |
|--------|-------------|
| **Create** | Add a new animal to the zoo |
| **Read** | View a list or details of any animal |
| **Update** | Edit an animal's information |
| **Delete** | Remove an animal from the system |
| **Search** | Find animals by name, age, weight, or origin |

**Each animal has:**
`name` · `age` · `weight` · `born_in_captivity`

---

# Django's MVT Architecture

Django follows the **Model – View – Template** pattern. Every web request flows through these three layers.

<!--
  viewBox height = 220 (real content) + 60 (invisible buffer) = 280
  The transparent rect at y=220 h=60 acts as a sacrificial bottom margin
  so Marp clips the buffer instead of the diagram.
-->
<svg viewBox="0 0 780 280" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#0f9b58"/>
    </marker>
    <marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#c0392b"/>
    </marker>
  </defs>
  <!-- Browser -->
  <rect x="10" y="70" width="120" height="80" rx="10" fill="#16213e" />
  <text x="70" y="105" text-anchor="middle" fill="white" font-size="13" font-weight="bold">Browser</text>
  <text x="70" y="122" text-anchor="middle" fill="#aed6f1" font-size="11">User visits URL</text>
  <!-- Arrow 1 -->
  <line x1="130" y1="110" x2="185" y2="110" stroke="#0f9b58" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="157" y="102" text-anchor="middle" fill="#555" font-size="10">Request</text>
  <!-- URL Router -->
  <rect x="185" y="70" width="120" height="80" rx="10" fill="#0f3460" />
  <text x="245" y="100" text-anchor="middle" fill="white" font-size="13" font-weight="bold">URLs</text>
  <text x="245" y="117" text-anchor="middle" fill="#aed6f1" font-size="11">urls.py</text>
  <text x="245" y="134" text-anchor="middle" fill="#aed6f1" font-size="10">Routes request</text>
  <!-- Arrow 2 -->
  <line x1="305" y1="110" x2="360" y2="110" stroke="#0f9b58" stroke-width="2.5" marker-end="url(#arr)"/>
  <!-- View -->
  <rect x="360" y="55" width="120" height="110" rx="10" fill="#0f9b58" />
  <text x="420" y="88" text-anchor="middle" fill="white" font-size="13" font-weight="bold">View</text>
  <text x="420" y="107" text-anchor="middle" fill="white" font-size="11">views.py</text>
  <text x="420" y="124" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">Business logic</text>
  <text x="420" y="141" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">Calls Model &amp; Template</text>
  <!-- Arrow to Model -->
  <line x1="480" y1="88" x2="535" y2="60" stroke="#0f9b58" stroke-width="2" marker-end="url(#arr)"/>
  <!-- Model -->
  <rect x="535" y="20" width="120" height="75" rx="10" fill="#e67e22" />
  <text x="595" y="50" text-anchor="middle" fill="white" font-size="13" font-weight="bold">Model</text>
  <text x="595" y="68" text-anchor="middle" fill="white" font-size="11">models.py</text>
  <text x="595" y="84" text-anchor="middle" fill="rgba(255,255,255,0.85)" font-size="10">Database</text>
  <!-- Arrow to Template -->
  <line x1="480" y1="133" x2="535" y2="155" stroke="#0f9b58" stroke-width="2" marker-end="url(#arr)"/>
  <!-- Template -->
  <rect x="535" y="130" width="120" height="75" rx="10" fill="#8e44ad" />
  <text x="595" y="160" text-anchor="middle" fill="white" font-size="13" font-weight="bold">Template</text>
  <text x="595" y="178" text-anchor="middle" fill="white" font-size="11">.html files</text>
  <text x="595" y="194" text-anchor="middle" fill="rgba(255,255,255,0.85)" font-size="10">HTML output</text>
  <!-- Arrow back -->
  <line x1="595" y1="205" x2="70" y2="205" stroke="#c0392b" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr2)"/>
  <line x1="70" y1="205" x2="70" y2="155" stroke="#c0392b" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr2)"/>
  <text x="332" y="218" text-anchor="middle" fill="#c0392b" font-size="10">Response (HTML page sent back)</text>
  <!-- INVISIBLE BUFFER — extends viewBox so Marp clips this, not the diagram -->
  <rect x="0" y="220" width="780" height="60" fill="none"/>
</svg>

---

<!-- _class: section-divider -->

# ⚙️ Setting Up the Project

*From zero to a running Django app in minutes*

---

# Project Setup — Step by Step

**1 · Create a virtual environment and install Django**

```bash
mkdir zoo_project && cd zoo_project
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install django
```

**2 · Create the project and app**

```bash
django-admin startproject zoo_site .
python manage.py startapp animals
```

**3 · Register the app in `zoo_site/settings.py`**

```python
INSTALLED_APPS = [
    # ... Django's built-in apps ...
    'animals',   # ← Add this line
]
```

> 💡 An **app** is a self-contained module inside a Django **project**. One project can have many apps.

---

# Project Structure

<!--
  viewBox height = 310 (real content) + 60 (invisible buffer) = 370
-->
<svg viewBox="0 0 740 370" xmlns="http://www.w3.org/2000/svg" width="100%">
  <!-- Background -->
  <rect x="0" y="0" width="740" height="310" rx="12" fill="#1e1e2e"/>
  <!-- Left column: file tree -->
  <text x="30" y="35" font-family="monospace" font-size="13" fill="#cdd6f4">zoo_project/</text>
  <text x="30" y="58" font-family="monospace" font-size="13" fill="#89b4fa">├── manage.py</text>
  <text x="30" y="81" font-family="monospace" font-size="13" fill="#cdd6f4">├── zoo_site/</text>
  <text x="30" y="104" font-family="monospace" font-size="13" fill="#6c7086">│   ├── settings.py</text>
  <text x="30" y="127" font-family="monospace" font-size="13" fill="#6c7086">│   └── urls.py</text>
  <text x="30" y="150" font-family="monospace" font-size="13" fill="#a6e3a1">└── animals/</text>
  <text x="30" y="173" font-family="monospace" font-size="13" fill="#f38ba8">    ├── models.py</text>
  <text x="30" y="196" font-family="monospace" font-size="13" fill="#fab387">    ├── views.py</text>
  <text x="30" y="219" font-family="monospace" font-size="13" fill="#f9e2af">    ├── urls.py</text>
  <text x="30" y="242" font-family="monospace" font-size="13" fill="#89dceb">    ├── forms.py</text>
  <text x="30" y="265" font-family="monospace" font-size="13" fill="#cba6f7">    └── templates/</text>
  <text x="30" y="288" font-family="monospace" font-size="13" fill="#cba6f7">        └── animals/  ← .html files</text>
  <!-- Divider -->
  <line x1="370" y1="15" x2="370" y2="295" stroke="#45475a" stroke-width="1"/>
  <!-- Right column: legends -->
  <text x="395" y="35" font-family="sans-serif" font-size="13" fill="#89b4fa" font-weight="bold">manage.py</text>
  <text x="395" y="52" font-family="sans-serif" font-size="11" fill="#6c7086">Django command-line utility</text>
  <text x="395" y="85" font-family="sans-serif" font-size="13" fill="#f38ba8" font-weight="bold">models.py</text>
  <text x="395" y="102" font-family="sans-serif" font-size="11" fill="#6c7086">Defines Animal class → database table</text>
  <text x="395" y="135" font-family="sans-serif" font-size="13" fill="#fab387" font-weight="bold">views.py</text>
  <text x="395" y="152" font-family="sans-serif" font-size="11" fill="#6c7086">Handles requests → returns responses</text>
  <text x="395" y="185" font-family="sans-serif" font-size="13" fill="#f9e2af" font-weight="bold">urls.py</text>
  <text x="395" y="202" font-family="sans-serif" font-size="11" fill="#6c7086">Maps URLs to views</text>
  <text x="395" y="235" font-family="sans-serif" font-size="13" fill="#89dceb" font-weight="bold">forms.py</text>
  <text x="395" y="252" font-family="sans-serif" font-size="11" fill="#6c7086">Search form definition</text>
  <text x="395" y="285" font-family="sans-serif" font-size="13" fill="#cba6f7" font-weight="bold">templates/</text>
  <text x="395" y="302" font-family="sans-serif" font-size="11" fill="#6c7086">HTML files with Django tags</text>
  <!-- INVISIBLE BUFFER -->
  <rect x="0" y="310" width="740" height="60" fill="none"/>
</svg>

---

# The Animal Model

The **model** defines what data is stored in the database. Each field maps to a column.

```python
# animals/models.py
from django.db import models
from django.urls import reverse

class Animal(models.Model):
    name              = models.CharField(max_length=100)
    age               = models.IntegerField(help_text="Age in years")
    weight            = models.FloatField(help_text="Weight in kilograms")
    born_in_captivity = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']       # Always sorted A→Z

    def __str__(self):
        return f"{self.name} (age {self.age})"

    def get_absolute_url(self):
        return reverse('animals:animal-detail', kwargs={'pk': self.pk})
```

Then run:
```bash
python manage.py makemigrations animals   # creates migration file
python manage.py migrate                  # applies changes to the database
```

---

# URL Routing

URLs tell Django **which view to call** for each web address.

```python
# animals/urls.py
from django.urls import path
from . import views

app_name = 'animals'   # namespace — avoids name collisions

urlpatterns = [
    path('',                         views.HomeView.as_view(),         name='home'),
    path('animals/',                 views.AnimalListView.as_view(),   name='animal-list'),
    path('animals/<int:pk>/',        views.AnimalDetailView.as_view(), name='animal-detail'),
    path('animals/add/',             views.AnimalCreateView.as_view(), name='animal-create'),
    path('animals/<int:pk>/edit/',   views.AnimalUpdateView.as_view(), name='animal-update'),
    path('animals/<int:pk>/delete/', views.AnimalDeleteView.as_view(), name='animal-delete'),
    path('animals/search/',          views.AnimalSearchView.as_view(), name='animal-search'),
]
```

> 💡 `<int:pk>` is a **URL parameter** — it captures the animal's ID from the address bar, e.g. `/animals/3/` gives `pk=3`.

---

<!-- _class: section-divider -->

# 🧩 Generic Class-Based Views

*Django's shortcut to common web patterns*

---

# What Are Class-Based Views?

Instead of writing the same code for listing, creating, editing, and deleting objects every time, Django provides **ready-made view classes** you simply inherit from.

<!--
  viewBox height = 230 (real content) + 60 (invisible buffer) = 290
-->
<svg viewBox="0 0 720 290" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#0f9b58"/>
    </marker>
  </defs>
  <!-- Django CBV base -->
  <rect x="260" y="10" width="200" height="55" rx="10" fill="#0f9b58"/>
  <text x="360" y="37" text-anchor="middle" fill="white" font-size="14" font-weight="bold">Django Generic CBV</text>
  <text x="360" y="55" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="11">Built-in, battle-tested logic</text>
  <!-- Lines down -->
  <line x1="360" y1="65" x2="360" y2="90" stroke="#0f9b58" stroke-width="2"/>
  <line x1="80"  y1="90" x2="640" y2="90" stroke="#0f9b58" stroke-width="2"/>
  <line x1="80"  y1="90" x2="80"  y2="115" stroke="#0f9b58" stroke-width="2" marker-end="url(#a)"/>
  <line x1="220" y1="90" x2="220" y2="115" stroke="#0f9b58" stroke-width="2" marker-end="url(#a)"/>
  <line x1="360" y1="90" x2="360" y2="115" stroke="#0f9b58" stroke-width="2" marker-end="url(#a)"/>
  <line x1="500" y1="90" x2="500" y2="115" stroke="#0f9b58" stroke-width="2" marker-end="url(#a)"/>
  <line x1="640" y1="90" x2="640" y2="115" stroke="#0f9b58" stroke-width="2" marker-end="url(#a)"/>
  <!-- Child boxes -->
  <rect x="20"  y="115" width="120" height="55" rx="8" fill="#16213e"/>
  <text x="80"  y="139" text-anchor="middle" fill="#a6e3a1" font-size="12" font-weight="bold">ListView</text>
  <text x="80"  y="157" text-anchor="middle" fill="#6c7086" font-size="10">List all animals</text>
  <rect x="160" y="115" width="120" height="55" rx="8" fill="#16213e"/>
  <text x="220" y="139" text-anchor="middle" fill="#89b4fa" font-size="12" font-weight="bold">DetailView</text>
  <text x="220" y="157" text-anchor="middle" fill="#6c7086" font-size="10">One animal</text>
  <rect x="300" y="115" width="120" height="55" rx="8" fill="#16213e"/>
  <text x="360" y="139" text-anchor="middle" fill="#f38ba8" font-size="12" font-weight="bold">CreateView</text>
  <text x="360" y="157" text-anchor="middle" fill="#6c7086" font-size="10">Add animal</text>
  <rect x="440" y="115" width="120" height="55" rx="8" fill="#16213e"/>
  <text x="500" y="139" text-anchor="middle" fill="#fab387" font-size="12" font-weight="bold">UpdateView</text>
  <text x="500" y="157" text-anchor="middle" fill="#6c7086" font-size="10">Edit animal</text>
  <rect x="580" y="115" width="120" height="55" rx="8" fill="#16213e"/>
  <text x="640" y="139" text-anchor="middle" fill="#f9e2af" font-size="12" font-weight="bold">DeleteView</text>
  <text x="640" y="157" text-anchor="middle" fill="#6c7086" font-size="10">Remove animal</text>
  <!-- Footer note -->
  <text x="360" y="200" text-anchor="middle" fill="#555" font-size="12">Your code only overrides what's specific to your app ↓</text>
  <rect x="120" y="210" width="480" height="22" rx="5" fill="#f0f4f8" stroke="#0f9b58" stroke-width="1.5"/>
  <text x="360" y="225" text-anchor="middle" fill="#0f9b58" font-size="11" font-weight="bold">get_context_data() · get_queryset() · model · fields · success_url</text>
  <!-- INVISIBLE BUFFER -->
  <rect x="0" y="230" width="720" height="60" fill="none"/>
</svg>

---

# Views at a Glance

| View | URL | What it renders |
|------|-----|-----------------|
| `TemplateView` | `/` | Home page with animal counts |
| `ListView` | `/animals/` | Paginated table of all animals |
| `DetailView` | `/animals/3/` | One animal's full profile |
| `CreateView` | `/animals/add/` | Blank form to add an animal |
| `UpdateView` | `/animals/3/edit/` | Pre-filled form to edit |
| `DeleteView` | `/animals/3/delete/` | Confirmation page |
| `FormView` | `/animals/search/` | Search form + results |

Every view passes extra data to templates via **`get_context_data()`**:
```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['my_variable'] = some_value   # available in the template
    return context
```

---

# CRUD Views — Display (1/2)

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Animal

class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'   # rename object_list → animals
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Animal.objects.count()
        return context

class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_elderly'] = self.object.age > 15
        return context
```

---

# CRUD Views — Edit & Delete (2/2)

```python
class AnimalCreateView(CreateView):
    model = Animal
    fields = ['name', 'age', 'weight', 'born_in_captivity']
    template_name = 'animals/animal_form.html'
    # After saving, redirects to animal.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = 'Create'
        return context

class AnimalUpdateView(UpdateView):
    model = Animal
    fields = ['name', 'age', 'weight', 'born_in_captivity']
    template_name = 'animals/animal_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = 'Update'
        return context

class AnimalDeleteView(DeleteView):
    model = Animal
    template_name = 'animals/animal_confirm_delete.html'
    success_url = reverse_lazy('animals:animal-list')
```

---

<!-- _class: section-divider -->

# 🎨 Templates & Inheritance

*Writing HTML pages the Django way*

---

# Template Inheritance

All pages share the same navbar and footer through a **base template**. Child templates only fill in the unique content.

<!--
  viewBox height = 250 (real content) + 60 (invisible buffer) = 310
-->
<svg viewBox="0 0 700 310" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <marker id="b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#8e44ad"/>
    </marker>
  </defs>
  <!-- base.html -->
  <rect x="220" y="10" width="260" height="100" rx="10" fill="#8e44ad"/>
  <text x="350" y="38" text-anchor="middle" fill="white" font-size="14" font-weight="bold">base.html</text>
  <rect x="235" y="48" width="230" height="18" rx="4" fill="rgba(255,255,255,0.15)"/>
  <text x="350" y="61" text-anchor="middle" fill="white" font-size="11">🔵 Navbar (all pages)</text>
  <rect x="235" y="70" width="230" height="18" rx="4" fill="rgba(255,255,255,0.3)" stroke="white" stroke-dasharray="4,2" stroke-width="1.5"/>
  <text x="350" y="83" text-anchor="middle" fill="white" font-size="11">{% block content %} ← child fills this</text>
  <rect x="235" y="92" width="230" height="15" rx="4" fill="rgba(255,255,255,0.15)"/>
  <text x="350" y="103" text-anchor="middle" fill="white" font-size="10">🔵 Footer (all pages)</text>
  <!-- Lines -->
  <line x1="350" y1="110" x2="350" y2="135" stroke="#8e44ad" stroke-width="2"/>
  <line x1="100" y1="135" x2="600" y2="135" stroke="#8e44ad" stroke-width="2"/>
  <line x1="100" y1="135" x2="100" y2="155" stroke="#8e44ad" stroke-width="2" marker-end="url(#b)"/>
  <line x1="250" y1="135" x2="250" y2="155" stroke="#8e44ad" stroke-width="2" marker-end="url(#b)"/>
  <line x1="400" y1="135" x2="400" y2="155" stroke="#8e44ad" stroke-width="2" marker-end="url(#b)"/>
  <line x1="600" y1="135" x2="600" y2="155" stroke="#8e44ad" stroke-width="2" marker-end="url(#b)"/>
  <!-- Child templates -->
  <rect x="30"  y="155" width="140" height="50" rx="8" fill="#16213e"/>
  <text x="100" y="177" text-anchor="middle" fill="#a6e3a1" font-size="11" font-weight="bold">home.html</text>
  <text x="100" y="193" text-anchor="middle" fill="#6c7086" font-size="10">Welcome + stats</text>
  <rect x="180" y="155" width="140" height="50" rx="8" fill="#16213e"/>
  <text x="250" y="177" text-anchor="middle" fill="#89b4fa" font-size="11" font-weight="bold">animal_list.html</text>
  <text x="250" y="193" text-anchor="middle" fill="#6c7086" font-size="10">Table + pagination</text>
  <rect x="330" y="155" width="140" height="50" rx="8" fill="#16213e"/>
  <text x="400" y="177" text-anchor="middle" fill="#f38ba8" font-size="11" font-weight="bold">animal_form.html</text>
  <text x="400" y="193" text-anchor="middle" fill="#6c7086" font-size="10">Create &amp; Update</text>
  <rect x="530" y="155" width="140" height="50" rx="8" fill="#16213e"/>
  <text x="600" y="177" text-anchor="middle" fill="#f9e2af" font-size="11" font-weight="bold">animal_search.html</text>
  <text x="600" y="193" text-anchor="middle" fill="#6c7086" font-size="10">Form + results</text>
  <!-- Extends label -->
  <text x="350" y="240" text-anchor="middle" fill="#555" font-size="11">All child templates start with: {% extends 'animals/base.html' %}</text>
  <!-- INVISIBLE BUFFER -->
  <rect x="0" y="250" width="700" height="60" fill="none"/>
</svg>

---

# base.html — The Shared Layout

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{% block title %}Zoo App{% endblock %}</title>
</head>
<body>

<nav>
    <strong>Zoo Management</strong> |
    <a href="{% url 'animals:home' %}">Home</a> |
    <a href="{% url 'animals:animal-list' %}">All Animals</a> |
    <a href="{% url 'animals:animal-create' %}">Add Animal</a> |
    <a href="{% url 'animals:animal-search' %}">Search</a>
</nav>

<hr>
<h1>{% block heading %}{% endblock %}</h1>

{% block content %}{% endblock %}

<footer>Zoo Animal Management System</footer>
</body>
</html>
```

> 💡 `{% url 'animals:home' %}` generates the correct URL from the name — no hardcoding paths!

---

# A Child Template Example

```html
{% extends 'animals/base.html' %}

{% block title %}All Animals{% endblock %}
{% block heading %}All Animals ({{ total_count }} total){% endblock %}

{% block content %}
<table border="1">
  <thead>
    <tr><th>Name</th><th>Age</th><th>Weight</th><th>Captive?</th><th>Actions</th></tr>
  </thead>
  <tbody>
    {% for animal in animals %}
    <tr>
      <td><a href="{{ animal.get_absolute_url }}">{{ animal.name }}</a></td>
      <td>{{ animal.age }}</td>
      <td>{{ animal.weight }} kg</td>
      <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
      <td>
        <a href="{% url 'animals:animal-update' animal.pk %}">Edit</a> |
        <a href="{% url 'animals:animal-delete' animal.pk %}">Delete</a>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

> 💡 `{{ total_count }}` comes from `get_context_data()` in the view.

---

<!-- _class: section-divider -->

# 🔍 The Search Feature

*Using FormView with GET requests*

---

# How the Search Works

The search uses `FormView` with a **GET request** — results are bookmarkable, no CSRF token needed.

<!--
  viewBox height = 200 (real content) + 60 (invisible buffer) = 260
-->
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <marker id="c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#0f9b58"/>
    </marker>
  </defs>
  <!-- User -->
  <rect x="10" y="65" width="110" height="60" rx="10" fill="#16213e"/>
  <text x="65" y="92" text-anchor="middle" fill="white" font-size="13" font-weight="bold">User</text>
  <text x="65" y="109" text-anchor="middle" fill="#aed6f1" font-size="10">Fills in form</text>
  <text x="65" y="122" text-anchor="middle" fill="#aed6f1" font-size="10">clicks Search</text>
  <!-- Arrow 1 -->
  <line x1="120" y1="95" x2="175" y2="95" stroke="#0f9b58" stroke-width="2" marker-end="url(#c)"/>
  <text x="148" y="86" text-anchor="middle" fill="#555" font-size="9">GET request</text>
  <!-- get_form_kwargs -->
  <rect x="175" y="45" width="150" height="90" rx="10" fill="#0f3460"/>
  <text x="250" y="72" text-anchor="middle" fill="#89b4fa" font-size="12" font-weight="bold">get_form_kwargs()</text>
  <text x="250" y="90" text-anchor="middle" fill="#cdd6f4" font-size="10">Binds request.GET</text>
  <text x="250" y="106" text-anchor="middle" fill="#cdd6f4" font-size="10">data to the form</text>
  <text x="250" y="122" text-anchor="middle" fill="#6c7086" font-size="10">(normally only POST)</text>
  <!-- Arrow 2 -->
  <line x1="325" y1="95" x2="375" y2="95" stroke="#0f9b58" stroke-width="2" marker-end="url(#c)"/>
  <!-- get_context_data -->
  <rect x="375" y="45" width="165" height="90" rx="10" fill="#0f9b58"/>
  <text x="457" y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">get_context_data()</text>
  <text x="457" y="90" text-anchor="middle" fill="white" font-size="10">form.is_valid() → True</text>
  <text x="457" y="106" text-anchor="middle" fill="white" font-size="10">Filters queryset</text>
  <text x="457" y="122" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">Adds results to context</text>
  <!-- Arrow 3 -->
  <line x1="540" y1="95" x2="585" y2="95" stroke="#0f9b58" stroke-width="2" marker-end="url(#c)"/>
  <!-- Template -->
  <rect x="585" y="65" width="105" height="60" rx="10" fill="#8e44ad"/>
  <text x="637" y="92" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Template</text>
  <text x="637" y="109" text-anchor="middle" fill="rgba(255,255,255,0.85)" font-size="10">Shows results</text>
  <!-- URL bar note -->
  <rect x="80" y="160" width="540" height="28" rx="6" fill="#f0f4f8" stroke="#0f9b58" stroke-width="1.5"/>
  <text x="350" y="178" text-anchor="middle" fill="#16213e" font-size="11">🔗  /animals/search/?name=lion&amp;min_age=2  ← bookmarkable!</text>
  <!-- INVISIBLE BUFFER -->
  <rect x="0" y="200" width="700" height="60" fill="none"/>
</svg>

**Key trick:** override `get_form_kwargs()` to bind `request.GET`:
```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    if self.request.method == 'GET' and self.request.GET:
        kwargs['data'] = self.request.GET
    return kwargs
```

---

# Search Form & Filtering Logic

```python
# forms.py — all fields optional, any combination works
class AnimalSearchForm(forms.Form):
    name              = forms.CharField(required=False, label="Name contains")
    min_age           = forms.IntegerField(required=False, label="Min age")
    max_age           = forms.IntegerField(required=False, label="Max age")
    min_weight        = forms.FloatField(required=False,   label="Min weight (kg)")
    max_weight        = forms.FloatField(required=False,   label="Max weight (kg)")
    born_in_captivity = forms.NullBooleanField(required=False)
```

```python
# views.py — filtering inside get_context_data()
queryset = Animal.objects.all()

if data.get('name'):
    queryset = queryset.filter(name__icontains=data['name'])  # partial match
if data.get('min_age') is not None:
    queryset = queryset.filter(age__gte=data['min_age'])
if data.get('max_weight') is not None:
    queryset = queryset.filter(weight__lte=data['max_weight'])
if data.get('born_in_captivity') is not None:
    queryset = queryset.filter(born_in_captivity=data['born_in_captivity'])
```

---

<!-- _class: section-divider -->

# 🚀 Running & Key Takeaways

---

# Running the App

```bash
# Create an admin user
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Then open your browser to `http://127.0.0.1:8000/`

**Pages to visit:**

| URL | What you see |
|-----|-------------|
| `/` | Home — animal counts |
| `/animals/` | All animals (paginated) |
| `/animals/add/` | Form to add an animal |
| `/animals/1/` | Profile of animal #1 |
| `/animals/1/edit/` | Edit animal #1 |
| `/animals/1/delete/` | Confirm deletion |
| `/animals/search/` | Search by any attribute |
| `/admin/` | Django admin panel |

---

# Key Concepts Recap (1/2)

**`get_context_data()`** — inject extra variables into any template
```python
context['is_elderly'] = animal.age > 15   # use as {{ is_elderly }} in HTML
```

**`reverse_lazy()`** — safe URL generation in class-level attributes
```python
success_url = reverse_lazy('animals:animal-list')  # resolves at request time
```

**`context_object_name`** — rename the default queryset variable
```python
context_object_name = 'animals'   # template uses {{ animals }} not {{ object_list }}
```

---

# Key Concepts Recap (2/2)

**`|yesno` filter** — clean boolean display in templates
```html
{{ animal.born_in_captivity|yesno:"Yes,No" }}  →  "Yes" or "No"
```

**`{% url %}` tag** — never hardcode paths
```html
<a href="{% url 'animals:animal-detail' animal.pk %}">View</a>
```

**`paginate_by`** — automatic pagination in `ListView`
```python
paginate_by = 5   # Django splits the queryset; page_obj provided automatically
```

**`get_absolute_url()`** — canonical URL defined on the model
```python
def get_absolute_url(self):
    return reverse('animals:animal-detail', kwargs={'pk': self.pk})
# CreateView and UpdateView redirect here automatically after saving
```

---

# What You've Learned 🎉

<!--
  viewBox height = 230 (real content) + 60 (invisible buffer) = 290
-->
<svg viewBox="0 0 700 290" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <marker id="d" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#aaa"/>
    </marker>
  </defs>
  <!-- Step boxes -->
  <rect x="10"  y="20" width="120" height="75" rx="10" fill="#0f9b58"/>
  <text x="70"  y="52" text-anchor="middle" fill="white" font-size="22">🏗️</text>
  <text x="70"  y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Project Setup</text>
  <text x="70"  y="88" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">venv · startproject</text>
  <rect x="150" y="20" width="120" height="75" rx="10" fill="#e67e22"/>
  <text x="210" y="52" text-anchor="middle" fill="white" font-size="22">🗄️</text>
  <text x="210" y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Model</text>
  <text x="210" y="88" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">Fields · migrations</text>
  <rect x="290" y="20" width="120" height="75" rx="10" fill="#0f3460"/>
  <text x="350" y="52" text-anchor="middle" fill="white" font-size="22">🔗</text>
  <text x="350" y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">URL Routing</text>
  <text x="350" y="88" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">path · namespaces</text>
  <rect x="430" y="20" width="120" height="75" rx="10" fill="#8e44ad"/>
  <text x="490" y="52" text-anchor="middle" fill="white" font-size="22">🧩</text>
  <text x="490" y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">CBVs</text>
  <text x="490" y="88" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">CRUD · FormView</text>
  <rect x="570" y="20" width="120" height="75" rx="10" fill="#c0392b"/>
  <text x="630" y="52" text-anchor="middle" fill="white" font-size="22">🎨</text>
  <text x="630" y="72" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Templates</text>
  <text x="630" y="88" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="10">Inheritance · tags</text>
  <!-- Connector arrows -->
  <line x1="130" y1="57" x2="150" y2="57" stroke="#aaa" stroke-width="2" marker-end="url(#d)"/>
  <line x1="270" y1="57" x2="290" y2="57" stroke="#aaa" stroke-width="2" marker-end="url(#d)"/>
  <line x1="410" y1="57" x2="430" y2="57" stroke="#aaa" stroke-width="2" marker-end="url(#d)"/>
  <line x1="550" y1="57" x2="570" y2="57" stroke="#aaa" stroke-width="2" marker-end="url(#d)"/>
  <!-- Next steps box -->
  <rect x="10" y="120" width="680" height="100" rx="12" fill="#f0f4f8" stroke="#0f9b58" stroke-width="2"/>
  <text x="350" y="145" text-anchor="middle" fill="#16213e" font-size="13" font-weight="bold">🚀 Where to go next</text>
  <text x="55"  y="170" fill="#16213e" font-size="11">✅ Add CSS styling with Bootstrap</text>
  <text x="55"  y="192" fill="#16213e" font-size="11">✅ Add user login &amp; authentication</text>
  <text x="375" y="170" fill="#16213e" font-size="11">✅ Deploy to a server (Heroku, Railway)</text>
  <text x="375" y="192" fill="#16213e" font-size="11">✅ Add image uploads for each animal</text>
  <!-- INVISIBLE BUFFER -->
  <rect x="0" y="230" width="700" height="60" fill="none"/>
</svg>

**Official docs:** [docs.djangoproject.com](https://docs.djangoproject.com) · **Tutorial:** [djangogirls.org](https://djangogirls.org)

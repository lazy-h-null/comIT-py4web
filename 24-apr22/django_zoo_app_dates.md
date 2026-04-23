# Django Zoo Animal Management App — Complete Guide

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Setup](#2-project-setup)
3. [Project Structure](#3-project-structure)
4. [Django Settings](#4-django-settings)
5. [The Animal Model](#5-the-animal-model)
6. [URL Configuration](#6-url-configuration)
7. [Generic Class-Based Views — Reference](#7-generic-class-based-views--reference)
8. [All Views Implemented](#8-all-views-implemented)
9. [Templates](#9-templates)
10. [Running and Testing the App](#10-running-and-testing-the-app)
11. [Key Concepts Summary](#11-key-concepts-summary)

---

## 1. Project Overview

This guide walks you through building a Django application to manage animals in a zoo. The app supports full **CRUD** operations (Create, Read, Update, Delete) and **search** functionality across all animal attributes. Every page includes a navigation bar and uses plain, unstyled HTML.

### Animal Attributes

| Field               | Type           | Description                              |
|---------------------|----------------|------------------------------------------|
| `name`              | `CharField`    | The animal's name                        |
| `age`               | `IntegerField` | Age in years                             |
| `weight`            | `FloatField`   | Weight in kilograms                      |
| `born_in_captivity` | `BooleanField` | Whether the animal was born in captivity |

### Django Generic Class-Based Views Used

| View Class         | Category   | Purpose                                   |
|--------------------|------------|-------------------------------------------|
| `TemplateView`     | Display    | Home / landing page                       |
| `ListView`         | Display    | List all animals with pagination          |
| `DetailView`       | Display    | View a single animal                      |
| `CreateView`       | Editing    | Add a new animal                          |
| `UpdateView`       | Editing    | Edit an existing animal                   |
| `DeleteView`       | Editing    | Delete an animal                          |
| `FormView`         | Editing    | Search animals by attributes              |
| `RedirectView`     | Navigation | Redirect a shortcut URL to the home page  |
| `ArchiveIndexView` | Date-based | List all years that have animals          |
| `YearArchiveView`  | Date-based | List animals added in a specific year     |
| `MonthArchiveView` | Date-based | List animals added in a specific month    |
| `WeekArchiveView`  | Date-based | List animals added in a specific week     |
| `DayArchiveView`   | Date-based | List animals added on a specific day      |
| `TodayArchiveView` | Date-based | List animals added today                  |
| `DateDetailView`   | Date-based | View one animal verified by its date      |

---

## 2. Project Setup

### Step 1 — Create a Virtual Environment and Install Django

```bash
# Create a project directory
mkdir zoo_project
cd zoo_project

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install Django
pip install django
```

### Step 2 — Create the Django Project and App

```bash
# Create the Django project (named 'zoo_site')
django-admin startproject zoo_site .

# Create the Django app (named 'animals')
python manage.py startapp animals
```

> **Note:** The `.` at the end of `startproject` places `manage.py` in the current directory rather than creating a nested folder.

### Step 3 — Register the App

Open `zoo_site/settings.py` and add `'animals'` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'animals',   # <-- Add this line
]
```

---

## 3. Project Structure

After setup, your project should look like this:

```
zoo_project/
├── manage.py
├── zoo_site/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── animals/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py          ← You will create this
    ├── models.py
    ├── urls.py           ← You will create this
    ├── views.py
    ├── migrations/
    │   └── __init__.py
    └── templates/
        └── animals/
            ├── base.html                    ← Shared layout with navbar
            ├── home.html                    ← TemplateView
            ├── animal_list.html             ← ListView
            ├── animal_detail.html           ← DetailView + DateDetailView
            ├── animal_form.html             ← CreateView / UpdateView
            ├── animal_confirm_delete.html   ← DeleteView
            ├── animal_search.html           ← FormView (form + results)
            ├── animal_archive.html          ← ArchiveIndexView
            ├── animal_archive_year.html     ← YearArchiveView
            ├── animal_archive_month.html    ← MonthArchiveView
            ├── animal_archive_week.html     ← WeekArchiveView
            └── animal_archive_day.html      ← DayArchiveView / TodayArchiveView
```

---

## 4. Django Settings

In `zoo_site/settings.py`, ensure the `TEMPLATES` setting has `APP_DIRS` set to `True`. This tells Django to look for templates inside each app's `templates/` folder:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],        # You can add project-wide template dirs here
        'APP_DIRS': True,  # Looks in each app's templates/ folder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

---

## 5. The Animal Model

### `animals/models.py`

```python
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Animal(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(help_text="Age in years")
    weight = models.FloatField(help_text="Weight in kilograms")
    born_in_captivity = models.BooleanField(default=False)

    # date_added is required by all date-based archive views.
    # It records when the animal was entered into the system.
    date_added = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']   # Default queryset ordering: alphabetical by name

    def __str__(self):
        return f"{self.name} (age {self.age})"

    def get_absolute_url(self):
        # Returns the canonical URL for a single animal's detail page.
        # Django's CreateView and UpdateView redirect here after a successful save.
        return reverse('animals:animal-detail', kwargs={'pk': self.pk})
```

### Create and Apply Migrations

```bash
python manage.py makemigrations animals
python manage.py migrate
```

### Register in Admin

In `animals/admin.py`:

```python
from django.contrib import admin
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'weight', 'born_in_captivity', 'date_added']
    list_filter = ['born_in_captivity', 'date_added']
    search_fields = ['name']
```

---

## 6. URL Configuration

### Project URLs — `zoo_site/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('animals.urls', namespace='animals')),
]
```

### App URLs — `animals/urls.py`

Create this file inside the `animals/` directory:

```python
from django.urls import path
from . import views

app_name = 'animals'   # Enables URL namespacing (e.g., {% url 'animals:animal-list' %})

urlpatterns = [

    # --- RedirectView: /zoo/ redirects to the home page ---
    path('zoo/', views.ZooRedirectView.as_view(), name='zoo-redirect'),

    # --- TemplateView: Home page ---
    path('', views.HomeView.as_view(), name='home'),

    # --- ListView: All animals ---
    path('animals/', views.AnimalListView.as_view(), name='animal-list'),

    # --- DetailView: Single animal by pk ---
    path('animals/<int:pk>/', views.AnimalDetailView.as_view(), name='animal-detail'),

    # --- CreateView: Add new animal ---
    path('animals/add/', views.AnimalCreateView.as_view(), name='animal-create'),

    # --- UpdateView: Edit existing animal ---
    path('animals/<int:pk>/edit/', views.AnimalUpdateView.as_view(), name='animal-update'),

    # --- DeleteView: Delete animal ---
    path('animals/<int:pk>/delete/', views.AnimalDeleteView.as_view(), name='animal-delete'),

    # --- FormView: Search animals ---
    path('animals/search/', views.AnimalSearchView.as_view(), name='animal-search'),

    # --- ArchiveIndexView: All years that have animals ---
    path('animals/archive/', views.AnimalArchiveIndexView.as_view(), name='animal-archive-index'),

    # --- YearArchiveView: Animals added in a given year ---
    path('animals/archive/<int:year>/', views.AnimalYearArchiveView.as_view(), name='animal-year-archive'),

    # --- MonthArchiveView: Animals added in a given month (numeric month) ---
    path('animals/archive/<int:year>/<int:month>/', views.AnimalMonthArchiveView.as_view(), name='animal-month-archive'),

    # --- WeekArchiveView: Animals added in a given week ---
    path('animals/archive/<int:year>/week/<int:week>/', views.AnimalWeekArchiveView.as_view(), name='animal-week-archive'),

    # --- DayArchiveView: Animals added on a specific day ---
    path('animals/archive/<int:year>/<int:month>/<int:day>/', views.AnimalDayArchiveView.as_view(), name='animal-day-archive'),

    # --- TodayArchiveView: Animals added today (no date in URL) ---
    path('animals/archive/today/', views.AnimalTodayArchiveView.as_view(), name='animal-today-archive'),

    # --- DateDetailView: Single animal verified by date + pk ---
    path('animals/archive/<int:year>/<int:month>/<int:day>/<int:pk>/',
         views.AnimalDateDetailView.as_view(), name='animal-date-detail'),
]
```

---

## 7. Generic Class-Based Views — Reference

### Display Views

| View | What it does | Key attributes |
|------|-------------|----------------|
| `TemplateView` | Renders a fixed template with no model involved. | `template_name` |
| `ListView` | Queries a model and passes a list to the template as `object_list` or `<model>_list`. | `model`, `paginate_by`, `queryset` |
| `DetailView` | Looks up one object by `pk` and passes it as `object` or `<model>`. | `model` |

### Editing Views

| View | What it does | Key attributes |
|------|-------------|----------------|
| `CreateView` | Displays a blank form, validates it, and saves a new object. | `model`, `fields` |
| `UpdateView` | Displays a pre-filled form for an existing object and saves changes. | `model`, `fields` |
| `DeleteView` | Displays a confirmation page and deletes the object on POST. | `model`, `success_url` |
| `FormView` | Displays any form and processes its submission. Not tied to a model. | `form_class`, `template_name` |

### Navigation View

| View | What it does | Key attributes |
|------|-------------|----------------|
| `RedirectView` | Issues an HTTP redirect without rendering a template. | `pattern_name`, `permanent` |

### Date-Based Views

All date-based views share two required class attributes: `model` and `date_field` (the name of the `DateField` on the model to filter by). They also all accept `allow_empty = True` to return an empty page instead of a 404 when no records exist for that period.

| View | What it does | Key automatic context variables |
|------|-------------|--------------------------------|
| `ArchiveIndexView` | Lists all objects grouped by year. | `date_list` (years with data), `object_list` |
| `YearArchiveView` | Lists objects and months for a given year. | `year`, `date_list` (months), `object_list` |
| `MonthArchiveView` | Lists all objects for a given year + month. | `month`, `object_list` |
| `WeekArchiveView` | Lists all objects for a given year + week. | `week`, `object_list` |
| `DayArchiveView` | Lists all objects for a given year + month + day. | `day`, `object_list` |
| `TodayArchiveView` | Same as `DayArchiveView` but always uses today's date. | `day`, `object_list` |
| `DateDetailView` | Retrieves a single object by date + pk. Prevents URL guessing. | `object` |

### Adding Extra Context

All CBVs support `get_context_data()`, which you override to inject additional variables into the template:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['my_extra_variable'] = some_value
    return context
```

These extra variables are then available in templates as `{{ my_extra_variable }}`.

---

## 8. All Views Implemented

### `animals/forms.py`

Create this file to define the search form used by `FormView`:

```python
from django import forms


class AnimalSearchForm(forms.Form):
    """
    A form for searching animals by any of their attributes.
    All fields are optional so users can search by one or more criteria.
    """
    name = forms.CharField(
        required=False,
        label="Name contains",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Lion'})
    )
    min_age = forms.IntegerField(
        required=False,
        label="Minimum age",
        min_value=0
    )
    max_age = forms.IntegerField(
        required=False,
        label="Maximum age",
        min_value=0
    )
    min_weight = forms.FloatField(
        required=False,
        label="Minimum weight (kg)",
        min_value=0
    )
    max_weight = forms.FloatField(
        required=False,
        label="Maximum weight (kg)",
        min_value=0
    )
    born_in_captivity = forms.NullBooleanField(
        required=False,
        label="Born in captivity",
        widget=forms.Select(choices=[
            ('', 'Any'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
```

### `animals/views.py`

```python
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView,
    CreateView, UpdateView, DeleteView,
    FormView, RedirectView,
)
from django.views.generic.dates import (
    ArchiveIndexView, YearArchiveView, MonthArchiveView,
    WeekArchiveView, DayArchiveView, TodayArchiveView,
    DateDetailView,
)

from .models import Animal
from .forms import AnimalSearchForm


# ---------------------------------------------------------------------------
# RedirectView — /zoo/ redirects to the home page
# ---------------------------------------------------------------------------
class ZooRedirectView(RedirectView):
    """
    RedirectView issues an HTTP redirect without rendering any template.
    'permanent=False' sends a 302 (temporary) redirect.
    'pattern_name' resolves the destination by named URL instead of a
    hard-coded string, so it stays correct if the URL ever changes.
    """
    permanent = False
    pattern_name = 'animals:home'


# ---------------------------------------------------------------------------
# TemplateView — Home / landing page
# ---------------------------------------------------------------------------
class HomeView(TemplateView):
    """
    TemplateView renders a fixed template with no model involved.
    We override get_context_data() to inject extra variables:
      - page_title: used in the <title> tag and heading
      - total_animals: total count of animals in the zoo
      - captive_count: how many were born in captivity
      - wild_count: how many were born in the wild
    """
    template_name = 'animals/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Welcome to the Zoo'
        context['total_animals'] = Animal.objects.count()
        context['captive_count'] = Animal.objects.filter(born_in_captivity=True).count()
        context['wild_count'] = Animal.objects.filter(born_in_captivity=False).count()
        return context


# ---------------------------------------------------------------------------
# ListView — All animals
# ---------------------------------------------------------------------------
class AnimalListView(ListView):
    """
    ListView queries all Animal objects and passes them to the template.
    context_object_name renames the default 'object_list' to 'animals'.
    paginate_by splits results into pages; Django automatically provides
    the 'page_obj' and 'paginator' variables for building pagination links.

    Extra context added:
      - page_title: for the browser tab and heading
      - total_count: total number of animals across all pages
    """
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 5

    def get_queryset(self):
        return Animal.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'All Animals'
        context['total_count'] = Animal.objects.count()
        return context


# ---------------------------------------------------------------------------
# DetailView — Single animal
# ---------------------------------------------------------------------------
class AnimalDetailView(DetailView):
    """
    DetailView looks up a single Animal by its pk (from the URL) and
    passes it to the template as 'animal' (context_object_name).

    Extra context added:
      - page_title: uses the animal's name
      - is_elderly: True if the animal is over 15 years old
      - weight_category: a human-readable size label derived from weight
    """
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.get_object()
        context['page_title'] = f'Animal: {animal.name}'
        context['is_elderly'] = animal.age > 15
        context['weight_category'] = self._weight_category(animal.weight)
        return context

    @staticmethod
    def _weight_category(weight):
        """Returns a human-readable weight category label."""
        if weight < 10:
            return 'Small'
        elif weight < 100:
            return 'Medium'
        elif weight < 500:
            return 'Large'
        return 'Very Large'


# ---------------------------------------------------------------------------
# CreateView — Add a new animal
# ---------------------------------------------------------------------------
class AnimalCreateView(CreateView):
    """
    CreateView displays a blank ModelForm for Animal, validates it on POST,
    and saves a new instance. After saving it redirects to the URL returned
    by Animal.get_absolute_url() (no success_url needed when that is defined).

    Extra context added:
      - page_title: shown in the heading
      - form_action: tells the shared template this is a Create operation
    """
    model = Animal
    fields = ['name', 'age', 'weight', 'born_in_captivity', 'date_added']
    template_name = 'animals/animal_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New Animal'
        context['form_action'] = 'Create'
        return context


# ---------------------------------------------------------------------------
# UpdateView — Edit an existing animal
# ---------------------------------------------------------------------------
class AnimalUpdateView(UpdateView):
    """
    UpdateView is identical to CreateView but pre-fills the form with the
    existing Animal data (looked up by pk from the URL).

    Extra context added:
      - page_title: includes the animal's current name
      - form_action: tells the shared template this is an Update operation
    """
    model = Animal
    fields = ['name', 'age', 'weight', 'born_in_captivity', 'date_added']
    template_name = 'animals/animal_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit: {self.object.name}'
        context['form_action'] = 'Update'
        return context


# ---------------------------------------------------------------------------
# DeleteView — Delete an animal
# ---------------------------------------------------------------------------
class AnimalDeleteView(DeleteView):
    """
    DeleteView shows a confirmation page on GET, then deletes the object
    and redirects to success_url on POST.

    reverse_lazy() is used instead of reverse() because Python evaluates
    class bodies at import time — before the URL configuration is loaded.

    Extra context added:
      - page_title: warns the user which animal they are about to delete
    """
    model = Animal
    template_name = 'animals/animal_confirm_delete.html'
    success_url = reverse_lazy('animals:animal-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete: {self.object.name}'
        return context


# ---------------------------------------------------------------------------
# FormView — Search animals
# ---------------------------------------------------------------------------
class AnimalSearchView(FormView):
    """
    FormView for searching animals. Uses GET so results are bookmarkable
    and no CSRF token is needed.

    The key challenge: FormView only binds form data on POST by default.
    We override get_form_kwargs() to also bind GET params, which makes the
    form validate when the user submits the search via GET.

    All search logic lives in get_context_data() so it runs on every request.

    Extra context added:
      - page_title: describes the page
      - results: the QuerySet of matching animals (after form submission)
      - result_count: number of matches
      - search_performed: boolean flag so the template knows to show results
    """
    template_name = 'animals/animal_search.html'
    form_class = AnimalSearchForm

    def get_form_kwargs(self):
        """
        By default, FormView only binds form data on POST.
        This override also binds GET params so the form validates on GET.
        Without this, the form is always unbound on GET and is_valid()
        never returns True, so no search ever runs.
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET' and self.request.GET:
            kwargs['data'] = self.request.GET
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Search Animals'
        context['results'] = None
        context['search_performed'] = False

        form = context['form']
        # Only run the search if GET params are present and the form is valid
        if self.request.GET and form.is_valid():
            data = form.cleaned_data
            queryset = Animal.objects.all()

            # Filter by name (case-insensitive partial match)
            if data.get('name'):
                queryset = queryset.filter(name__icontains=data['name'])

            # Filter by age range
            if data.get('min_age') is not None:
                queryset = queryset.filter(age__gte=data['min_age'])
            if data.get('max_age') is not None:
                queryset = queryset.filter(age__lte=data['max_age'])

            # Filter by weight range
            if data.get('min_weight') is not None:
                queryset = queryset.filter(weight__gte=data['min_weight'])
            if data.get('max_weight') is not None:
                queryset = queryset.filter(weight__lte=data['max_weight'])

            # Filter by born_in_captivity
            if data.get('born_in_captivity') is not None:
                queryset = queryset.filter(born_in_captivity=data['born_in_captivity'])

            context['results'] = queryset
            context['result_count'] = queryset.count()
            context['search_performed'] = True

        return context


# ---------------------------------------------------------------------------
# ArchiveIndexView — All years that have animals
# ---------------------------------------------------------------------------
class AnimalArchiveIndexView(ArchiveIndexView):
    """
    ArchiveIndexView groups all objects by the date_field and provides
    'date_list' in the context: a queryset of distinct years that have
    at least one record. allow_empty=True returns an empty page instead
    of a 404 when no animals exist yet.

    Extra context added:
      - page_title
      - total_years: how many distinct years have animals
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive.html'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Animal Archive'
        context['total_years'] = len(context.get('date_list') or [])
        return context


# ---------------------------------------------------------------------------
# YearArchiveView — Animals added in a specific year
# ---------------------------------------------------------------------------
class AnimalYearArchiveView(YearArchiveView):
    """
    YearArchiveView filters objects whose date_field falls in the given year,
    captured from the URL (e.g. /archive/2024/).
    make_object_list=True puts the actual Animal objects (not just month
    dates) into 'object_list' so we can display them in the template.

    Extra context added:
      - page_title: includes the year
      - animal_count: number of animals added that year
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive_year.html'
    make_object_list = True
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Animals Added in {self.get_year()}"
        context['animal_count'] = len(context.get('object_list') or [])
        return context


# ---------------------------------------------------------------------------
# MonthArchiveView — Animals added in a specific month
# ---------------------------------------------------------------------------
class AnimalMonthArchiveView(MonthArchiveView):
    """
    MonthArchiveView filters by year + month from the URL (e.g. /archive/2024/3/).
    month_format='%m' allows numeric months instead of the default '%b' (Jan).

    Extra context added:
      - page_title: includes the month name and year
      - animal_count: number of animals added that month
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive_month.html'
    month_format = '%m'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month_name = context['month'].strftime('%B')   # e.g. "March"
        context['page_title'] = f"Animals Added in {month_name} {self.get_year()}"
        context['animal_count'] = context['object_list'].count()
        return context


# ---------------------------------------------------------------------------
# WeekArchiveView — Animals added in a specific week
# ---------------------------------------------------------------------------
class AnimalWeekArchiveView(WeekArchiveView):
    """
    WeekArchiveView filters by year + week number from the URL
    (e.g. /archive/2024/week/12/).
    week_format='%W' uses Monday-based week numbers (0–53).

    Extra context added:
      - page_title: includes the week number and year
      - animal_count: number of animals added that week
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive_week.html'
    week_format = '%W'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Animals Added in Week {self.get_week()}, {self.get_year()}"
        context['animal_count'] = context['object_list'].count()
        return context


# ---------------------------------------------------------------------------
# DayArchiveView — Animals added on a specific day
# ---------------------------------------------------------------------------
class AnimalDayArchiveView(DayArchiveView):
    """
    DayArchiveView filters by year + month + day from the URL
    (e.g. /archive/2024/3/15/).

    Extra context added:
      - page_title: includes the full formatted date
      - animal_count: number of animals added on that day
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive_day.html'
    month_format = '%m'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Animals Added on {context['day'].strftime('%B %d, %Y')}"
        context['animal_count'] = context['object_list'].count()
        return context


# ---------------------------------------------------------------------------
# TodayArchiveView — Animals added today
# ---------------------------------------------------------------------------
class AnimalTodayArchiveView(TodayArchiveView):
    """
    TodayArchiveView works exactly like DayArchiveView but automatically
    uses today's date — no date segments are needed in the URL (/archive/today/).
    It reuses the same day template since the context variables are identical.

    Extra context added:
      - page_title: says "Today"
      - animal_count: number of animals added today
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_archive_day.html'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Animals Added Today'
        context['animal_count'] = context['object_list'].count()
        return context


# ---------------------------------------------------------------------------
# DateDetailView — Single animal verified by date + pk
# ---------------------------------------------------------------------------
class AnimalDateDetailView(DateDetailView):
    """
    DateDetailView retrieves a single object using both its pk AND the
    date_field value embedded in the URL. This prevents URL enumeration:
    the date in the URL must match the animal's actual date_added or
    Django returns a 404.

    URL example: /archive/2024/3/15/7/

    It reuses animal_detail.html since it passes the same context variables
    as DetailView ('animal', 'is_elderly', 'weight_category').

    Extra context added:
      - page_title: includes the animal's name
      - is_elderly: derived boolean (same as DetailView)
      - weight_category: derived label (same as DetailView)
    """
    model = Animal
    date_field = 'date_added'
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
    month_format = '%m'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.get_object()
        context['page_title'] = f'Animal: {animal.name} (Archive)'
        context['is_elderly'] = animal.age > 15
        context['weight_category'] = AnimalDetailView._weight_category(animal.weight)
        return context
```

---

## 9. Templates

### `animals/templates/animals/base.html` — Shared Layout with Navigation Bar

Every other template extends this file. The `{% block %}` tags define regions that child templates can override.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Zoo App{% endblock %}</title>
</head>
<body>

<nav>
    <strong>Zoo Management</strong> |
    <a href="{% url 'animals:home' %}">Home</a> |
    <a href="{% url 'animals:animal-list' %}">All Animals</a> |
    <a href="{% url 'animals:animal-create' %}">Add Animal</a> |
    <a href="{% url 'animals:animal-search' %}">Search</a> |
    <a href="{% url 'animals:animal-archive-index' %}">Archive</a> |
    <a href="{% url 'animals:animal-today-archive' %}">Added Today</a>
</nav>

<hr>

<h1>{% block heading %}{% endblock %}</h1>

{% block content %}{% endblock %}

<hr>
<footer>Zoo Animal Management System</footer>

</body>
</html>
```

> **How template inheritance works:** Child templates use `{% extends 'animals/base.html' %}` and fill in named blocks. Everything outside a block in the child is ignored.

---

### `animals/templates/animals/home.html` — TemplateView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{# page_title, total_animals, captive_count, wild_count come from HomeView.get_context_data() #}
<p>Welcome to the Zoo Animal Management System.</p>

<p>
    The zoo currently has <strong>{{ total_animals }}</strong> animal(s) on record.
    Of these, <strong>{{ captive_count }}</strong> were born in captivity and
    <strong>{{ wild_count }}</strong> were born in the wild.
</p>

<ul>
    <li><a href="{% url 'animals:animal-list' %}">Browse all animals</a></li>
    <li><a href="{% url 'animals:animal-create' %}">Add a new animal</a></li>
    <li><a href="{% url 'animals:animal-search' %}">Search animals</a></li>
    <li><a href="{% url 'animals:animal-archive-index' %}">Browse archive by date</a></li>
    <li><a href="{% url 'animals:animal-today-archive' %}">Animals added today</a></li>
</ul>
{% endblock %}
```

---

### `animals/templates/animals/animal_list.html` — ListView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }} ({{ total_count }} total){% endblock %}

{% block content %}
{# 'animals' = context_object_name; 'total_count' and 'page_title' from get_context_data() #}

{% if animals %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age (years)</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Date Added</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in animals %}
        <tr>
            <td><a href="{{ animal.get_absolute_url }}">{{ animal.name }}</a></td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td>{{ animal.date_added }}</td>
            <td>
                <a href="{% url 'animals:animal-update' animal.pk %}">Edit</a> |
                <a href="{% url 'animals:animal-delete' animal.pk %}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

{# Pagination — paginator and page_obj are provided automatically by ListView #}
<p>
    Page {{ page_obj.number }} of {{ paginator.num_pages }}
    {% if page_obj.has_previous %}
        | <a href="?page={{ page_obj.previous_page_number }}">Previous</a>
    {% endif %}
    {% if page_obj.has_next %}
        | <a href="?page={{ page_obj.next_page_number }}">Next</a>
    {% endif %}
</p>

{% else %}
<p>No animals found.</p>
{% endif %}

{% endblock %}
```

---

### `animals/templates/animals/animal_detail.html` — DetailView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{# 'animal' = context_object_name from DetailView #}
{# 'is_elderly' and 'weight_category' are extra variables from get_context_data() #}

<table border="1">
    <tr><th>Name</th><td>{{ animal.name }}</td></tr>
    <tr>
        <th>Age</th>
        <td>{{ animal.age }} year(s) {% if is_elderly %}<em>(Elderly animal)</em>{% endif %}</td>
    </tr>
    <tr><th>Weight</th><td>{{ animal.weight }} kg ({{ weight_category }})</td></tr>
    <tr><th>Born in Captivity</th><td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td></tr>
    <tr><th>Date Added</th><td>{{ animal.date_added }}</td></tr>
</table>

<p>
    <a href="{% url 'animals:animal-update' animal.pk %}">Edit this animal</a> |
    <a href="{% url 'animals:animal-delete' animal.pk %}">Delete this animal</a> |
    <a href="{% url 'animals:animal-list' %}">Back to list</a> |
    <a href="{% url 'animals:animal-archive-index' %}">Archive</a>
</p>
{% endblock %}
```

---

### `animals/templates/animals/animal_form.html` — CreateView / UpdateView

This single template is shared by both `AnimalCreateView` and `AnimalUpdateView`. The `form_action` extra context variable ("Create" or "Update") differentiates the heading and button label.

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{# 'form' is provided automatically by CreateView/UpdateView #}
{# 'form_action' and 'page_title' are extra variables from get_context_data() #}

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">{{ form_action }} Animal</button>
</form>

<p><a href="{% url 'animals:animal-list' %}">Cancel — Back to list</a></p>
{% endblock %}
```

---

### `animals/templates/animals/animal_confirm_delete.html` — DeleteView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{# 'object' is the Animal instance provided automatically by DeleteView #}

<p>Are you sure you want to permanently delete <strong>{{ object.name }}</strong>?</p>
<p>This action cannot be undone.</p>

<form method="post">
    {% csrf_token %}
    <button type="submit">Yes, Delete</button>
    <a href="{{ object.get_absolute_url }}">Cancel</a>
</form>
{% endblock %}
```

---

### `animals/templates/animals/animal_search.html` — FormView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{# 'form' is the AnimalSearchForm provided by FormView #}
{# 'results', 'result_count', 'search_performed' are extra variables from get_context_data() #}

{# method="get" so results are bookmarkable and no CSRF token is needed #}
<form method="get">
    {{ form.as_p }}
    <button type="submit">Search</button>
</form>

{% if search_performed %}
<hr>
<h2>Results ({{ result_count }} found)</h2>

{% if results %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Details</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in results %}
        <tr>
            <td>{{ animal.name }}</td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td><a href="{{ animal.get_absolute_url }}">View</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>No animals matched your search criteria.</p>
{% endif %}
{% endif %}

{% endblock %}
```

---

### `animals/templates/animals/animal_archive.html` — ArchiveIndexView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }}{% endblock %}

{% block content %}
{#
  Automatic context from ArchiveIndexView:
    date_list  — queryset of years (as datetime objects) that have animals
    object_list — all Animal objects (latest first)
  Extra context from get_context_data():
    total_years — count of distinct years
#}

<p>The archive spans <strong>{{ total_years }}</strong> year(s).</p>

{% if date_list %}
<ul>
    {% for year in date_list %}
    <li>
        <a href="{% url 'animals:animal-year-archive' year.year %}">
            {{ year.year }}
        </a>
    </li>
    {% endfor %}
</ul>
{% else %}
<p>No animals have been added yet.</p>
{% endif %}

{% endblock %}
```

---

### `animals/templates/animals/animal_archive_year.html` — YearArchiveView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }} — {{ animal_count }} animal(s){% endblock %}

{% block content %}
{#
  Automatic context from YearArchiveView:
    year        — the year as a datetime object
    date_list   — queryset of months (datetime objects) that have animals
    object_list — all Animal objects added that year (because make_object_list=True)
  Extra context from get_context_data():
    animal_count — total animals added this year
#}

<h2>Browse by month</h2>
{% if date_list %}
<ul>
    {% for month in date_list %}
    <li>
        <a href="{% url 'animals:animal-month-archive' year.year month.month %}">
            {{ month|date:"F" }}
        </a>
    </li>
    {% endfor %}
</ul>
{% else %}
<p>No months on record for this year.</p>
{% endif %}

<h2>All Animals Added in {{ year.year }}</h2>
{% if object_list %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Date Added</th>
            <th>Details</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in object_list %}
        <tr>
            <td>{{ animal.name }}</td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td>{{ animal.date_added }}</td>
            <td><a href="{{ animal.get_absolute_url }}">View</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>No animals were added in {{ year.year }}.</p>
{% endif %}

<p><a href="{% url 'animals:animal-archive-index' %}">Back to archive index</a></p>

{% endblock %}
```

---

### `animals/templates/animals/animal_archive_month.html` — MonthArchiveView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }} — {{ animal_count }} animal(s){% endblock %}

{% block content %}
{#
  Automatic context from MonthArchiveView:
    month       — the month as a datetime object
    object_list — all Animal objects added that month
  Extra context from get_context_data():
    animal_count — total animals added this month
#}

{% if object_list %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Date Added</th>
            <th>Details</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in object_list %}
        <tr>
            <td>{{ animal.name }}</td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td>{{ animal.date_added }}</td>
            <td>
                <a href="{% url 'animals:animal-date-detail' animal.date_added.year animal.date_added.month animal.date_added.day animal.pk %}">
                    View
                </a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>No animals were added during this month.</p>
{% endif %}

<p>
    <a href="{% url 'animals:animal-year-archive' month.year %}">
        Back to {{ month.year }} archive
    </a> |
    <a href="{% url 'animals:animal-archive-index' %}">Archive index</a>
</p>

{% endblock %}
```

---

### `animals/templates/animals/animal_archive_week.html` — WeekArchiveView

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }} — {{ animal_count }} animal(s){% endblock %}

{% block content %}
{#
  Automatic context from WeekArchiveView:
    week        — the start date of the week as a datetime object
    object_list — all Animal objects added during that week
  Extra context from get_context_data():
    animal_count — total animals added this week
#}

{% if object_list %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Date Added</th>
            <th>Details</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in object_list %}
        <tr>
            <td>{{ animal.name }}</td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td>{{ animal.date_added }}</td>
            <td><a href="{{ animal.get_absolute_url }}">View</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>No animals were added during this week.</p>
{% endif %}

<p>
    Week starting {{ week|date:"N j, Y" }} |
    <a href="{% url 'animals:animal-archive-index' %}">Archive index</a>
</p>

{% endblock %}
```

---

### `animals/templates/animals/animal_archive_day.html` — DayArchiveView / TodayArchiveView

This single template is shared by both `DayArchiveView` and `TodayArchiveView` since both provide identical context variables.

```html
{% extends 'animals/base.html' %}

{% block title %}{{ page_title }}{% endblock %}
{% block heading %}{{ page_title }} — {{ animal_count }} animal(s){% endblock %}

{% block content %}
{#
  Automatic context from DayArchiveView / TodayArchiveView:
    day         — the date as a datetime object
    object_list — all Animal objects added on that day
  Extra context from get_context_data():
    animal_count — total animals added on this day
#}

{% if object_list %}
<table border="1">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Weight (kg)</th>
            <th>Born in Captivity</th>
            <th>Details</th>
        </tr>
    </thead>
    <tbody>
        {% for animal in object_list %}
        <tr>
            <td>{{ animal.name }}</td>
            <td>{{ animal.age }}</td>
            <td>{{ animal.weight }}</td>
            <td>{{ animal.born_in_captivity|yesno:"Yes,No" }}</td>
            <td>
                <a href="{% url 'animals:animal-date-detail' day.year day.month day.day animal.pk %}">
                    View (date-verified)
                </a> |
                <a href="{{ animal.get_absolute_url }}">View</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>No animals were added on {{ day|date:"N j, Y" }}.</p>
{% endif %}

<p>
    <a href="{% url 'animals:animal-month-archive' day.year day.month %}">
        Back to {{ day|date:"F Y" }}
    </a> |
    <a href="{% url 'animals:animal-archive-index' %}">Archive index</a>
</p>

{% endblock %}
```

---

## 10. Running and Testing the App

### Create a Superuser (for Admin)

```bash
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### Key URLs to Test

| URL | View | What to test |
|-----|------|-------------|
| `/` | HomeView | Animal counts |
| `/zoo/` | ZooRedirectView | Should redirect to `/` |
| `/animals/` | AnimalListView | Paginated table with date column |
| `/animals/add/` | AnimalCreateView | Create form including date_added |
| `/animals/1/` | AnimalDetailView | Detail with is_elderly and weight_category |
| `/animals/1/edit/` | AnimalUpdateView | Edit form pre-filled |
| `/animals/1/delete/` | AnimalDeleteView | Confirmation page |
| `/animals/search/` | AnimalSearchView | Search by any attribute |
| `/animals/archive/` | ArchiveIndexView | List of years |
| `/animals/archive/2024/` | YearArchiveView | Animals in 2024, browseable by month |
| `/animals/archive/2024/3/` | MonthArchiveView | Animals in March 2024 |
| `/animals/archive/2024/week/12/` | WeekArchiveView | Animals in week 12 of 2024 |
| `/animals/archive/2024/3/15/` | DayArchiveView | Animals added on Mar 15 2024 |
| `/animals/archive/today/` | TodayArchiveView | Animals added today |
| `/animals/archive/2024/3/15/1/` | DateDetailView | Animal #1 verified by date |

### Add Sample Data via Admin

```
http://127.0.0.1:8000/admin/
```

Login with your superuser credentials and add several Animal objects with **different `date_added` values** (spread across multiple years, months, and days) so you can fully exercise all the archive views.

---

## 11. Key Concepts Summary

### Why Generic Class-Based Views?

Django's generic CBVs eliminate boilerplate. Instead of writing the same queryset lookup, pagination logic, and form handling in every view, you inherit from a generic class and only override what is specific to your use case.

### Why `get_context_data()`?

Every CBV calls `get_context_data()` to build the dictionary passed to the template. By calling `super().get_context_data(**kwargs)` first, you get all the automatic variables (like `object_list`, `form`, `page_obj`, `date_list`) and then simply add your own keys on top.

### Why `reverse_lazy()`?

`reverse_lazy()` is used in class-level attributes (like `success_url`) because Python evaluates class bodies at import time — before the URL configuration is loaded. `reverse_lazy()` defers the URL lookup until the first actual request.

### Why `date_added` on the Model?

All date-based archive views (`ArchiveIndexView`, `YearArchiveView`, etc.) require a `DateField` or `DateTimeField` to filter against. The `date_field` class attribute on each view tells Django which field to use. Without it, the archive views cannot function. `date_added` also serves as a useful audit field showing when each animal entered the system.

### Why does `DateDetailView` need both a date and a pk?

`DateDetailView` requires both the date URL segments and the pk to retrieve an object. This prevents URL enumeration attacks: a visitor cannot simply guess `/animals/archive/1999/1/1/999/` and retrieve any arbitrary record — the date in the URL must match the object's actual `date_added`. If it does not match, Django returns a 404.

### Why does `TodayArchiveView` reuse the day template?

`TodayArchiveView` is a subclass of `DayArchiveView` and provides the exact same context variables (`day`, `object_list`). Reusing `animal_archive_day.html` for both keeps the codebase DRY — there is no duplication between the two.

### Why `pattern_name` in `RedirectView`?

Using `pattern_name = 'animals:home'` instead of a hard-coded `url = '/'` means the redirect destination is always in sync with the URL configuration. If you ever change the home page URL, the redirect updates automatically.

### How Template Inheritance Works

```
base.html                 — defines {% block %} placeholders and the shared navbar/footer
  ├── home.html           — TemplateView
  ├── animal_list.html    — ListView
  ├── animal_detail.html  — DetailView + DateDetailView
  ├── animal_form.html    — CreateView + UpdateView
  ├── animal_confirm_delete.html — DeleteView
  ├── animal_search.html  — FormView
  ├── animal_archive.html — ArchiveIndexView
  ├── animal_archive_year.html  — YearArchiveView
  ├── animal_archive_month.html — MonthArchiveView
  ├── animal_archive_week.html  — WeekArchiveView
  └── animal_archive_day.html   — DayArchiveView + TodayArchiveView
```

Child templates only provide content for the blocks they need. Everything else is inherited from the parent.

### The `yesno` Template Filter

`{{ animal.born_in_captivity|yesno:"Yes,No" }}` converts a boolean into a human-readable string — one of Django's built-in template filters. It avoids writing `{% if %}{% else %}{% endif %}` blocks for simple boolean display.

# Stattic pages with templates and static files

Create 4 webpages with templates (4 + 1 base template)

Submit repo with markdown file with blocks of code for: 
* views.py
* urls.py
* settings.py (All modified sections only)

Include screenshots for every page.

Use only render, for every page add any of these data  in the main block (include name and values for every element using the context dictionary, use loop for iterables):

* 3 variables with different data types
* a list of mixed data types of length 6
* a dictionary with string keys and different data types of length 5



## Example
### code

config/settings.py
```Python
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'static_pages_templates', # added 
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'], # modified
        'APP_DIRS': True,
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

STATIC_URL = '/static/' # modified

STATICFILES_DIRS = [   # added
    BASE_DIR / "static",
]
```

config/urls.py
```Python
from django.contrib import admin
from django.urls import path
from static_pages_templates import views

urlpatterns = [
    path('', views.home, name="home"),
    path('contact/', views.contact, name="contact"),
]
```

templates/static_page_templates/base.html
```HTML
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My cool website with templates {% endblock %}</title>
    <link rel="stylesheet" href="{% static 'static_pages_templates/css/daisyui.css'%}" type="text/css">
    <script src="{% static 'static_pages_templates/js/tailwindcss.js'%}"></script>
    <link rel="stylesheet" href="{% static 'static_pages_templates/css/themes.css'%}" type="text/css">
</head>
<body>
    <header>
        <div class="navbar bg-base-100 shadow-sm">
            
                <a class="btn btn-ghost text-xl" href="/">Home</a>
                <a class="btn btn-ghost text-xl" href="/contact/">Contact</a>
            
        </div>

        
    </header>
    <h1 class="text-4xl font-bold text-primary">{% block h1 %}{% endblock %}</h1>
    <h2 class="text-2xl font-semibold text-neutral">{% block h2 %}{% endblock %}</h2>
    <p class="py-4 text-base-content">{%block p %} {% endblock %}</p>
    <main>
        {% block main %}{% endblock %}
    </main>

</body>
</html>
```

templates/static_page_templates/home.html
```HTML
{% extends 'static_pages_templates/base.html' %}
{% load static %}

{% block title %}My Cool Website{% endblock %}

{% block h1 %}My Cool Website{% endblock %}
{% block h2 %}Come and see{% endblock %}
{% block p %}Explore at your own risk{% endblock %}

{% block main %}

<ol>
    <li>Name: {{ name }}</li>
    <li> Age: {{ age }} </li>
    <li>Gains: {{ gains }}</li>
</ol>

{% endblock %}
```

static_pages_templates/views.py

```Python
from django.shortcuts import render

# Create your views here.

def home(request):
    ctx = {
        'name': "Tony",
        'age': 25,
        'gains': 2344.322211
    }
    return render(request, 'static_pages_templates/home.html', ctx)

def contact(request):
    return render(request, 'static_pages_templates/contact.html')

```

### Rendering

home
![Home page](home2.png)

contact
![Contact](contact2.png)

# Building a Django HR Management Dashboard with HTMX

A complete guide to building a full-CRUD Human Resources dashboard modeled after a large tech company (Alphabet Inc.) hierarchy — no CSS styling, HTMX for all HTTP interactions, and Django's ORM for hierarchical employee data.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Setup](#2-project-setup)
3. [App Structure](#3-app-structure)
4. [Models](#4-models)
5. [Database Migrations](#5-database-migrations)
6. [Fake Data Seed Script](#6-fake-data-seed-script)
7. [Forms](#7-forms)
8. [Views](#8-views)
9. [URL Configuration](#9-url-configuration)
10. [Templates](#10-templates)
11. [HTMX & CSRF Setup](#11-htmx--csrf-setup)
12. [Running the Project](#12-running-the-project)

---

## 1. Prerequisites

- Python 3.11+
- pip
- virtualenv (recommended)

```bash
pip install django faker
```

---

## 2. Project Setup

```bash
django-admin startproject hrms_project
cd hrms_project
python manage.py startapp hrms
```

Add `hrms` to `INSTALLED_APPS` in `hrms_project/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'hrms',
]
```

Download HTMX (no CDN, keep it local or use a CDN link in base template — see Section 10).

---

## 3. App Structure

```
hrms_project/
├── hrms_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── hrms/
│   ├── migrations/
│   ├── templates/
│   │   └── hrms/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── employees/
│   │       │   ├── list.html
│   │       │   ├── detail.html
│   │       │   ├── form.html
│   │       │   └── confirm_delete.html
│   │       ├── departments/
│   │       │   ├── list.html
│   │       │   ├── detail.html
│   │       │   ├── form.html
│   │       │   └── confirm_delete.html
│   │       └── projects/
│   │           ├── list.html
│   │           ├── detail.html
│   │           ├── form.html
│   │           └── confirm_delete.html
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── seed_data.py
└── manage.py
```

---

## 4. Models

Create `hrms/models.py` with the following content. The hierarchy mirrors Alphabet's structure: Individual Contributors (L1–L4), Middle Management, Senior Leadership, and C-Suite.

```python
# hrms/models.py

from django.db import models


# ─────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────

class EmployeeLevel(models.TextChoices):
    # Individual Contributors
    L1 = "L1", "L1 – Associate"
    L2 = "L2", "L2 – Junior"
    L3 = "L3", "L3 – Mid-Level"
    L4 = "L4", "L4 – Senior IC"
    # Middle Management
    SPM = "SPM", "Senior Product Manager"
    GROUP_MANAGER = "GM", "Group Manager"
    # Senior Leadership
    DIRECTOR = "DIR", "Director"
    SVP = "SVP", "Senior Vice President"
    # C-Suite
    VP = "VP", "Vice President"
    CEO = "CEO", "Chief Executive Officer"
    CFO = "CFO", "Chief Financial Officer"
    CTO = "CTO", "Chief Technology Officer"
    COO = "COO", "Chief Operating Officer"


class EmployeeType(models.TextChoices):
    INDIVIDUAL_CONTRIBUTOR = "IC", "Individual Contributor"
    MIDDLE_MANAGEMENT = "MM", "Middle Management"
    SENIOR_LEADERSHIP = "SL", "Senior Leadership"
    C_SUITE = "CS", "C-Suite"


class ProjectStatus(models.TextChoices):
    PLANNING = "PLAN", "Planning"
    ACTIVE = "ACTIVE", "Active"
    ON_HOLD = "HOLD", "On Hold"
    COMPLETED = "DONE", "Completed"
    CANCELLED = "CANC", "Cancelled"


# ─────────────────────────────────────────────
# Department
# ─────────────────────────────────────────────

class Department(models.Model):
    """
    Represents a business unit (e.g., Google Search, YouTube, Google Cloud).
    Departments can be nested: a sub-department points to a parent department.
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_departments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


# ─────────────────────────────────────────────
# Employee
# ─────────────────────────────────────────────

class Employee(models.Model):
    """
    Unified employee model covering all four tiers of the Alphabet hierarchy.

    Relationships:
      - manager (self-referential FK): direct reporting line
      - department (FK): the primary business unit the employee belongs to
      - direct_reports: reverse of manager FK — employees who report to this person
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=200)
    employee_type = models.CharField(
        max_length=2,
        choices=EmployeeType.choices,
        default=EmployeeType.INDIVIDUAL_CONTRIBUTOR,
    )
    level = models.CharField(
        max_length=5,
        choices=EmployeeLevel.choices,
        default=EmployeeLevel.L1,
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees",
    )
    # Self-referential: an employee's direct manager
    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="direct_reports",
    )
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.level})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]


# ─────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────

class Project(models.Model):
    """
    A business initiative that spans one or more departments and employees.

    Relationships:
      - department (FK): the owning / sponsoring department
      - lead (FK → Employee): the employee accountable for delivery
      - members (M2M → Employee): all employees contributing to the project
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=6,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PLANNING,
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projects",
    )
    lead = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="led_projects",
    )
    # All contributors (includes lead)
    members = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="projects",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
```

### Relationship Summary

| Relationship | From | To | Type |
|---|---|---|---|
| Reporting line | `Employee.manager` | `Employee` | FK (self) |
| Primary unit | `Employee.department` | `Department` | FK |
| Sub-unit | `Department.parent` | `Department` | FK (self) |
| Project ownership | `Project.department` | `Department` | FK |
| Project accountability | `Project.lead` | `Employee` | FK |
| Project contribution | `Project.members` | `Employee` | M2M |

---

## 5. Database Migrations

```bash
python manage.py makemigrations hrms
python manage.py migrate
```

---

## 6. Fake Data Seed Script

Create `seed_data.py` at the project root. Run it once after migrations to populate realistic Alphabet-style data.

```python
# seed_data.py
"""
Populate the HRMS database with fake Alphabet-style data.
Run with:  python manage.py shell < seed_data.py
  or:      python seed_data.py   (from the project root with DJANGO_SETTINGS_MODULE set)
"""

import os
import sys
import django
import random
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hrms_project.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from faker import Faker
from hrms.models import Department, Employee, Project, EmployeeLevel, EmployeeType, ProjectStatus

fake = Faker()
Faker.seed(42)
random.seed(42)

# ── Wipe existing data ────────────────────────────────────────────────────────
Project.objects.all().delete()
Employee.objects.all().delete()
Department.objects.all().delete()

# ── Departments ───────────────────────────────────────────────────────────────
top_level_departments = [
    "Google Search",
    "YouTube",
    "Google Cloud",
    "Google Ads",
    "Hardware",
    "AI Research (DeepMind)",
    "Android & Chrome",
    "Finance",
    "Legal & Policy",
    "People Operations",
]

sub_department_map = {
    "Google Search":        ["Search Quality", "Search Infrastructure", "Knowledge Graph"],
    "YouTube":              ["YouTube Premium", "YouTube Kids", "Creator Ecosystem"],
    "Google Cloud":         ["GKE & Compute", "BigQuery & Analytics", "Cloud Security"],
    "Google Ads":           ["Performance Max", "Display & Video 360", "Ad Tech Platform"],
    "Hardware":             ["Pixel Phones", "Nest & Home", "Fitbit"],
    "AI Research (DeepMind)": ["Gemini", "Robotics", "Safety Research"],
    "Android & Chrome":     ["Android OS", "Chrome Browser", "ChromeOS"],
    "Finance":              ["FP&A", "Tax", "Treasury"],
    "Legal & Policy":       ["Privacy & Compliance", "Litigation", "Government Affairs"],
    "People Operations":    ["Talent Acquisition", "L&D", "Total Rewards"],
}

dept_objects = {}
for name in top_level_departments:
    d = Department.objects.create(name=name, description=fake.sentence())
    dept_objects[name] = d
    for sub_name in sub_department_map.get(name, []):
        s = Department.objects.create(
            name=sub_name, description=fake.sentence(), parent=d
        )
        dept_objects[sub_name] = s

all_depts = list(Department.objects.filter(parent__isnull=False))  # prefer sub-depts for employees

# ── C-Suite ───────────────────────────────────────────────────────────────────
c_suite_data = [
    ("Sundar",  "Pichai",  "CEO",  EmployeeLevel.CEO,  EmployeeType.C_SUITE,  "Chief Executive Officer"),
    ("Ruth",    "Porat",   "CFO",  EmployeeLevel.CFO,  EmployeeType.C_SUITE,  "Chief Financial Officer"),
    ("Prabhakar","Raghavan","CTO", EmployeeLevel.CTO,  EmployeeType.C_SUITE,  "Chief Technology Officer"),
]

c_suite_employees = []
for fn, ln, abbr, level, etype, title in c_suite_data:
    e = Employee.objects.create(
        first_name=fn, last_name=ln,
        email=f"{fn.lower()}.{ln.lower()}@alphabet.com",
        title=title, employee_type=etype, level=level,
        department=dept_objects["Google Search"],   # HQ placeholder
        hire_date=date(2015, 1, 1),
        bio=fake.paragraph(),
    )
    c_suite_employees.append(e)

ceo = c_suite_employees[0]

# ── SVPs (Senior Leadership) ──────────────────────────────────────────────────
svp_employees = []
for top_dept_name in list(top_level_departments)[:6]:
    dept = dept_objects[top_dept_name]
    e = Employee.objects.create(
        first_name=fake.first_name(), last_name=fake.last_name(),
        email=fake.unique.company_email(),
        title=f"SVP, {top_dept_name}",
        employee_type=EmployeeType.SENIOR_LEADERSHIP,
        level=EmployeeLevel.SVP,
        department=dept,
        manager=ceo,
        hire_date=fake.date_between(start_date="-12y", end_date="-6y"),
        bio=fake.paragraph(),
    )
    svp_employees.append((dept, e))

# ── Directors (Senior Leadership) ─────────────────────────────────────────────
director_employees = []
for parent_dept, svp in svp_employees:
    sub_depts = list(parent_dept.sub_departments.all())
    for sub_dept in sub_depts:
        e = Employee.objects.create(
            first_name=fake.first_name(), last_name=fake.last_name(),
            email=fake.unique.company_email(),
            title=f"Director, {sub_dept.name}",
            employee_type=EmployeeType.SENIOR_LEADERSHIP,
            level=EmployeeLevel.DIRECTOR,
            department=sub_dept,
            manager=svp,
            hire_date=fake.date_between(start_date="-10y", end_date="-4y"),
            bio=fake.paragraph(),
        )
        director_employees.append((sub_dept, e))

# ── Middle Management (SPMs & Group Managers) ─────────────────────────────────
manager_employees = []
for sub_dept, director in director_employees:
    for _ in range(random.randint(2, 3)):
        level = random.choice([EmployeeLevel.SPM, EmployeeLevel.GROUP_MANAGER])
        title = "Senior Product Manager" if level == EmployeeLevel.SPM else "Group Manager"
        e = Employee.objects.create(
            first_name=fake.first_name(), last_name=fake.last_name(),
            email=fake.unique.company_email(),
            title=f"{title}, {sub_dept.name}",
            employee_type=EmployeeType.MIDDLE_MANAGEMENT,
            level=level,
            department=sub_dept,
            manager=director,
            hire_date=fake.date_between(start_date="-8y", end_date="-2y"),
            bio=fake.paragraph(),
        )
        manager_employees.append((sub_dept, e))

# ── Individual Contributors (L1–L4) ───────────────────────────────────────────
ic_levels = [EmployeeLevel.L1, EmployeeLevel.L2, EmployeeLevel.L3, EmployeeLevel.L4]
ic_titles = {
    EmployeeLevel.L1: "Associate Software Engineer",
    EmployeeLevel.L2: "Software Engineer",
    EmployeeLevel.L3: "Senior Software Engineer",
    EmployeeLevel.L4: "Staff Software Engineer",
}

ic_employees = []
for sub_dept, mgr in manager_employees:
    for _ in range(random.randint(3, 6)):
        level = random.choice(ic_levels)
        e = Employee.objects.create(
            first_name=fake.first_name(), last_name=fake.last_name(),
            email=fake.unique.company_email(),
            title=ic_titles[level],
            employee_type=EmployeeType.INDIVIDUAL_CONTRIBUTOR,
            level=level,
            department=sub_dept,
            manager=mgr,
            hire_date=fake.date_between(start_date="-5y", end_date="today"),
            bio=fake.paragraph(),
        )
        ic_employees.append(e)

print(f"Employees created: {Employee.objects.count()}")

# ── Projects ──────────────────────────────────────────────────────────────────
all_managers = [e for _, e in manager_employees]
all_ics = ic_employees
all_employees = list(Employee.objects.all())

project_names = [
    "Project Monarch", "Gemini Ultra Rollout", "Pixel 9 Launch",
    "Cloud Cost Optimisation", "YouTube Shorts Monetisation",
    "Search Ranking v3", "SafeSearch Overhaul", "Nest Thermostat AI",
    "BigQuery ML Integration", "Chrome Memory Saver",
    "Android Privacy Sandbox", "Ad Attribution Rebuild",
    "DeepMind Safety Audit", "Global Talent Pipeline",
    "Carbon Neutral Datacenters",
]

for i, proj_name in enumerate(project_names):
    dept = random.choice(all_depts)
    lead = random.choice(all_managers)
    start = fake.date_between(start_date="-2y", end_date="today")
    end = start + timedelta(days=random.randint(90, 540))
    status = random.choice(list(ProjectStatus.values))

    project = Project.objects.create(
        name=proj_name,
        description=fake.paragraph(nb_sentences=3),
        status=status,
        department=dept,
        lead=lead,
        start_date=start,
        end_date=end,
    )

    # Assign between 5–15 members
    members = random.sample(all_employees, k=random.randint(5, 15))
    if lead not in members:
        members.append(lead)
    project.members.set(members)

print(f"Projects created: {Project.objects.count()}")
print("Seed complete.")
```

Run the seed script:

```bash
python seed_data.py
```

---

## 7. Forms

```python
# hrms/forms.py

from django import forms
from .models import Department, Employee, Project


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description", "parent"]


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name", "last_name", "email", "title",
            "employee_type", "level", "department", "manager",
            "hire_date", "is_active", "bio",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name", "description", "status",
            "department", "lead", "members",
            "start_date", "end_date",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date":   forms.DateInput(attrs={"type": "date"}),
            "members":    forms.SelectMultiple(),
        }
```

---

## 8. Views

All mutation views (`create`, `update`, `delete`) return HTMX-friendly partial responses. List and detail views render full pages on first load.

```python
# hrms/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import Department, Employee, Project
from .forms import DepartmentForm, EmployeeForm, ProjectForm


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard(request):
    context = {
        "employee_count": Employee.objects.filter(is_active=True).count(),
        "department_count": Department.objects.count(),
        "project_count": Project.objects.count(),
        "recent_employees": Employee.objects.order_by("-created_at")[:5],
        "active_projects": Project.objects.filter(status="ACTIVE")[:5],
    }
    return render(request, "hrms/dashboard.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# DEPARTMENT VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def department_list(request):
    q = request.GET.get("q", "")
    departments = Department.objects.filter(parent__isnull=True).prefetch_related("sub_departments")
    if q:
        departments = Department.objects.filter(name__icontains=q)
    return render(request, "hrms/departments/list.html", {"departments": departments, "q": q})


def department_detail(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    employees = dept.employees.select_related("manager")
    projects = dept.projects.all()
    sub_depts = dept.sub_departments.all()
    return render(request, "hrms/departments/detail.html", {
        "dept": dept, "employees": employees,
        "projects": projects, "sub_depts": sub_depts,
    })


@require_http_methods(["GET", "POST"])
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dept = form.save()
        if request.headers.get("HX-Request"):
            # Return a small confirmation snippet
            return HttpResponse(
                f'<p>Department <strong>{dept.name}</strong> created. '
                f'<a href="/departments/{dept.pk}/">View</a></p>'
            )
        return redirect("hrms:department_detail", pk=dept.pk)
    return render(request, "hrms/departments/form.html", {"form": form, "action": "Create"})


@require_http_methods(["GET", "POST"])
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if request.method == "POST" and form.is_valid():
        form.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<p>Department <strong>{dept.name}</strong> updated. '
                f'<a href="/departments/{dept.pk}/">View</a></p>'
            )
        return redirect("hrms:department_detail", pk=dept.pk)
    return render(request, "hrms/departments/form.html", {
        "form": form, "action": "Update", "object": dept
    })


@require_http_methods(["GET", "DELETE", "POST"])
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method in ("DELETE", "POST"):
        name = dept.name
        dept.delete()
        if request.headers.get("HX-Request"):
            return HttpResponse(f'<p>Department <strong>{name}</strong> deleted.</p>')
        return redirect("hrms:department_list")
    return render(request, "hrms/departments/confirm_delete.html", {"object": dept, "type": "Department"})


# ══════════════════════════════════════════════════════════════════════════════
# EMPLOYEE VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def employee_list(request):
    q = request.GET.get("q", "")
    level = request.GET.get("level", "")
    dept_id = request.GET.get("dept", "")

    employees = Employee.objects.select_related("department", "manager")

    if q:
        employees = employees.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if level:
        employees = employees.filter(level=level)
    if dept_id:
        employees = employees.filter(department_id=dept_id)

    # If this is an HTMX search request, return only the table rows partial
    if request.headers.get("HX-Request"):
        return render(request, "hrms/employees/_table_rows.html", {"employees": employees})

    departments = Department.objects.all()
    from .models import EmployeeLevel
    return render(request, "hrms/employees/list.html", {
        "employees": employees, "q": q,
        "level": level, "dept_id": dept_id,
        "departments": departments,
        "level_choices": EmployeeLevel.choices,
    })


def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    direct_reports = emp.direct_reports.select_related("department")
    projects = emp.projects.all()
    led_projects = emp.led_projects.all()
    return render(request, "hrms/employees/detail.html", {
        "emp": emp, "direct_reports": direct_reports,
        "projects": projects, "led_projects": led_projects,
    })


@require_http_methods(["GET", "POST"])
def employee_create(request):
    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        emp = form.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<p>Employee <strong>{emp.full_name}</strong> created. '
                f'<a href="/employees/{emp.pk}/">View</a></p>'
            )
        return redirect("hrms:employee_detail", pk=emp.pk)
    return render(request, "hrms/employees/form.html", {"form": form, "action": "Create"})


@require_http_methods(["GET", "POST"])
def employee_update(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=emp)
    if request.method == "POST" and form.is_valid():
        form.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<p>Employee <strong>{emp.full_name}</strong> updated. '
                f'<a href="/employees/{emp.pk}/">View</a></p>'
            )
        return redirect("hrms:employee_detail", pk=emp.pk)
    return render(request, "hrms/employees/form.html", {
        "form": form, "action": "Update", "object": emp
    })


@require_http_methods(["GET", "DELETE", "POST"])
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method in ("DELETE", "POST"):
        name = emp.full_name
        emp.delete()
        if request.headers.get("HX-Request"):
            return HttpResponse(f'<p>Employee <strong>{name}</strong> deleted.</p>')
        return redirect("hrms:employee_list")
    return render(request, "hrms/employees/confirm_delete.html", {
        "object": emp, "type": "Employee"
    })


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def project_list(request):
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")
    projects = Project.objects.select_related("department", "lead")
    if q:
        projects = projects.filter(name__icontains=q)
    if status:
        projects = projects.filter(status=status)
    if request.headers.get("HX-Request"):
        return render(request, "hrms/projects/_table_rows.html", {"projects": projects})
    from .models import ProjectStatus
    return render(request, "hrms/projects/list.html", {
        "projects": projects, "q": q, "status": status,
        "status_choices": ProjectStatus.choices,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    members = project.members.select_related("department")
    return render(request, "hrms/projects/detail.html", {
        "project": project, "members": members
    })


@require_http_methods(["GET", "POST"])
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<p>Project <strong>{project.name}</strong> created. '
                f'<a href="/projects/{project.pk}/">View</a></p>'
            )
        return redirect("hrms:project_detail", pk=project.pk)
    return render(request, "hrms/projects/form.html", {"form": form, "action": "Create"})


@require_http_methods(["GET", "POST"])
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<p>Project <strong>{project.name}</strong> updated. '
                f'<a href="/projects/{project.pk}/">View</a></p>'
            )
        return redirect("hrms:project_detail", pk=project.pk)
    return render(request, "hrms/projects/form.html", {
        "form": form, "action": "Update", "object": project
    })


@require_http_methods(["GET", "DELETE", "POST"])
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method in ("DELETE", "POST"):
        name = project.name
        project.delete()
        if request.headers.get("HX-Request"):
            return HttpResponse(f'<p>Project <strong>{name}</strong> deleted.</p>')
        return redirect("hrms:project_list")
    return render(request, "hrms/projects/confirm_delete.html", {
        "object": project, "type": "Project"
    })
```

---

## 9. URL Configuration

### `hrms/urls.py`

```python
# hrms/urls.py

from django.urls import path
from . import views

app_name = "hrms"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Departments
    path("departments/",                   views.department_list,   name="department_list"),
    path("departments/create/",            views.department_create, name="department_create"),
    path("departments/<int:pk>/",          views.department_detail, name="department_detail"),
    path("departments/<int:pk>/update/",   views.department_update, name="department_update"),
    path("departments/<int:pk>/delete/",   views.department_delete, name="department_delete"),

    # Employees
    path("employees/",                     views.employee_list,   name="employee_list"),
    path("employees/create/",              views.employee_create, name="employee_create"),
    path("employees/<int:pk>/",            views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/update/",     views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/",     views.employee_delete, name="employee_delete"),

    # Projects
    path("projects/",                      views.project_list,   name="project_list"),
    path("projects/create/",               views.project_create, name="project_create"),
    path("projects/<int:pk>/",             views.project_detail, name="project_detail"),
    path("projects/<int:pk>/update/",      views.project_update, name="project_update"),
    path("projects/<int:pk>/delete/",      views.project_delete, name="project_delete"),
]
```

### `hrms_project/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hrms.urls", namespace="hrms")),
]
```

---

## 10. Templates

No CSS is applied anywhere. All interactivity goes through HTMX attributes.

### `hrms/templates/hrms/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}HR Dashboard{% endblock %}</title>
  <!-- HTMX via CDN (swap for a local copy in production) -->
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body
  hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
>

<nav>
  <a href="{% url 'hrms:dashboard' %}">Dashboard</a> |
  <a href="{% url 'hrms:employee_list' %}">Employees</a> |
  <a href="{% url 'hrms:department_list' %}">Departments</a> |
  <a href="{% url 'hrms:project_list' %}">Projects</a>
</nav>

<hr>

<div id="main-content">
  {% block content %}{% endblock %}
</div>

</body>
</html>
```

> **Key pattern:** `hx-headers` on `<body>` injects the CSRF token into every HTMX request automatically. Django's CSRF middleware reads `X-CSRFToken` from the request header.

---

### `hrms/templates/hrms/dashboard.html`

```html
{% extends "hrms/base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<h1>HR Dashboard</h1>

<p>Active Employees: {{ employee_count }}</p>
<p>Departments: {{ department_count }}</p>
<p>Projects: {{ project_count }}</p>

<h2>Recently Added Employees</h2>
<ul>
  {% for emp in recent_employees %}
    <li><a href="{% url 'hrms:employee_detail' emp.pk %}">{{ emp.full_name }}</a> — {{ emp.title }}</li>
  {% endfor %}
</ul>

<h2>Active Projects</h2>
<ul>
  {% for proj in active_projects %}
    <li><a href="{% url 'hrms:project_detail' proj.pk %}">{{ proj.name }}</a> ({{ proj.department }})</li>
  {% endfor %}
</ul>
{% endblock %}
```

---

### `hrms/templates/hrms/employees/list.html`

```html
{% extends "hrms/base.html" %}
{% block title %}Employees{% endblock %}
{% block content %}
<h1>Employees</h1>

<a href="{% url 'hrms:employee_create' %}">+ New Employee</a>

<form>
  <input
    type="text"
    name="q"
    value="{{ q }}"
    placeholder="Search name or email…"
    hx-get="{% url 'hrms:employee_list' %}"
    hx-trigger="keyup changed delay:300ms"
    hx-target="#employee-rows"
    hx-swap="innerHTML"
  >

  <select name="level"
    hx-get="{% url 'hrms:employee_list' %}"
    hx-trigger="change"
    hx-target="#employee-rows"
    hx-swap="innerHTML"
    hx-include="[name='q'],[name='dept']"
  >
    <option value="">All Levels</option>
    {% for val, label in level_choices %}
      <option value="{{ val }}" {% if val == level %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>

  <select name="dept"
    hx-get="{% url 'hrms:employee_list' %}"
    hx-trigger="change"
    hx-target="#employee-rows"
    hx-swap="innerHTML"
    hx-include="[name='q'],[name='level']"
  >
    <option value="">All Departments</option>
    {% for dept in departments %}
      <option value="{{ dept.pk }}" {% if dept.pk|stringformat:"s" == dept_id %}selected{% endif %}>{{ dept.name }}</option>
    {% endfor %}
  </select>
</form>

<table border="1">
  <thead>
    <tr>
      <th>Name</th><th>Title</th><th>Level</th><th>Department</th><th>Manager</th><th>Actions</th>
    </tr>
  </thead>
  <tbody id="employee-rows">
    {% include "hrms/employees/_table_rows.html" %}
  </tbody>
</table>
{% endblock %}
```

---

### `hrms/templates/hrms/employees/_table_rows.html`

```html
{% for emp in employees %}
<tr>
  <td><a href="{% url 'hrms:employee_detail' emp.pk %}">{{ emp.full_name }}</a></td>
  <td>{{ emp.title }}</td>
  <td>{{ emp.get_level_display }}</td>
  <td>{{ emp.department }}</td>
  <td>
    {% if emp.manager %}
      <a href="{% url 'hrms:employee_detail' emp.manager.pk %}">{{ emp.manager.full_name }}</a>
    {% else %}—{% endif %}
  </td>
  <td>
    <a href="{% url 'hrms:employee_update' emp.pk %}">Edit</a> |
    <button
      hx-delete="{% url 'hrms:employee_delete' emp.pk %}"
      hx-target="closest tr"
      hx-swap="outerHTML"
      hx-confirm="Delete {{ emp.full_name }}?"
    >Delete</button>
  </td>
</tr>
{% empty %}
<tr><td colspan="6">No employees found.</td></tr>
{% endfor %}
```

---

### `hrms/templates/hrms/employees/detail.html`

```html
{% extends "hrms/base.html" %}
{% block title %}{{ emp.full_name }}{% endblock %}
{% block content %}
<h1>{{ emp.full_name }}</h1>
<p>Title: {{ emp.title }}</p>
<p>Level: {{ emp.get_level_display }}</p>
<p>Type: {{ emp.get_employee_type_display }}</p>
<p>Department: <a href="{% url 'hrms:department_detail' emp.department.pk %}">{{ emp.department }}</a></p>
<p>Manager:
  {% if emp.manager %}
    <a href="{% url 'hrms:employee_detail' emp.manager.pk %}">{{ emp.manager.full_name }}</a>
  {% else %}(none — top of hierarchy){% endif %}
</p>
<p>Hire Date: {{ emp.hire_date }}</p>
<p>Active: {{ emp.is_active|yesno:"Yes,No" }}</p>
<p>Bio: {{ emp.bio }}</p>

<p>
  <a href="{% url 'hrms:employee_update' emp.pk %}">Edit</a> |
  <button
    hx-delete="{% url 'hrms:employee_delete' emp.pk %}"
    hx-target="#delete-result"
    hx-swap="innerHTML"
    hx-confirm="Permanently delete {{ emp.full_name }}?"
  >Delete</button>
</p>
<div id="delete-result"></div>

<h2>Direct Reports ({{ direct_reports.count }})</h2>
<ul>
  {% for dr in direct_reports %}
    <li><a href="{% url 'hrms:employee_detail' dr.pk %}">{{ dr.full_name }}</a> — {{ dr.title }}</li>
  {% empty %}
    <li>None</li>
  {% endfor %}
</ul>

<h2>Projects (member)</h2>
<ul>
  {% for proj in projects %}
    <li><a href="{% url 'hrms:project_detail' proj.pk %}">{{ proj.name }}</a></li>
  {% empty %}
    <li>None</li>
  {% endfor %}
</ul>

<h2>Led Projects</h2>
<ul>
  {% for proj in led_projects %}
    <li><a href="{% url 'hrms:project_detail' proj.pk %}">{{ proj.name }}</a></li>
  {% empty %}
    <li>None</li>
  {% endfor %}
</ul>
{% endblock %}
```

---

### `hrms/templates/hrms/employees/form.html`

```html
{% extends "hrms/base.html" %}
{% block title %}{{ action }} Employee{% endblock %}
{% block content %}
<h1>{{ action }} Employee</h1>

<div id="form-result"></div>

<form
  hx-post="{% if object %}{% url 'hrms:employee_update' object.pk %}{% else %}{% url 'hrms:employee_create' %}{% endif %}"
  hx-target="#form-result"
  hx-swap="innerHTML"
>
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">{{ action }}</button>
  <a href="{% url 'hrms:employee_list' %}">Cancel</a>
</form>
{% endblock %}
```

---

### `hrms/templates/hrms/employees/confirm_delete.html`

```html
{% extends "hrms/base.html" %}
{% block title %}Delete {{ type }}{% endblock %}
{% block content %}
<h1>Delete {{ type }}: {{ object }}</h1>
<p>Are you sure? This action cannot be undone.</p>

<div id="delete-result"></div>

<button
  hx-post="{% url 'hrms:employee_delete' object.pk %}"
  hx-target="#delete-result"
  hx-swap="innerHTML"
>Yes, Delete</button>
<a href="{% url 'hrms:employee_list' %}">Cancel</a>
{% endblock %}
```

---

### Department & Project Templates

Follow the exact same patterns as the employee templates. Replace `employee` with `department` or `project`, adjust fields accordingly, and use the matching URL names. The structure for `form.html`, `detail.html`, `list.html`, `_table_rows.html`, and `confirm_delete.html` is identical — only the model fields and URL names differ.

For example, `hrms/templates/hrms/departments/list.html` uses:
- `hx-get="{% url 'hrms:department_list' %}"` for search
- `hx-delete="{% url 'hrms:department_delete' dept.pk %}"` for inline delete

And `hrms/templates/hrms/projects/detail.html` adds a members table:

```html
<h2>Project Members</h2>
<table border="1">
  <thead><tr><th>Name</th><th>Level</th><th>Department</th></tr></thead>
  <tbody>
    {% for member in members %}
    <tr>
      <td><a href="{% url 'hrms:employee_detail' member.pk %}">{{ member.full_name }}</a></td>
      <td>{{ member.get_level_display }}</td>
      <td>{{ member.department }}</td>
    </tr>
    {% empty %}
    <tr><td colspan="3">No members assigned.</td></tr>
    {% endfor %}
  </tbody>
</table>
```

---

## 11. HTMX & CSRF Setup

### How CSRF Works Here

Django requires a CSRF token for all non-GET requests. HTMX does not include it by default. The solution used in this project is the `hx-headers` attribute on `<body>`:

```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

This means **every HTMX request** — regardless of which element triggers it — automatically carries the `X-CSRFToken` header. Django's `CsrfViewMiddleware` checks this header in addition to the `csrfmiddlewaretoken` form field, so no per-form token field is needed for HTMX-only forms.

> The `{% csrf_token %}` tag inside `<form>` elements is kept for graceful non-JS fallback.

### HTMX Patterns Used

| Pattern | Usage |
|---|---|
| `hx-get` + `hx-trigger="keyup delay:300ms"` | Live search without page reload |
| `hx-post` + `hx-target="#form-result"` | Inline form submission feedback |
| `hx-delete` + `hx-target="closest tr"` | Remove a table row on delete |
| `hx-confirm` | Native browser confirmation dialog before destructive actions |
| `hx-include` | Include sibling filter inputs in a search request |
| `hx-swap="outerHTML"` | Replace the entire element (e.g., a deleted row) |

### Django Settings — Ensure CSRF Middleware is Active

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",   # ← required
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

---

## 12. Running the Project

```bash
# 1. Apply migrations
python manage.py migrate

# 2. Seed fake data
python seed_data.py

# 3. Create a superuser (optional, for Django admin)
python manage.py createsuperuser

# 4. Register models with admin (optional)
# hrms/admin.py
from django.contrib import admin
from .models import Department, Employee, Project
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Project)

# 5. Start the dev server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` to see the dashboard.

---

## Architecture Overview

```
Alphabet Inc. Hierarchy
═══════════════════════

CEO (Sundar Pichai)
 ├── CFO
 ├── CTO
 └── SVP, Google Search
      └── Director, Search Quality
           ├── Group Manager
           │    ├── L4 Staff SWE
           │    ├── L3 Senior SWE
           │    └── L2 SWE
           └── Senior PM
                └── L1 Associate SWE

Department Tree
═══════════════
Google Cloud (top-level)
 ├── GKE & Compute        (sub-dept, parent=Google Cloud)
 ├── BigQuery & Analytics (sub-dept)
 └── Cloud Security       (sub-dept)

Project Relationships
═════════════════════
Project "Gemini Ultra Rollout"
 ├── department  → AI Research (DeepMind)
 ├── lead        → Employee (Group Manager)
 └── members     → [Employee, Employee, Employee, …]
```

---

*End of guide. The application is intentionally unstyled to keep the focus on Django model design, HTMX integration patterns, and the CSRF header approach.*

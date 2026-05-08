# Semmelweis Handwashing Analysis — Django App
### Complete Build Guide with Annotated Code

> This document is generated from the working application source. Every code
> block is taken verbatim from the real files, with explanatory comments added
> inline.

---

## Table of Contents

- [Semmelweis Handwashing Analysis — Django App](#semmelweis-handwashing-analysis--django-app)
    - [Complete Build Guide with Annotated Code](#complete-build-guide-with-annotated-code)
  - [Table of Contents](#table-of-contents)
  - [1. What the App Does](#1-what-the-app-does)
  - [2. Project Structure](#2-project-structure)
  - [3. Setup \& Installation](#3-setup--installation)
    - [requirements.txt](#requirementstxt)
  - [4. Settings](#4-settings)
  - [5. Models](#5-models)
  - [6. Forms](#6-forms)
  - [7. Services (data layer)](#7-services-data-layer)
  - [8. Views](#8-views)
  - [9. URLs](#9-urls)
  - [10. Templates](#10-templates)
    - [DaisyUI Tab Pattern](#daisyui-tab-pattern)
    - [`base.html`](#basehtml)
    - [`upload.html`](#uploadhtml)
    - [`dashboard.html`](#dashboardhtml)
    - [`yearly_list.html`](#yearly_listhtml)
    - [`_yearly_table.html` (partial)](#_yearly_tablehtml-partial)
    - [`yearly_form.html`](#yearly_formhtml)
    - [`monthly_list.html`](#monthly_listhtml)
    - [`monthly_form.html`](#monthly_formhtml)
    - [`confirm_delete.html`](#confirm_deletehtml)
    - [`analysis_results.html`](#analysis_resultshtml)
  - [11. Static JS — charts.js](#11-static-js--chartsjs)
  - [12. Admin](#12-admin)
  - [13. First Run](#13-first-run)

---

## 1. What the App Does

The app is a Django web application that replicates and extends the classic
Semmelweis handwashing Jupyter notebook analysis. It provides:

- **CSV import** of two datasets: yearly clinic death records and monthly
  clinic death records.
- **CRUD management** of both datasets via Django generic class-based views.
- **Interactive charts** rendered in-browser with Chart.js.
- **Statistical analysis**: mean comparison, bootstrap 95 % confidence
  interval, and Welch's t-test.
- **Downloadable outputs**: processed CSV files and PNG chart images generated
  server-side with Matplotlib.
- **DaisyUI + Tailwind CSS** loaded from CDN for styling — no build step
  needed.
- **Tabbed UI** using DaisyUI's radio-input tab pattern throughout.

---

## 2. Project Structure

```
semmelweis_project/         ← Django project root (created by startproject)
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created on first migrate
├── semmelweis_project/     ← project package (settings, root urls, wsgi)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── analysis/               ← the single Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py         ← all pandas/matplotlib/scipy logic lives here
│   ├── urls.py
│   ├── views.py
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py
├── templates/              ← project-level templates directory
│   ├── base.html
│   └── analysis/           ← one sub-folder per app by convention
│       ├── dashboard.html
│       ├── upload.html
│       ├── yearly_list.html
│       ├── yearly_form.html
│       ├── _yearly_table.html   ← reusable partial (prefixed with _)
│       ├── monthly_list.html
│       ├── monthly_form.html
│       ├── confirm_delete.html
│       └── analysis_results.html
├── static/
│   └── js/
│       └── charts.js       ← Chart.js helper functions
└── media/
    └── uploads/
        └── semmelweis.jpeg ← doctor portrait (copy here manually)
```

---

## 3. Setup & Installation

### requirements.txt

```
Django>=4.2,<5.0
pandas>=2.0
matplotlib>=3.7
numpy>=1.24
scipy>=1.10
```

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Scaffold the Django project and app
django-admin startproject semmelweis_project .
python manage.py startapp analysis

# 4. Create the directories Django will not create automatically
mkdir -p templates/analysis
mkdir -p static/js
mkdir -p media/uploads

# 5. Copy the portrait photo into media/uploads/
cp /path/to/ignaz_semmelweis_1860.jpeg media/uploads/semmelweis.jpeg
```

---

## 4. Settings

```python
# semmelweis_project/settings.py
# Only the additions / changes from the default are shown.

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Installed apps ────────────────────────────────────────────────────────────
# Add 'analysis' so Django discovers models, admin, and static files inside it.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analysis',   # ← register the analysis app
]

# ── Templates ─────────────────────────────────────────────────────────────────
# DIRS tells Django to look in the project-level templates/ folder first.
# APP_DIRS: True also allows templates inside each app's own templates/ folder.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # ← critical: point at project templates/
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

# ── Static files ──────────────────────────────────────────────────────────────
# STATIC_URL is the URL prefix for serving static files.
# STATICFILES_DIRS tells Django where to look for additional static files
# that are NOT inside an app's static/ sub-folder.
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ── Media files ───────────────────────────────────────────────────────────────
# MEDIA_URL / MEDIA_ROOT handle user-uploaded content (the portrait photo and
# any files uploaded via the CSV import form).
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Primary key ───────────────────────────────────────────────────────────────
# BigAutoField uses a 64-bit integer for primary keys — good practice for
# tables that could grow large.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## 5. Models

```python
# analysis/models.py

from django.db import models


class YearlyRecord(models.Model):
    """
    Stores one row from yearly_deaths_by_clinic.csv.

    Each row represents the total births and deaths at one clinic for one year.
    The CSV contains data for Clinic 1 and Clinic 2 from 1841 to 1846.
    """

    year   = models.IntegerField()           # e.g. 1841, 1842, …
    births = models.IntegerField()           # total births in that year
    deaths = models.IntegerField()           # total deaths in that year
    clinic = models.CharField(max_length=20) # 'clinic 1' or 'clinic 2'

    class Meta:
        # Default sort order: clinic name first, then year ascending.
        # This means all Clinic 1 rows appear before Clinic 2 rows.
        ordering = ["clinic", "year"]

    def __str__(self):
        # Human-readable label used in admin and delete confirmation pages.
        return f"{self.clinic} – {self.year}"

    @property
    def proportion_deaths(self):
        """
        Computed field: deaths ÷ births, rounded to 6 decimal places.
        @property means it is accessed like an attribute (r.proportion_deaths)
        but is never stored in the database — it is always calculated on the fly.
        The guard against zero prevents ZeroDivisionError if births is 0.
        """
        return round(self.deaths / self.births, 6) if self.births else 0


class MonthlyRecord(models.Model):
    """
    Stores one row from monthly_deaths.csv.

    Contains monthly birth and death counts for Clinic 1 from 1841 to 1849.
    The pivotal date — when Semmelweis mandated handwashing — is June 1847.
    """

    date   = models.DateField()   # first day of the reported month, e.g. 1841-01-01
    births = models.IntegerField()
    deaths = models.IntegerField()

    # Class constant: the date handwashing was made mandatory.
    # Stored here so every part of the code can reference MonthlyRecord.HANDWASHING_START
    # instead of hard-coding the string "1847-06-01" in multiple places.
    HANDWASHING_START = "1847-06-01"

    class Meta:
        ordering = ["date"]  # chronological order

    def __str__(self):
        return str(self.date)

    @property
    def proportion_deaths(self):
        """Deaths as a fraction of births for this month."""
        return round(self.deaths / self.births, 6) if self.births else 0

    @property
    def after_handwashing(self):
        """
        Returns True if this record falls on or after June 1847.
        Used in the monthly_list.html template to colour rows and show
        'Before' / 'After' badges.
        The import is inside the function to avoid a circular import at module
        load time (though in practice it would not cause issues here).
        """
        from datetime import date
        pivot = date(1847, 6, 1)
        return self.date >= pivot
```

---

## 6. Forms

```python
# analysis/forms.py

from django import forms
from .models import YearlyRecord, MonthlyRecord


class CSVUploadForm(forms.Form):
    """
    A plain Form (not ModelForm) for uploading one or two CSV files.
    Both fields are optional individually, but the clean() method enforces
    that at least one file must be provided.

    The DaisyUI CSS classes are applied via the widget attrs dict —
    this keeps the template clean (no manual class="" on inputs).
    """

    yearly_csv = forms.FileField(
        required=False,
        label="Yearly deaths CSV  (yearly_deaths_by_clinic.csv)",
        # file-input and file-input-bordered are DaisyUI classes for styled
        # file upload buttons. w-full makes it span its container.
        widget=forms.ClearableFileInput(attrs={"class": "file-input file-input-bordered w-full"}),
    )
    monthly_csv = forms.FileField(
        required=False,
        label="Monthly deaths CSV  (monthly_deaths.csv)",
        widget=forms.ClearableFileInput(attrs={"class": "file-input file-input-bordered w-full"}),
    )

    def clean(self):
        """
        Cross-field validation: raises a non-field error if the user submits
        the form without choosing any file. This runs after each field's own
        validation, so cleaned_data is already populated here.
        """
        cleaned = super().clean()
        if not cleaned.get("yearly_csv") and not cleaned.get("monthly_csv"):
            raise forms.ValidationError("Upload at least one CSV file.")
        return cleaned


class YearlyRecordForm(forms.ModelForm):
    """
    ModelForm for creating/editing a YearlyRecord.
    Declaring widgets in Meta.widgets applies DaisyUI classes without
    needing a custom __init__ — the cleanest way to style ModelForms.
    The clinic field uses a Select widget with explicit choices rather than
    a free-text input to prevent typos like "Clinic 1" vs "clinic 1".
    """
    class Meta:
        model  = YearlyRecord
        fields = ["year", "births", "deaths", "clinic"]
        widgets = {
            "year":   forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
            "births": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
            "deaths": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
            "clinic": forms.Select(
                # Hard-coded choices match the values the CSV importer writes.
                choices=[("clinic 1", "Clinic 1"), ("clinic 2", "Clinic 2")],
                attrs={"class": "select select-bordered w-full"},
            ),
        }


class MonthlyRecordForm(forms.ModelForm):
    """
    ModelForm for creating/editing a MonthlyRecord.
    The date field uses type="date" so browsers render a native date-picker
    instead of a plain text input.
    """
    class Meta:
        model  = MonthlyRecord
        fields = ["date", "births", "deaths"]
        widgets = {
            # type="date" renders a browser date-picker (HTML5).
            "date":   forms.DateInput(attrs={"type": "date", "class": "input input-bordered w-full"}),
            "births": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
            "deaths": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
        }
```

---

## 7. Services (data layer)

`services.py` is a plain Python module (not a Django class) that contains
all data-intensive logic: CSV parsing, DataFrame construction, Chart.js JSON
serialisation, statistical analysis, and Matplotlib PNG generation.
Keeping this code out of views keeps views thin and makes the logic easy to
test and reuse.

```python
# analysis/services.py

import io
import json
import numpy as np
import pandas as pd
import matplotlib
# "Agg" is a non-interactive Matplotlib backend that renders to memory buffers.
# It must be set BEFORE importing pyplot, otherwise Matplotlib tries to open a
# display which fails on a headless server.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import date
from scipy import stats

from .models import YearlyRecord, MonthlyRecord

# Module-level constant: the handwashing pivot date as a pandas Timestamp.
# Using pd.Timestamp allows direct comparison with DataFrame date columns.
PIVOT = pd.Timestamp("1847-06-01")


# ─────────────────────────────────────────────────────────────────────────────
# CSV IMPORT
# Each importer: reads the uploaded file with pandas, wipes the existing table,
# then uses bulk_create for a single efficient INSERT rather than one per row.
# ─────────────────────────────────────────────────────────────────────────────

def import_yearly_csv(file_obj):
    """
    Parses an uploaded yearly_deaths_by_clinic.csv file and populates the
    YearlyRecord table from scratch.
    file_obj is a Django InMemoryUploadedFile (behaves like a file handle).
    """
    df = pd.read_csv(file_obj)
    YearlyRecord.objects.all().delete()   # wipe first to avoid duplicates
    YearlyRecord.objects.bulk_create([
        YearlyRecord(
            year=int(row["year"]),
            births=int(row["births"]),
            deaths=int(row["deaths"]),
            clinic=str(row["clinic"]).strip(),  # .strip() removes accidental spaces
        )
        for _, row in df.iterrows()
    ])


def import_monthly_csv(file_obj):
    """
    Parses an uploaded monthly_deaths.csv file and populates the
    MonthlyRecord table from scratch.
    parse_dates=["date"] tells pandas to convert that column to Timestamps
    so .date() can be called to get a Python date object for the model field.
    """
    df = pd.read_csv(file_obj, parse_dates=["date"])
    MonthlyRecord.objects.all().delete()
    MonthlyRecord.objects.bulk_create([
        MonthlyRecord(
            date=row["date"].date(),   # pandas Timestamp → Python date
            births=int(row["births"]),
            deaths=int(row["deaths"]),
        )
        for _, row in df.iterrows()
    ])


# ─────────────────────────────────────────────────────────────────────────────
# DATAFRAMES
# Convert the Django ORM queryset into a pandas DataFrame.
# .values() returns a ValuesQuerySet (list of dicts) which pandas can read
# directly. This avoids instantiating full model objects for every row.
# ─────────────────────────────────────────────────────────────────────────────

def yearly_to_dataframe():
    """Returns all YearlyRecord rows as a DataFrame with a proportion_deaths column."""
    qs = YearlyRecord.objects.values("year", "births", "deaths", "clinic")
    df = pd.DataFrame(list(qs))
    if not df.empty:
        df["proportion_deaths"] = (df["deaths"] / df["births"]).round(6)
    return df


def monthly_to_dataframe():
    """
    Returns all MonthlyRecord rows as a DataFrame sorted by date,
    with a proportion_deaths column and dates converted to Timestamps.
    """
    qs = MonthlyRecord.objects.values("date", "births", "deaths")
    df = pd.DataFrame(list(qs))
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])   # Python date → Timestamp for comparisons
        df["proportion_deaths"] = (df["deaths"] / df["births"]).round(6)
        df = df.sort_values("date").reset_index(drop=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# CHART.JS JSON DATA
# These functions return JSON strings that are injected directly into <script>
# blocks in templates as JavaScript objects.
# {"empty": True} is a sentinel value: the JS checks `if (cd && !cd.empty)`
# before calling the render functions so no error is thrown on an empty DB.
# ─────────────────────────────────────────────────────────────────────────────

def yearly_chart_data():
    """
    Builds the data object for renderClinicChart() in charts.js.
    Returns: { labels: [year,...], clinic1: [proportion,...], clinic2: [...] }
    """
    df = yearly_to_dataframe()
    if df.empty:
        return json.dumps({"empty": True})
    c1 = df[df["clinic"] == "clinic 1"].sort_values("year")
    c2 = df[df["clinic"] == "clinic 2"].sort_values("year")
    return json.dumps({
        "labels":  c1["year"].tolist(),
        "clinic1": c1["proportion_deaths"].tolist(),
        "clinic2": c2["proportion_deaths"].tolist(),
    })


def monthly_chart_data():
    """
    Builds the data object for renderMonthlyChart() in charts.js.
    Splits the records into two separate datasets at PIVOT (June 1847) so the
    JS can render them as two colour-coded line segments on the same chart.
    Returns: { labelsBefore, before, labelsAfter, after }
    """
    df = monthly_to_dataframe()
    if df.empty:
        return json.dumps({"empty": True})
    before = df[df["date"] < PIVOT]
    after  = df[df["date"] >= PIVOT]
    return json.dumps({
        "labelsBefore": [str(d.date()) for d in before["date"]],
        "before":       before["proportion_deaths"].tolist(),
        "labelsAfter":  [str(d.date()) for d in after["date"]],
        "after":        after["proportion_deaths"].tolist(),
    })


def bootstrap_chart_data_json(boot_diffs, ci_lower, ci_upper):
    """
    Converts the bootstrap difference list into a histogram-friendly JSON blob
    for renderBootstrapHistogram() in charts.js.
    np.histogram returns (counts, bin_edges); we take the bin midpoints as labels.
    """
    counts, edges = np.histogram(boot_diffs, bins=40)
    return json.dumps({
        "labels":   [round((edges[i] + edges[i + 1]) / 2, 5) for i in range(len(counts))],
        "counts":   counts.tolist(),
        "ci_lower": round(ci_lower, 5),   # used by charts.js to colour bars outside the CI
        "ci_upper": round(ci_upper, 5),
    })


# ─────────────────────────────────────────────────────────────────────────────
# FULL ANALYSIS
# Called once by AnalysisView.get_context_data(). Returns a single dict that
# is merged into the template context with ctx.update(services.run_full_analysis()).
# ─────────────────────────────────────────────────────────────────────────────

def run_full_analysis():
    """
    Runs the complete Semmelweis analysis and returns a context dict with:
      clinic_comparison   – list of {year, clinic1, clinic2} dicts for the table
      yearly_chart_data   – JSON string for Chart.js
      monthly_chart_data  – JSON string for Chart.js
      mean_before         – mean proportion deaths before June 1847
      mean_after          – mean proportion deaths after June 1847
      mean_diff           – difference (after - before)
      bootstrap_chart_data– JSON string for Chart.js histogram
      ci_lower / ci_upper – 2.5th and 97.5th percentiles of bootstrap distribution
      ci_lower_pct / ci_upper_pct – same values as percentages for display
      t_stat / p_value    – Welch's t-test results
      p_value_fmt         – formatted p-value string (scientific notation)
      significant         – bool: True if p < 0.05
    """
    ctx = {}

    # ── Clinic comparison table (yearly) ──────────────────────────────────────
    ydf = yearly_to_dataframe()
    if not ydf.empty:
        # set_index makes year-based lookup via c1[year] possible.
        c1 = ydf[ydf["clinic"] == "clinic 1"].set_index("year")["proportion_deaths"]
        c2 = ydf[ydf["clinic"] == "clinic 2"].set_index("year")["proportion_deaths"]
        years = sorted(set(c1.index) | set(c2.index))
        ctx["clinic_comparison"] = [
            {
                "year":    y,
                "clinic1": round(c1[y], 4) if y in c1.index else "—",
                "clinic2": round(c2[y], 4) if y in c2.index else "—",
            }
            for y in years
        ]
    else:
        ctx["clinic_comparison"] = []

    ctx["yearly_chart_data"] = yearly_chart_data()

    # ── Monthly handwashing effect ─────────────────────────────────────────────
    mdf = monthly_to_dataframe()
    ctx["monthly_chart_data"] = monthly_chart_data()

    if not mdf.empty:
        before_s = mdf[mdf["date"] < PIVOT]["proportion_deaths"]
        after_s  = mdf[mdf["date"] >= PIVOT]["proportion_deaths"]
        ctx["mean_before"] = round(float(before_s.mean()), 4)
        ctx["mean_after"]  = round(float(after_s.mean()),  4)
        # mean_diff is negative: after < before, confirming deaths fell.
        ctx["mean_diff"]   = round(float(after_s.mean() - before_s.mean()), 4)
    else:
        ctx.update(mean_before=0, mean_after=0, mean_diff=0)
        before_s = after_s = pd.Series(dtype=float)

    # ── Bootstrap 95 % Confidence Interval ────────────────────────────────────
    # We resample the before and after groups 3 000 times with replacement and
    # compute the mean difference each time. The 2.5th and 97.5th percentiles
    # of the resulting distribution are the 95 % CI bounds.
    # np.random.default_rng(42): seed=42 makes results reproducible.
    if len(before_s) > 1 and len(after_s) > 1:
        rng = np.random.default_rng(42)
        boot_diffs = [
            rng.choice(after_s.values,  size=len(after_s),  replace=True).mean() -
            rng.choice(before_s.values, size=len(before_s), replace=True).mean()
            for _ in range(3000)
        ]
        ci_lower = float(np.quantile(boot_diffs, 0.025))
        ci_upper = float(np.quantile(boot_diffs, 0.975))
        ctx["bootstrap_chart_data"] = bootstrap_chart_data_json(boot_diffs, ci_lower, ci_upper)
    else:
        ci_lower = ci_upper = 0.0
        ctx["bootstrap_chart_data"] = json.dumps({"empty": True})

    ctx["ci_lower"]     = round(ci_lower, 4)
    ctx["ci_upper"]     = round(ci_upper, 4)
    # abs() because ci_lower is negative (deaths went down); *100 for display as %
    ctx["ci_lower_pct"] = round(abs(ci_lower) * 100, 2)
    ctx["ci_upper_pct"] = round(abs(ci_upper) * 100, 2)

    # ── Welch's t-test ─────────────────────────────────────────────────────────
    # equal_var=False → Welch's variant, which does NOT assume equal variances.
    # This is the safer default when comparing two independent groups.
    if len(before_s) > 1 and len(after_s) > 1:
        t_stat, p_value = stats.ttest_ind(before_s, after_s, equal_var=False)
    else:
        t_stat = p_value = float("nan")

    ctx["t_stat"]      = round(float(t_stat), 4)
    ctx["p_value"]     = float(p_value)
    # f"{p_value:.2e}" formats as scientific notation, e.g. "1.23e-10".
    # The `p_value != p_value` check is a NaN test (NaN is the only float not equal to itself).
    ctx["p_value_fmt"] = f"{p_value:.2e}" if not (p_value != p_value) else "N/A"
    ctx["significant"] = (p_value < 0.05) if not (p_value != p_value) else False

    return ctx


# ─────────────────────────────────────────────────────────────────────────────
# PNG EXPORTS
# Each function builds a Matplotlib figure, converts it to PNG bytes via a
# BytesIO buffer, and closes the figure to free memory.
# ─────────────────────────────────────────────────────────────────────────────

def _fig_to_png(fig):
    """
    Shared helper: saves a Matplotlib figure to an in-memory PNG byte string.
    bbox_inches="tight" crops whitespace around the chart.
    dpi=150 gives a good balance of resolution and file size.
    plt.close(fig) is essential — without it each download call leaks a figure
    object and Matplotlib eventually logs a warning about too many open figures.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)       # rewind to the start so .read() returns the full content
    return buf.read()


def clinic_comparison_chart_png():
    """
    Generates a line chart comparing death proportions for Clinic 1 vs Clinic 2
    across years 1841–1846.
    """
    df = yearly_to_dataframe()
    fig, ax = plt.subplots(figsize=(8, 4))
    if not df.empty:
        for label, grp in df.groupby("clinic"):
            grp = grp.sort_values("year")
            ax.plot(grp["year"], grp["proportion_deaths"], marker="o", label=label)
        ax.legend()
    ax.set_xlabel("Year")
    ax.set_ylabel("Proportion of deaths")
    ax.set_title("Death Proportion by Clinic (1841–1846)")
    return _fig_to_png(fig)


def monthly_proportion_chart_png():
    """
    Generates a line chart of monthly death proportions, with the before and
    after handwashing periods drawn in separate colours and a vertical dashed
    line at the pivot date.
    """
    df = monthly_to_dataframe()
    fig, ax = plt.subplots(figsize=(10, 4))
    if not df.empty:
        before = df[df["date"] < PIVOT].sort_values("date")
        after  = df[df["date"] >= PIVOT].sort_values("date")
        ax.plot(before["date"], before["proportion_deaths"],
                color="tab:red",   label="Before handwashing")
        ax.plot(after["date"],  after["proportion_deaths"],
                color="tab:green", label="After handwashing")
        ax.axvline(PIVOT, color="gray", linestyle="--", linewidth=1)
        ax.legend()
    ax.set_ylabel("Proportion of deaths")
    ax.set_title("Monthly Proportion of Deaths — Clinic 1")
    return _fig_to_png(fig)


def bootstrap_histogram_png():
    """
    Generates a histogram of the bootstrap distribution (3 000 resamples)
    with vertical dashed lines at the 2.5th and 97.5th percentile (the CI bounds).
    """
    mdf = monthly_to_dataframe()
    fig, ax = plt.subplots(figsize=(8, 4))
    if not mdf.empty:
        before_s = mdf[mdf["date"] < PIVOT]["proportion_deaths"]
        after_s  = mdf[mdf["date"] >= PIVOT]["proportion_deaths"]
        rng = np.random.default_rng(42)
        boot_diffs = [
            rng.choice(after_s.values,  size=len(after_s),  replace=True).mean() -
            rng.choice(before_s.values, size=len(before_s), replace=True).mean()
            for _ in range(3000)
        ]
        ci = np.quantile(boot_diffs, [0.025, 0.975])
        ax.hist(boot_diffs, bins=40, color="steelblue", alpha=0.7)
        ax.axvline(ci[0], color="red",   linestyle="--", label=f"2.5%  = {ci[0]:.4f}")
        ax.axvline(ci[1], color="green", linestyle="--", label=f"97.5% = {ci[1]:.4f}")
        ax.legend()
    ax.set_xlabel("Mean difference in proportion deaths")
    ax.set_ylabel("Frequency")
    ax.set_title("Bootstrap Distribution (3 000 resamples)")
    return _fig_to_png(fig)
```

---

## 8. Views

```python
# analysis/views.py

# Django's generic class-based views handle the boilerplate for list/create/
# update/delete operations. We override only what we need to customise.
from django.views.generic import (
    TemplateView,   # renders a template with a context — no model needed
    ListView,       # renders a list of model instances
    CreateView,     # renders and processes a creation form
    UpdateView,     # renders and processes an edit form
    DeleteView,     # renders and processes a deletion confirmation
)
from django.views import View       # base class for views that need custom GET/POST
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse

from .models import YearlyRecord, MonthlyRecord
from .forms import CSVUploadForm, YearlyRecordForm, MonthlyRecordForm
from . import services


# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD
# Uses the base View class directly because we need explicit GET and POST
# methods with custom logic (calling services functions).
# ─────────────────────────────────────────────────────────────────────────────

class UploadCSVView(View):
    template_name = "analysis/upload.html"

    def get(self, request):
        # Show an empty upload form.
        return render(request, self.template_name, {"form": CSVUploadForm()})

    def post(self, request):
        # request.FILES contains the uploaded file objects.
        form = CSVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            # Re-render the form with validation errors.
            return render(request, self.template_name, {"form": form})
        # call the appropriate importer only for the files that were provided
        if form.cleaned_data.get("yearly_csv"):
            services.import_yearly_csv(form.cleaned_data["yearly_csv"])
        if form.cleaned_data.get("monthly_csv"):
            services.import_monthly_csv(form.cleaned_data["monthly_csv"])
        # Post-Redirect-Get pattern: redirect after a successful POST to
        # prevent the browser from re-submitting on refresh.
        return redirect("analysis:dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD (homepage)
# TemplateView is used because this page does not list a single model — it
# shows summary stats and charts from two different models.
# ─────────────────────────────────────────────────────────────────────────────

class DashboardView(TemplateView):
    template_name = "analysis/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["yearly_count"]       = YearlyRecord.objects.count()
        ctx["monthly_count"]      = MonthlyRecord.objects.count()
        # has_data drives the "no data" warning banner in the template.
        ctx["has_data"]           = ctx["yearly_count"] > 0 or ctx["monthly_count"] > 0
        # JSON strings that Chart.js in the template will deserialise.
        ctx["yearly_chart_data"]  = services.yearly_chart_data()
        ctx["monthly_chart_data"] = services.monthly_chart_data()
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# YEARLY — CRUD
# All four generic views share the same form template (yearly_form.html) for
# Create and Update, and confirm_delete.html for Delete.
# success_url uses reverse_lazy() instead of reverse() because the URLconf has
# not been loaded yet when the class body is evaluated at import time.
# ─────────────────────────────────────────────────────────────────────────────

class YearlyListView(ListView):
    model               = YearlyRecord
    template_name       = "analysis/yearly_list.html"
    context_object_name = "records"   # name used in the template for the queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Provide pre-filtered querysets so the template can show per-clinic tabs
        # without needing to filter in the template layer.
        ctx["clinic1"]    = YearlyRecord.objects.filter(clinic="clinic 1")
        ctx["clinic2"]    = YearlyRecord.objects.filter(clinic="clinic 2")
        ctx["chart_data"] = services.yearly_chart_data()
        return ctx


class YearlyCreateView(CreateView):
    model         = YearlyRecord
    form_class    = YearlyRecordForm
    template_name = "analysis/yearly_form.html"
    success_url   = reverse_lazy("analysis:yearly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 'title' and 'cancel_url' are used by the shared yearly_form.html template.
        ctx["title"]      = "Add Yearly Record"
        ctx["cancel_url"] = reverse_lazy("analysis:yearly-list")
        return ctx


class YearlyUpdateView(UpdateView):
    model         = YearlyRecord
    form_class    = YearlyRecordForm
    template_name = "analysis/yearly_form.html"
    success_url   = reverse_lazy("analysis:yearly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # self.object is the model instance being edited — set by UpdateView.
        ctx["title"]      = f"Edit Yearly Record — {self.object}"
        ctx["cancel_url"] = reverse_lazy("analysis:yearly-list")
        return ctx


class YearlyDeleteView(DeleteView):
    model         = YearlyRecord
    template_name = "analysis/confirm_delete.html"
    success_url   = reverse_lazy("analysis:yearly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("analysis:yearly-list")
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# MONTHLY — CRUD
# Same structure as the Yearly CRUD group above.
# ─────────────────────────────────────────────────────────────────────────────

class MonthlyListView(ListView):
    model               = MonthlyRecord
    template_name       = "analysis/monthly_list.html"
    context_object_name = "records"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["chart_data"]        = services.monthly_chart_data()
        # Pass the pivot date string so the template can display it without
        # hard-coding it in the HTML.
        ctx["handwashing_start"] = MonthlyRecord.HANDWASHING_START
        return ctx


class MonthlyCreateView(CreateView):
    model         = MonthlyRecord
    form_class    = MonthlyRecordForm
    template_name = "analysis/monthly_form.html"
    success_url   = reverse_lazy("analysis:monthly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]      = "Add Monthly Record"
        ctx["cancel_url"] = reverse_lazy("analysis:monthly-list")
        return ctx


class MonthlyUpdateView(UpdateView):
    model         = MonthlyRecord
    form_class    = MonthlyRecordForm
    template_name = "analysis/monthly_form.html"
    success_url   = reverse_lazy("analysis:monthly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]      = f"Edit Monthly Record — {self.object}"
        ctx["cancel_url"] = reverse_lazy("analysis:monthly-list")
        return ctx


class MonthlyDeleteView(DeleteView):
    model         = MonthlyRecord
    template_name = "analysis/confirm_delete.html"
    success_url   = reverse_lazy("analysis:monthly-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("analysis:monthly-list")
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS
# TemplateView again — one call to services.run_full_analysis() populates the
# entire context for the analysis_results.html template.
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisView(TemplateView):
    template_name = "analysis/analysis_results.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # run_full_analysis() returns a dict; update() merges it into ctx.
        ctx.update(services.run_full_analysis())
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOADS
# Each view calls a services function that returns raw PNG bytes or a pandas
# DataFrame. The response Content-Disposition header triggers a browser download.
# ─────────────────────────────────────────────────────────────────────────────

class DownloadYearlyCSVView(View):
    def get(self, request):
        df = services.yearly_to_dataframe()
        resp = HttpResponse(content_type="text/csv")
        # attachment; filename= tells the browser to download rather than display.
        resp["Content-Disposition"] = 'attachment; filename="yearly_deaths.csv"'
        df.to_csv(resp, index=False)  # write CSV directly into the response object
        return resp


class DownloadMonthlyCSVView(View):
    def get(self, request):
        df = services.monthly_to_dataframe()
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="monthly_deaths.csv"'
        df.to_csv(resp, index=False)
        return resp


class DownloadClinicChartView(View):
    def get(self, request):
        png = services.clinic_comparison_chart_png()  # raw PNG bytes
        resp = HttpResponse(content_type="image/png")
        resp["Content-Disposition"] = 'attachment; filename="clinic_comparison.png"'
        resp.write(png)
        return resp


class DownloadMonthlyChartView(View):
    def get(self, request):
        png = services.monthly_proportion_chart_png()
        resp = HttpResponse(content_type="image/png")
        resp["Content-Disposition"] = 'attachment; filename="monthly_proportion.png"'
        resp.write(png)
        return resp


class DownloadBootstrapChartView(View):
    def get(self, request):
        png = services.bootstrap_histogram_png()
        resp = HttpResponse(content_type="image/png")
        resp["Content-Disposition"] = 'attachment; filename="bootstrap_ci.png"'
        resp.write(png)
        return resp
```

---

## 9. URLs

```python
# semmelweis_project/urls.py
# The root URLconf: includes the analysis app's urls under the empty prefix (""),
# meaning all analysis URLs are available at the site root.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # namespace="analysis" means URL names are referenced as "analysis:dashboard" etc.
    path("", include("analysis.urls", namespace="analysis")),
# In development, Django serves media files (uploaded images) itself.
# static() returns an empty list in production when DEBUG=False.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```python
# analysis/urls.py
# App-level URLconf. Each path() maps a URL pattern to a view class.
# app_name must match the namespace declared in the root urls.py include().

from django.urls import path
from . import views

app_name = "analysis"

urlpatterns = [
    # ── Dashboard & upload ────────────────────────────────────────────────────
    path("",        views.DashboardView.as_view(), name="dashboard"),
    path("upload/", views.UploadCSVView.as_view(),  name="upload"),

    # ── Yearly CRUD ───────────────────────────────────────────────────────────
    # List:   GET  /yearly/
    # Create: GET  /yearly/add/           (show form)
    #         POST /yearly/add/           (save record)
    # Update: GET  /yearly/<pk>/edit/     (show pre-filled form)
    #         POST /yearly/<pk>/edit/     (save changes)
    # Delete: GET  /yearly/<pk>/delete/   (show confirmation)
    #         POST /yearly/<pk>/delete/   (perform deletion)
    path("yearly/",                  views.YearlyListView.as_view(),   name="yearly-list"),
    path("yearly/add/",              views.YearlyCreateView.as_view(), name="yearly-create"),
    path("yearly/<int:pk>/edit/",    views.YearlyUpdateView.as_view(), name="yearly-update"),
    path("yearly/<int:pk>/delete/",  views.YearlyDeleteView.as_view(), name="yearly-delete"),

    # ── Monthly CRUD ──────────────────────────────────────────────────────────
    path("monthly/",                 views.MonthlyListView.as_view(),   name="monthly-list"),
    path("monthly/add/",             views.MonthlyCreateView.as_view(), name="monthly-create"),
    path("monthly/<int:pk>/edit/",   views.MonthlyUpdateView.as_view(), name="monthly-update"),
    path("monthly/<int:pk>/delete/", views.MonthlyDeleteView.as_view(), name="monthly-delete"),

    # ── Analysis ──────────────────────────────────────────────────────────────
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),

    # ── Downloads ─────────────────────────────────────────────────────────────
    path("download/yearly-csv/",      views.DownloadYearlyCSVView.as_view(),     name="dl-yearly-csv"),
    path("download/monthly-csv/",     views.DownloadMonthlyCSVView.as_view(),    name="dl-monthly-csv"),
    path("download/clinic-chart/",    views.DownloadClinicChartView.as_view(),   name="dl-clinic-chart"),
    path("download/monthly-chart/",   views.DownloadMonthlyChartView.as_view(),  name="dl-monthly-chart"),
    path("download/bootstrap-chart/", views.DownloadBootstrapChartView.as_view(),name="dl-bootstrap-chart"),
]
```

---

## 10. Templates

### DaisyUI Tab Pattern

All tabbed sections in this app use DaisyUI v4's **radio-input** pattern.
The CSS selector `.tab-content` is shown only when its sibling radio input is
`:checked`. The rule is:

```
radio input → immediately followed by → .tab-content div
```

If any other element appears between them the tab panel will never be visible.

```html
<!-- ✅ Correct: radio and tab-content are immediate siblings -->
<div role="tablist" class="tabs tabs-boxed">
  <input type="radio" name="my-tabs" role="tab" class="tab" aria-label="Tab 1" checked />
  <div role="tabpanel" class="tab-content ...">Content 1</div>

  <input type="radio" name="my-tabs" role="tab" class="tab" aria-label="Tab 2" />
  <div role="tabpanel" class="tab-content ...">Content 2</div>
</div>
```

---

### `base.html`

```html
<!-- templates/base.html -->
<!-- Every page extends this template via  "extends" "base.html".
     It loads all shared dependencies from CDN (DaisyUI, Tailwind, Chart.js)
     and renders the top navigation bar. -->
<!DOCTYPE html>
<html lang="en" data-theme="light">
<!-- data-theme="light" activates DaisyUI's light colour palette globally. -->
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}Semmelweis{% endblock %}</title>

  <!-- DaisyUI (component styles) must load before Tailwind (utility classes). -->
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4/dist/full.min.css" rel="stylesheet" />
  <!-- Tailwind Play CDN: for development only. Use the CLI build for production. -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js v4: interactive canvas charts rendered in the browser. -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>

  {% load static %}
  <!-- defer: the script is downloaded in parallel but executed after the HTML is parsed.
       This ensures Chart.js is loaded before charts.js runs. -->
  <script src="{% static 'js/charts.js' %}" defer></script>
</head>
<body class="min-h-screen bg-base-200">

  <!-- Navbar: bg-base-100 is white in the light theme; shadow adds a subtle drop shadow. -->
  <nav class="navbar bg-base-100 shadow px-4 gap-2">
    <div class="flex-1">
      <!-- btn-ghost: transparent button style. text-xl makes the brand name larger. -->
      <a href="{% url 'analysis:dashboard' %}" class="btn btn-ghost text-xl font-bold">
        🧼 Semmelweis
      </a>
    </div>
    <div class="flex-none flex gap-2">
      <a href="{% url 'analysis:upload' %}"       class="btn btn-sm btn-outline">Upload CSV</a>
      <a href="{% url 'analysis:yearly-list' %}"  class="btn btn-sm btn-outline">Yearly</a>
      <a href="{% url 'analysis:monthly-list' %}" class="btn btn-sm btn-outline">Monthly</a>
      <!-- btn-primary uses the DaisyUI primary colour (blue by default). -->
      <a href="{% url 'analysis:analysis' %}"     class="btn btn-sm btn-primary">Analysis</a>
    </div>
  </nav>

  <!-- max-w-6xl keeps the content from stretching too wide on large screens. -->
  <main class="container mx-auto p-4 max-w-6xl">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

---

### `upload.html`

```html
<!-- templates/analysis/upload.html -->
<!-- A simple card form for uploading CSV files.
     enctype="multipart/form-data" is required for file uploads — without it
     the file content is never sent to the server. -->
{% extends "base.html" %}
{% block title %}Upload CSV{% endblock %}

{% block content %}
<div class="card bg-base-100 shadow max-w-lg mx-auto mt-8">
  <div class="card-body">
    <h2 class="card-title">Import CSV Files</h2>
    <p class="text-sm text-gray-500 mb-2">
      Upload <code>yearly_deaths_by_clinic.csv</code> and/or
      <code>monthly_deaths.csv</code>. Existing records are replaced on each import.
    </p>

    <!-- non_field_errors: form-level errors from clean() (e.g. "Upload at least one file"). -->
    {% if form.non_field_errors %}
      <div class="alert alert-error text-sm mb-2">{{ form.non_field_errors }}</div>
    {% endif %}

    <!-- multipart/form-data is mandatory for file uploads. -->
    <form method="post" enctype="multipart/form-data" class="space-y-4">
      {% csrf_token %}
      <!-- Loop over each form field rather than listing them individually.
           This means adding a field to the form class automatically renders it here. -->
      {% for field in form %}
        <div class="form-control">
          <label class="label"><span class="label-text font-medium">{{ field.label }}</span></label>
          {{ field }}  <!-- renders the widget (file input) with its DaisyUI classes -->
          {% if field.errors %}
            <span class="text-error text-xs mt-1">{{ field.errors.0 }}</span>
          {% endif %}
        </div>
      {% endfor %}
      <div class="card-actions justify-end pt-2">
        <a href="{% url 'analysis:dashboard' %}" class="btn btn-ghost btn-sm">Cancel</a>
        <button class="btn btn-primary btn-sm">Import</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

---

### `dashboard.html`

```html
<!-- templates/analysis/dashboard.html -->
<!-- The homepage. Uses DaisyUI radio-input tabs to show four panels:
     Overview (bio + stats), Yearly chart, Monthly chart, Analysis link.
     IMPORTANT TAB RULE: each <input type="radio"> must be immediately followed
     by its <div role="tabpanel"> with no elements in between. -->
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}

{% block content %}
<h1 class="text-2xl font-bold my-4">Semmelweis Handwashing Analysis</h1>

<!-- Conditional warning banner shown when no data has been imported yet. -->
{% if not has_data %}
<div class="alert alert-warning mb-4">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0" fill="none"
       viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
  </svg>
  <span>No data loaded yet.
    <a href="{% url 'analysis:upload' %}" class="link font-semibold">Upload CSV files</a>
    to begin.
  </span>
</div>
{% endif %}

<!-- DaisyUI tabs: role="tablist" + tabs-boxed gives the pill/box style. -->
<div role="tablist" class="tabs tabs-boxed mb-0 bg-base-100 rounded-b-none px-2 pt-2">

  <!-- Tab 1: Overview -->
  <input type="radio" name="dash-tabs" role="tab" class="tab"
         aria-label="Overview" checked="checked" />
  <div role="tabpanel" class="tab-content col-span-4 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <div class="flex flex-col md:flex-row gap-6 items-start">
      <!-- Portrait served from media/uploads/ via the MEDIA_URL setting. -->
      <img src="/media/uploads/semmelweis.jpeg"
           alt="Dr. Ignaz Semmelweis"
           class="w-36 rounded shadow-md shrink-0" />
      <div>
        <h2 class="text-xl font-semibold mb-2">Dr. Ignaz Semmelweis (1818–1865)</h2>
        <p class="text-sm leading-relaxed max-w-prose text-gray-700">
          A Hungarian physician active at the Vienna General Hospital.
          In the early 1840s, up to <strong>10 %</strong> of women who gave birth
          there died of <em>childbed fever</em>. Semmelweis discovered the cause:
          doctors delivered babies immediately after performing autopsies, without
          washing their hands. He mandated handwashing in <strong>June 1847</strong>,
          cutting mortality dramatically — but was ridiculed by his peers and
          eventually forced to leave Vienna.
        </p>

        <!-- stats-horizontal: lays the stat boxes in a row rather than a column. -->
        <div class="stats stats-horizontal shadow mt-4 text-sm">
          <div class="stat py-3 px-5">
            <div class="stat-title text-xs">Yearly records loaded</div>
            <!-- text-primary: the DaisyUI primary colour (blue). -->
            <div class="stat-value text-primary text-2xl">{{ yearly_count }}</div>
          </div>
          <div class="stat py-3 px-5">
            <div class="stat-title text-xs">Monthly records loaded</div>
            <div class="stat-value text-secondary text-2xl">{{ monthly_count }}</div>
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <a href="{% url 'analysis:upload' %}"   class="btn btn-sm btn-outline">Upload CSV</a>
          <a href="{% url 'analysis:analysis' %}" class="btn btn-sm btn-primary">Run Analysis →</a>
        </div>
      </div>
    </div>
  </div>

  <!-- Tab 2: Yearly chart -->
  <input type="radio" name="dash-tabs" role="tab" class="tab" aria-label="Yearly Data" />
  <div role="tabpanel" class="tab-content col-span-4 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold">Yearly Deaths by Clinic (1841–1846)</h2>
      <div class="flex gap-2">
        <a href="{% url 'analysis:yearly-list' %}"    class="btn btn-sm btn-outline">Full CRUD view</a>
        <a href="{% url 'analysis:dl-yearly-csv' %}"  class="btn btn-sm btn-outline">⬇ CSV</a>
        <a href="{% url 'analysis:dl-clinic-chart' %}"class="btn btn-sm btn-outline">⬇ PNG</a>
      </div>
    </div>
    <!-- Only render the canvas when data exists; otherwise show an info alert. -->
    {% if yearly_count %}
      <!-- h-72 gives the canvas a fixed height so Chart.js can calculate dimensions. -->
      <div class="bg-white rounded-lg p-3 shadow-inner h-72">
        <canvas id="dashClinicChart"></canvas>
      </div>
    {% else %}
      <div class="alert alert-info text-sm">
        No yearly data yet. <a href="{% url 'analysis:upload' %}" class="link">Upload the CSV</a>.
      </div>
    {% endif %}
  </div>

  <!-- Tab 3: Monthly chart -->
  <input type="radio" name="dash-tabs" role="tab" class="tab" aria-label="Monthly Data" />
  <div role="tabpanel" class="tab-content col-span-4 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold">Monthly Proportion of Deaths — Clinic 1</h2>
      <div class="flex gap-2">
        <a href="{% url 'analysis:monthly-list' %}"    class="btn btn-sm btn-outline">Full CRUD view</a>
        <a href="{% url 'analysis:dl-monthly-csv' %}"  class="btn btn-sm btn-outline">⬇ CSV</a>
        <a href="{% url 'analysis:dl-monthly-chart' %}"class="btn btn-sm btn-outline">⬇ PNG</a>
      </div>
    </div>
    {% if monthly_count %}
      <div class="bg-white rounded-lg p-3 shadow-inner h-72">
        <canvas id="dashMonthlyChart"></canvas>
      </div>
    {% else %}
      <div class="alert alert-info text-sm">
        No monthly data yet. <a href="{% url 'analysis:upload' %}" class="link">Upload the CSV</a>.
      </div>
    {% endif %}
  </div>

  <!-- Tab 4: Analysis link -->
  <input type="radio" name="dash-tabs" role="tab" class="tab" aria-label="Statistical Analysis" />
  <div role="tabpanel" class="tab-content col-span-4 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <p class="text-sm text-gray-600 mb-4">
      The full analysis page runs the complete Semmelweis notebook:
      clinic comparison, handwashing effect, bootstrap confidence interval,
      and Welch's t-test.
    </p>
    <a href="{% url 'analysis:analysis' %}" class="btn btn-primary">
      Open Full Analysis →
    </a>
  </div>
</div>

<script>
  // DOMContentLoaded: wait until the page is fully parsed AND the deferred
  // charts.js has been executed before calling the render functions.
  document.addEventListener("DOMContentLoaded", function () {
    // {{ yearly_chart_data|safe }} injects the JSON string directly into JS.
    // |safe tells Django's template engine not to HTML-escape the string.
    const cd = {{ yearly_chart_data|safe }};
    const md = {{ monthly_chart_data|safe }};
    // Guard: only render if the data is not the empty sentinel {empty: true}.
    if (cd && !cd.empty) renderClinicChart("dashClinicChart", cd);
    if (md && !md.empty) renderMonthlyChart("dashMonthlyChart", md);
  });
</script>
{% endblock %}
```

---

### `yearly_list.html`

```html
<!-- templates/analysis/yearly_list.html -->
<!-- Shows the clinic comparison chart plus three tabs:
     Clinic 1 records | Clinic 2 records | All records.
     Each tab panel uses the _yearly_table.html partial. -->
{% extends "base.html" %}
{% block title %}Yearly Data{% endblock %}

{% block content %}
<div class="flex justify-between items-center my-4">
  <h1 class="text-xl font-bold">Yearly Deaths by Clinic</h1>
  <div class="flex gap-2">
    <a href="{% url 'analysis:yearly-create' %}"  class="btn btn-sm btn-primary">+ Add record</a>
    <a href="{% url 'analysis:dl-yearly-csv' %}"  class="btn btn-sm btn-outline">⬇ CSV</a>
    <a href="{% url 'analysis:dl-clinic-chart' %}"class="btn btn-sm btn-outline">⬇ Chart PNG</a>
  </div>
</div>

<!-- Chart card: h-80 gives the canvas a defined height. -->
<div class="card bg-base-100 shadow mb-6">
  <div class="card-body">
    {% if records %}
      <div class="h-80"><canvas id="clinicChart"></canvas></div>
    {% else %}
      <p class="text-sm text-gray-500">No records yet.</p>
    {% endif %}
  </div>
</div>

<!-- DaisyUI tabs: alternating radio / tab-content siblings. -->
<div role="tablist" class="tabs tabs-boxed mb-0 bg-base-100 rounded-b-none px-2 pt-2">
  <input type="radio" name="ytabs" role="tab" class="tab"
         aria-label="Clinic 1" checked="checked" />
  <div role="tabpanel" class="tab-content col-span-3 bg-base-100 rounded-b-box rounded-tr-box p-4">
    <!-- "include" renders the partial template and passes 'rows' as the context variable.
         The 'with rows=clinic1' syntax scopes clinic1 to the variable name 'rows'
         expected by _yearly_table.html. -->
    {% include "analysis/_yearly_table.html" with rows=clinic1 %}
  </div>

  <input type="radio" name="ytabs" role="tab" class="tab" aria-label="Clinic 2" />
  <div role="tabpanel" class="tab-content col-span-3 bg-base-100 rounded-b-box rounded-tr-box p-4">
    {% include "analysis/_yearly_table.html" with rows=clinic2 %}
  </div>

  <input type="radio" name="ytabs" role="tab" class="tab" aria-label="All Records" />
  <div role="tabpanel" class="tab-content col-span-3 bg-base-100 rounded-b-box rounded-tr-box p-4">
    {% include "analysis/_yearly_table.html" with rows=records %}
  </div>
</div>

<script>
  document.addEventListener("DOMContentLoaded", function () {
    const cd = {{ chart_data|safe }};
    if (cd && !cd.empty) renderClinicChart("clinicChart", cd);
  });
</script>
{% endblock %}
```

---

### `_yearly_table.html` (partial)

```html
<!-- templates/analysis/_yearly_table.html -->
<!-- Reusable partial: renders a zebra-striped table for any queryset passed
     in as the 'rows' variable. The leading underscore in the filename signals
     that this is a partial, not a standalone page. -->
{% if rows %}
<div class="overflow-x-auto">
  <!-- table-zebra: alternating row background colours (DaisyUI).
       table-sm:    compact row padding. -->
  <table class="table table-zebra table-sm w-full">
    <thead>
      <tr>
        <th>Year</th>
        <th>Clinic</th>
        <th>Births</th>
        <th>Deaths</th>
        <th>Proportion</th>
        <th class="text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td>{{ r.year }}</td>
        <td>{{ r.clinic }}</td>
        <td>{{ r.births }}</td>
        <td>{{ r.deaths }}</td>
        <!-- floatformat:4 rounds to 4 decimal places for compact display. -->
        <td>{{ r.proportion_deaths|floatformat:4 }}</td>
        <td class="text-right">
          <!-- btn-xs: extra-small button, fits in a table cell. -->
          <a href="{% url 'analysis:yearly-update' r.pk %}"
             class="btn btn-xs btn-ghost">Edit</a>
          <a href="{% url 'analysis:yearly-delete' r.pk %}"
             class="btn btn-xs btn-error btn-outline">Delete</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
  <!-- Shown when the filtered queryset (e.g. clinic1) is empty. -->
  <p class="text-sm text-gray-500 py-4">No records for this clinic.</p>
{% endif %}
```

---

### `yearly_form.html`

```html
<!-- templates/analysis/yearly_form.html -->
<!-- Shared by YearlyCreateView and YearlyUpdateView.
     The 'title' context variable distinguishes the two uses.
     'cancel_url' is provided by get_context_data() in each view. -->
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="card bg-base-100 shadow max-w-md mx-auto mt-8">
  <div class="card-body">
    <h2 class="card-title">{{ title }}</h2>

    <!-- method="post": form submissions go to the same URL that rendered the form.
         Django's URL dispatcher routes them to the same view's POST handler. -->
    <form method="post" class="space-y-4 mt-2">
      {% csrf_token %}
      {% for field in form %}
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">{{ field.label }}</span>
          </label>
          {{ field }}
          {% if field.errors %}
            <span class="text-error text-xs mt-1">{{ field.errors.0 }}</span>
          {% endif %}
        </div>
      {% endfor %}

      <div class="card-actions justify-end pt-2">
        <!-- cancel_url is reverse_lazy("analysis:yearly-list") from the view. -->
        <a href="{{ cancel_url }}" class="btn btn-ghost btn-sm">Cancel</a>
        <button class="btn btn-primary btn-sm">Save</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

---

### `monthly_list.html`

```html
<!-- templates/analysis/monthly_list.html -->
<!-- Displays the monthly proportion chart plus a full table with Before/After
     period badges and edit/delete actions on each row. -->
{% extends "base.html" %}
{% block title %}Monthly Data{% endblock %}

{% block content %}
<div class="flex justify-between items-center my-4">
  <h1 class="text-xl font-bold">Monthly Deaths — Clinic 1</h1>
  <div class="flex gap-2">
    <a href="{% url 'analysis:monthly-create' %}"  class="btn btn-sm btn-primary">+ Add record</a>
    <a href="{% url 'analysis:dl-monthly-csv' %}"  class="btn btn-sm btn-outline">⬇ CSV</a>
    <a href="{% url 'analysis:dl-monthly-chart' %}"class="btn btn-sm btn-outline">⬇ Chart PNG</a>
  </div>
</div>

<div class="card bg-base-100 shadow mb-4">
  <div class="card-body">
    {% if records %}
      <div class="h-80"><canvas id="monthlyPropChart"></canvas></div>
      <p class="text-xs text-gray-400 mt-1">
        Red = before handwashing  ·  Green = after
        <!-- handwashing_start is passed from MonthlyListView.get_context_data() -->
        (mandatory from {{ handwashing_start }})
      </p>
    {% else %}
      <p class="text-sm text-gray-500">No records yet.</p>
    {% endif %}
  </div>
</div>

<div class="card bg-base-100 shadow">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table table-zebra table-sm w-full">
        <thead>
          <tr>
            <th>Date</th><th>Births</th><th>Deaths</th>
            <th>Proportion</th><th>Period</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {% for r in records %}
          <tr>
            <td>{{ r.date }}</td>
            <td>{{ r.births }}</td>
            <td>{{ r.deaths }}</td>
            <td>{{ r.proportion_deaths|floatformat:4 }}</td>
            <td>
              <!-- r.after_handwashing calls the @property on the model. -->
              {% if r.after_handwashing %}
                <!-- badge-success: green. text-white ensures readable contrast. -->
                <span class="badge badge-success badge-sm text-white">After</span>
              {% else %}
                <!-- badge-error: red. -->
                <span class="badge badge-error badge-sm text-white">Before</span>
              {% endif %}
            </td>
            <td class="text-right">
              <a href="{% url 'analysis:monthly-update' r.pk %}"
                 class="btn btn-xs btn-ghost">Edit</a>
              <a href="{% url 'analysis:monthly-delete' r.pk %}"
                 class="btn btn-xs btn-error btn-outline">Delete</a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
  document.addEventListener("DOMContentLoaded", function () {
    const md = {{ chart_data|safe }};
    if (md && !md.empty) renderMonthlyChart("monthlyPropChart", md);
  });
</script>
{% endblock %}
```

---

### `monthly_form.html`

```html
<!-- templates/analysis/monthly_form.html -->
<!-- Shared by MonthlyCreateView and MonthlyUpdateView. Identical structure
     to yearly_form.html — the difference is only the form fields rendered. -->
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="card bg-base-100 shadow max-w-md mx-auto mt-8">
  <div class="card-body">
    <h2 class="card-title">{{ title }}</h2>
    <form method="post" class="space-y-4 mt-2">
      {% csrf_token %}
      {% for field in form %}
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">{{ field.label }}</span>
          </label>
          {{ field }}
          {% if field.errors %}
            <span class="text-error text-xs mt-1">{{ field.errors.0 }}</span>
          {% endif %}
        </div>
      {% endfor %}
      <div class="card-actions justify-end pt-2">
        <a href="{{ cancel_url }}" class="btn btn-ghost btn-sm">Cancel</a>
        <button class="btn btn-primary btn-sm">Save</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

---

### `confirm_delete.html`

```html
<!-- templates/analysis/confirm_delete.html -->
<!-- Shared by YearlyDeleteView and MonthlyDeleteView.
     Django's DeleteView provides {{ object }} (the instance to be deleted)
     automatically. cancel_url is added by our custom get_context_data(). -->
{% extends "base.html" %}
{% block title %}Confirm Delete{% endblock %}

{% block content %}
<div class="card bg-base-100 shadow max-w-sm mx-auto mt-12">
  <div class="card-body">
    <h2 class="card-title text-error">Delete Record</h2>
    <p class="text-sm text-gray-600">
      Are you sure you want to delete
      <!-- {{ object }} calls __str__() on the model instance. -->
      <strong>{{ object }}</strong>? This cannot be undone.
    </p>
    <!-- Django's DeleteView requires a POST request to actually delete. -->
    <form method="post" class="mt-4">
      {% csrf_token %}
      <div class="card-actions justify-end">
        <a href="{{ cancel_url }}" class="btn btn-ghost btn-sm">Cancel</a>
        <button class="btn btn-error btn-sm">Yes, delete</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

---

### `analysis_results.html`

```html
<!-- templates/analysis/analysis_results.html -->
<!-- Five-tab analysis page. Each tab panel is a direct sibling of its radio
     input (DaisyUI tab requirement). All chart data is injected as JSON from
     the view context and rendered by charts.js functions on DOMContentLoaded. -->
{% extends "base.html" %}
{% block title %}Statistical Analysis{% endblock %}

{% block content %}
<div class="flex justify-between items-center my-4">
  <h1 class="text-2xl font-bold">Statistical Analysis</h1>
  <!-- All download buttons are always visible regardless of the active tab. -->
  <div class="flex gap-2">
    <a href="{% url 'analysis:dl-clinic-chart' %}"    class="btn btn-sm btn-outline">⬇ Clinic PNG</a>
    <a href="{% url 'analysis:dl-monthly-chart' %}"   class="btn btn-sm btn-outline">⬇ Monthly PNG</a>
    <a href="{% url 'analysis:dl-bootstrap-chart' %}" class="btn btn-sm btn-outline">⬇ Bootstrap PNG</a>
    <a href="{% url 'analysis:dl-yearly-csv' %}"      class="btn btn-sm btn-outline">⬇ Yearly CSV</a>
    <a href="{% url 'analysis:dl-monthly-csv' %}"     class="btn btn-sm btn-outline">⬇ Monthly CSV</a>
  </div>
</div>

<div role="tablist" class="tabs tabs-boxed mb-0 bg-base-100 rounded-b-none px-2 pt-2">

  <!-- Tab 1: Clinic Comparison -->
  <input type="radio" name="atabs" role="tab" class="tab"
         aria-label="Clinic Comparison" checked="checked" />
  <div role="tabpanel" class="tab-content col-span-5 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <h2 class="font-semibold mb-3">Proportion of Deaths: Clinic 1 vs Clinic 2 (1841–1846)</h2>
    <div class="bg-white rounded p-3 shadow-inner mb-4 h-80">
      <canvas id="aClinicChart"></canvas>
    </div>
    {% if clinic_comparison %}
    <div class="overflow-x-auto">
      <table class="table table-sm table-zebra w-full">
        <thead><tr>
          <th>Year</th><th>Clinic 1 (proportion)</th><th>Clinic 2 (proportion)</th>
        </tr></thead>
        <tbody>
          {% for row in clinic_comparison %}
          <tr>
            <td>{{ row.year }}</td>
            <td>{{ row.clinic1 }}</td>
            <td>{{ row.clinic2 }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
      <p class="text-sm text-gray-500">No yearly data loaded.</p>
    {% endif %}
  </div>

  <!-- Tab 2: Handwashing Effect -->
  <input type="radio" name="atabs" role="tab" class="tab" aria-label="Handwashing Effect" />
  <div role="tabpanel" class="tab-content col-span-5 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <h2 class="font-semibold mb-3">Monthly Proportion of Deaths (Clinic 1)</h2>
    <div class="bg-white rounded p-3 shadow-inner mb-4 h-80">
      <canvas id="aMonthlyChart"></canvas>
    </div>
    <!-- DaisyUI stats component: shows three key numbers side by side. -->
    <div class="stats stats-horizontal shadow text-sm">
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">Mean before washing</div>
        <div class="stat-value text-error text-xl">{{ mean_before }}</div>
      </div>
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">Mean after washing</div>
        <div class="stat-value text-success text-xl">{{ mean_after }}</div>
      </div>
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">Mean difference</div>
        <div class="stat-value text-primary text-xl">{{ mean_diff }}</div>
      </div>
    </div>
    <p class="text-sm text-gray-500 mt-3">
      Handwashing reduced the proportion of deaths by approximately
      <strong>{{ mean_diff }}</strong> (absolute).
    </p>
  </div>

  <!-- Tab 3: Bootstrap CI -->
  <input type="radio" name="atabs" role="tab" class="tab" aria-label="Bootstrap CI" />
  <div role="tabpanel" class="tab-content col-span-5 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <h2 class="font-semibold mb-3">Bootstrap 95 % Confidence Interval (3 000 resamples)</h2>
    <div class="bg-white rounded p-3 shadow-inner mb-4 h-80">
      <canvas id="aBootstrapChart"></canvas>
    </div>
    <div class="stats stats-horizontal shadow text-sm">
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">Lower bound (2.5 %)</div>
        <div class="stat-value text-lg">{{ ci_lower }}</div>
      </div>
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">Upper bound (97.5 %)</div>
        <div class="stat-value text-lg">{{ ci_upper }}</div>
      </div>
    </div>
    <p class="text-sm text-gray-500 mt-3">
      With 95 % confidence, handwashing reduced the monthly death proportion by between
      <strong>{{ ci_lower_pct }}%</strong> and <strong>{{ ci_upper_pct }}%</strong>
      (absolute reduction).
    </p>
  </div>

  <!-- Tab 4: t-Test -->
  <input type="radio" name="atabs" role="tab" class="tab" aria-label="t-Test" />
  <div role="tabpanel" class="tab-content col-span-5 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <h2 class="font-semibold mb-3">Welch's t-Test: Before vs After Handwashing</h2>
    <div class="stats stats-horizontal shadow text-sm">
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">t-statistic</div>
        <div class="stat-value text-lg">{{ t_stat }}</div>
      </div>
      <div class="stat py-3 px-5">
        <div class="stat-title text-xs">p-value</div>
        <!-- Conditional class: green if significant, red if not. -->
        <div class="stat-value text-lg {% if significant %}text-success{% else %}text-error{% endif %}">
          {{ p_value_fmt }}
        </div>
      </div>
    </div>
    <!-- alert-success / alert-error: DaisyUI coloured alert boxes. -->
    <div class="alert {% if significant %}alert-success{% else %}alert-error{% endif %} mt-4 text-sm">
      {% if significant %}
        ✅ The difference is <strong>statistically significant</strong> (p &lt; 0.05).
        Handwashing provably reduced mortality.
      {% else %}
        ❌ The difference is <strong>not statistically significant</strong> (p ≥ 0.05).
      {% endif %}
    </div>
  </div>

  <!-- Tab 5: Summary -->
  <input type="radio" name="atabs" role="tab" class="tab" aria-label="Summary" />
  <div role="tabpanel" class="tab-content col-span-5 bg-base-100 rounded-b-box rounded-tr-box p-6">
    <h2 class="font-semibold mb-3">Conclusions</h2>
    <ul class="list-disc list-inside space-y-2 text-sm text-gray-700">
      <li>Clinic 1 (medical students performing autopsies) had consistently
          higher death proportions than Clinic 2 (midwife students) from 1841–1846.</li>
      <li>After Semmelweis mandated handwashing in June 1847, deaths fell by
          roughly <strong>{{ mean_diff }}</strong> in absolute proportion.</li>
      <li>Bootstrap 95 % CI:
          [<strong>{{ ci_lower }}</strong>, <strong>{{ ci_upper }}</strong>] —
          equivalent to a {{ ci_lower_pct }}–{{ ci_upper_pct }} percentage-point
          reduction.</li>
      <li>Welch's t-test: t = {{ t_stat }}, p = {{ p_value_fmt }}.
          {% if significant %}Result is statistically significant.
          {% else %}Result is not statistically significant.{% endif %}
      </li>
    </ul>

    {% if clinic_comparison %}
    <h3 class="font-semibold mt-5 mb-2">Clinic Comparison Table</h3>
    <div class="overflow-x-auto">
      <table class="table table-sm table-zebra w-full">
        <thead><tr>
          <th>Year</th><th>Clinic 1 (proportion)</th><th>Clinic 2 (proportion)</th>
        </tr></thead>
        <tbody>
          {% for row in clinic_comparison %}
          <tr>
            <td>{{ row.year }}</td>
            <td>{{ row.clinic1 }}</td>
            <td>{{ row.clinic2 }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}
  </div>
</div>

<script>
  document.addEventListener("DOMContentLoaded", function () {
    const cd = {{ yearly_chart_data|safe }};
    const md = {{ monthly_chart_data|safe }};
    const bd = {{ bootstrap_chart_data|safe }};
    if (cd && !cd.empty) renderClinicChart("aClinicChart", cd);
    if (md && !md.empty) renderMonthlyChart("aMonthlyChart", md);
    if (bd && !bd.empty) renderBootstrapHistogram("aBootstrapChart", bd);
  });
</script>
{% endblock %}
```

---

## 11. Static JS — charts.js

```js
// static/js/charts.js
// Three Chart.js helper functions called from inline <script> blocks in
// the templates. Each function receives a canvas element ID and a data object
// deserialized from Django's JSON context variables.
// This file is loaded with defer in base.html, so it is guaranteed to
// execute after Chart.js has loaded.

/**
 * renderClinicChart
 * Draws a dual-line chart comparing death proportions for Clinic 1 vs Clinic 2.
 *
 * @param {string} canvasId - the id attribute of the <canvas> element
 * @param {object} data     - { labels: [year,...], clinic1: [...], clinic2: [...] }
 */
function renderClinicChart(canvasId, data) {
  const el = document.getElementById(canvasId);
  if (!el || !data || data.empty) return;  // silent guard — no data yet

  new Chart(el, {
    type: "line",
    data: {
      labels: data.labels,   // x-axis: years
      datasets: [
        {
          label: "Clinic 1",
          data: data.clinic1,
          borderColor: "#ef4444",                    // Tailwind red-500
          backgroundColor: "rgba(239,68,68,0.1)",    // transparent fill
          pointRadius: 5,
          tension: 0.3,   // slight curve on lines
          fill: true,
        },
        {
          label: "Clinic 2",
          data: data.clinic2,
          borderColor: "#22c55e",                    // Tailwind green-500
          backgroundColor: "rgba(34,197,94,0.1)",
          pointRadius: 5,
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,  // allows the chart to fill the parent div's height
      plugins: { legend: { position: "top" } },
      scales: {
        y: {
          title: { display: true, text: "Proportion of deaths" },
          beginAtZero: true,
        },
        x: { title: { display: true, text: "Year" } },
      },
    },
  });
}

/**
 * renderMonthlyChart
 * Draws two connected line segments: one red (before June 1847) and one green
 * (after), on a single shared x-axis. Nulls pad the inactive segment so
 * Chart.js draws them as separate non-connected lines.
 *
 * @param {string} canvasId
 * @param {object} data - { labelsBefore, before, labelsAfter, after }
 */
function renderMonthlyChart(canvasId, data) {
  const el = document.getElementById(canvasId);
  if (!el || !data || data.empty) return;

  // Merge both label arrays into a single x-axis.
  const allLabels = [...data.labelsBefore, ...data.labelsAfter];

  // Pad each dataset with nulls on the side where it has no data.
  // spanGaps: false means Chart.js will NOT connect across nulls — the gap
  // between the two coloured segments is intentional.
  const beforePadded = [
    ...data.before,
    ...new Array(data.labelsAfter.length).fill(null),
  ];
  const afterPadded = [
    ...new Array(data.labelsBefore.length).fill(null),
    ...data.after,
  ];

  new Chart(el, {
    type: "line",
    data: {
      labels: allLabels,
      datasets: [
        {
          label: "Before handwashing",
          data: beforePadded,
          borderColor: "#ef4444",
          backgroundColor: "rgba(239,68,68,0.08)",
          pointRadius: 3,
          tension: 0.2,
          spanGaps: false,   // do not bridge the null gap
          fill: true,
        },
        {
          label: "After handwashing",
          data: afterPadded,
          borderColor: "#22c55e",
          backgroundColor: "rgba(34,197,94,0.08)",
          pointRadius: 3,
          tension: 0.2,
          spanGaps: false,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "top" } },
      scales: {
        y: {
          title: { display: true, text: "Proportion of deaths" },
          beginAtZero: true,
        },
        x: {
          ticks: { maxTicksLimit: 14, maxRotation: 45 },
          title: { display: true, text: "Date" },
        },
      },
    },
  });
}

/**
 * renderBootstrapHistogram
 * Draws a bar chart (histogram) of the bootstrap distribution.
 * Bars outside the 95 % CI are coloured red; bars inside are blue.
 *
 * @param {string} canvasId
 * @param {object} data - { labels, counts, ci_lower, ci_upper }
 */
function renderBootstrapHistogram(canvasId, data) {
  const el = document.getElementById(canvasId);
  if (!el || !data || data.empty) return;

  new Chart(el, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Frequency",
          data: data.counts,
          // Colour each bar based on whether it falls inside the CI.
          backgroundColor: data.labels.map((v) => {
            if (v < data.ci_lower || v > data.ci_upper)
              return "rgba(239,68,68,0.4)";    // red: outside CI
            return "rgba(59,130,246,0.6)";     // blue: inside CI
          }),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            // Show the bin centre value in the tooltip header.
            title: (items) => `Diff ≈ ${items[0].label}`,
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Mean difference in proportion deaths" },
          ticks: { maxTicksLimit: 10 },
        },
        y: { title: { display: true, text: "Count" } },
      },
    },
  });
}
```

---

## 12. Admin

```python
# analysis/admin.py
# Registers both models with Django's built-in admin at /admin/.
# list_display controls which columns appear in the changelist table.
# list_filter adds a sidebar filter widget.

from django.contrib import admin
from .models import YearlyRecord, MonthlyRecord


@admin.register(YearlyRecord)
class YearlyRecordAdmin(admin.ModelAdmin):
    # proportion_deaths is a @property, not a DB column — admin displays it
    # read-only automatically since it has no corresponding form field.
    list_display = ("year", "clinic", "births", "deaths", "proportion_deaths")
    list_filter  = ("clinic",)   # sidebar filter: click Clinic 1 / Clinic 2
    ordering     = ("clinic", "year")


@admin.register(MonthlyRecord)
class MonthlyRecordAdmin(admin.ModelAdmin):
    # after_handwashing is a @property; displayed as a boolean tick/cross icon.
    list_display = ("date", "births", "deaths", "proportion_deaths", "after_handwashing")
    ordering     = ("date",)
```

---

## 13. First Run

```bash
# Create database tables from the models
python manage.py makemigrations
python manage.py migrate

# Optional: create a superuser to access /admin
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/upload/** and import both CSV files.

| URL | Page |
|---|---|
| `/` | Dashboard — 4 tabs: bio, yearly chart, monthly chart, analysis link |
| `/upload/` | Import `yearly_deaths_by_clinic.csv` and/or `monthly_deaths.csv` |
| `/yearly/` | Clinic comparison chart + tabbed data tables |
| `/yearly/add/` | Add a yearly record |
| `/yearly/<pk>/edit/` | Edit a yearly record |
| `/yearly/<pk>/delete/` | Delete confirmation |
| `/monthly/` | Monthly proportion chart + full table |
| `/monthly/add/` | Add a monthly record |
| `/analysis/` | 5-tab statistical analysis page |
| `/download/yearly-csv/` | Download processed yearly data as CSV |
| `/download/monthly-csv/` | Download processed monthly data as CSV |
| `/download/clinic-chart/` | Download clinic comparison chart as PNG |
| `/download/monthly-chart/` | Download monthly proportion chart as PNG |
| `/download/bootstrap-chart/` | Download bootstrap histogram as PNG |
| `/admin/` | Django admin panel |
```

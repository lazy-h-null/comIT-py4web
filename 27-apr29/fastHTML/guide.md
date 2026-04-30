# HTMX Feature Explorer — Code Walkthrough

A detailed explanation of `main.py`: a single-file FastHTML application that
demonstrates every major HTMX attribute, styled with DaisyUI and Tailwind CSS.

---

## Table of Contents

1. [Technology Stack](#1-technology-stack)
2. [Project Structure](#2-project-structure)
3. [App Bootstrap](#3-app-bootstrap)
4. [CSS & Styling Setup](#4-css--styling-setup)
5. [Reusable Helper Components](#5-reusable-helper-components)
6. [Critical FastHTML Routing Rule](#6-critical-fasthtml-routing-rule)
7. [Demo Routes — Explained One by One](#7-demo-routes--explained-one-by-one)
   - [7.1 hx-get & hx-post](#71-hx-get--hx-post)
   - [7.2 hx-trigger](#72-hx-trigger)
   - [7.3 hx-swap & hx-target](#73-hx-swap--hx-target)
   - [7.4 hx-indicator & hx-disabled-elt](#74-hx-indicator--hx-disabled-elt)
   - [7.5 hx-confirm & hx-delete](#75-hx-confirm--hx-delete)
   - [7.6 hx-vals & hx-include](#76-hx-vals--hx-include)
   - [7.7 hx-push-url](#77-hx-push-url)
   - [7.8 Polling & Progress](#78-polling--progress)
   - [7.9 Out-of-Band Swaps (hx-swap-oob)](#79-out-of-band-swaps-hx-swap-oob)
8. [Main Page Route](#8-main-page-route)
9. [FastHTML FT Component Patterns](#9-fasthtml-ft-component-patterns)
10. [Common Pitfalls & Lessons Learned](#10-common-pitfalls--lessons-learned)

---

## 1. Technology Stack

| Layer | Library | Role |
|-------|---------|------|
| Server | **FastHTML** + Starlette + Uvicorn | Python web framework, routing, HTML rendering |
| Interactivity | **HTMX** (via CDN) | Server-driven UI updates without writing JavaScript |
| Component styling | **DaisyUI** (via CDN) | Tailwind-based component library (buttons, cards, badges…) |
| Utility CSS | **Tailwind CSS** (via CDN) | Low-level utility classes for spacing, typography, layout |
| Fonts | Google Fonts (Space Mono + DM Sans) | Monospace + sans-serif type pairing |

The entire application is **one Python file** with zero JavaScript written by hand.
All interactivity is handled by HTMX making HTTP requests to FastHTML route handlers
and swapping the HTML responses into the page.

---

## 2. Project Structure

```
main.py
│
├── CDN headers (Link / Script tags)
├── Custom CSS (Style tag)
├── fast_app() bootstrap
│
├── Helper functions
│   ├── section_header()
│   ├── attr_badge()
│   └── result_box()
│
├── Route handlers (one unique function per route+method)
│   ├── GET  /demo/click           → hx-get demo
│   ├── POST /demo/click           → hx-post demo
│   ├── GET  /demo/trigger/hover   → mouseover trigger
│   ├── GET  /demo/trigger/delay   → click delay trigger
│   ├── GET  /demo/trigger/keyup   → keyup+debounce trigger
│   ├── GET  /demo/swap/{mode}     → hx-swap modes
│   ├── GET  /demo/slow            → hx-indicator (slow response)
│   ├── GET  /demo/list            → render deletable list
│   ├── DELETE /demo/list/{idx}    → remove one item
│   ├── GET  /demo/page-a          → push-url fragment A
│   ├── GET  /demo/page-b          → push-url fragment B
│   ├── GET  /demo/vals            → hx-vals & hx-include demo
│   ├── POST /demo/progress/start  → start polling job
│   ├── GET  /demo/progress/poll   → polling tick
│   ├── POST /demo/oob             → out-of-band swap demo
│   └── GET  /                     → main page
│
└── serve()
```

---

## 3. App Bootstrap

```python
from fasthtml.common import *
import random, time

app, rt = fast_app(hdrs=hdrs, live=False)
```

`from fasthtml.common import *` imports everything needed: all HTML tag
functions (`Div`, `P`, `Button`, `Input`…), Starlette helpers, HTMX utilities,
and FastHTML's routing decorators.

`fast_app()` creates the FastHTML application object (`app`) and a routing
shortcut (`rt`). Key parameters:

- `hdrs` — a tuple of extra tags injected into every `<head>`. Used here to
  load DaisyUI, Tailwind, Google Fonts, and the custom `<style>` block.
- `live=False` — disables the built-in live-reload websocket (fine for
  production or demos).

`serve()` at the bottom starts Uvicorn on `localhost:5001`. You never need
`if __name__ == "__main__":` — FastHTML handles that guard internally.

---

## 4. CSS & Styling Setup

### DaisyUI + Tailwind via CDN

```python
daisyui_css = Link(rel="stylesheet",
    href="https://cdn.jsdelivr.net/npm/daisyui@4.10.1/dist/full.min.css")
tailwind_js = Script(src="https://cdn.tailwindcss.com")
```

Both are loaded from CDN so no build step is required. DaisyUI provides
semantic component classes (`btn`, `card`, `badge`, `alert`, `loading`…).
Tailwind provides utility classes (`flex`, `gap-2`, `text-sm`, `mt-4`…).

### Google Fonts

```python
google_fonts = Link(rel="stylesheet",
    href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700"
         "&family=DM+Sans:wght@300;400;500;600&display=swap")
```

Two fonts are loaded: **Space Mono** for code/monospace elements and
**DM Sans** for body text. They are wired up via CSS variables:

```css
:root {
  --font-mono: 'Space Mono', monospace;
  --font-sans: 'DM Sans', sans-serif;
}
body { font-family: var(--font-sans); }
```

### HTMX Indicator CSS

```css
.htmx-indicator               { opacity: 0; transition: opacity 200ms ease; }
.htmx-request .htmx-indicator { opacity: 1; }
.htmx-request.htmx-indicator  { opacity: 1; }
```

These three rules are the standard HTMX loading-indicator pattern:

- Any element with class `htmx-indicator` is invisible by default.
- When an HTMX request is in-flight, HTMX adds the class `htmx-request` to
  the element named in `hx-indicator`. That parent's `.htmx-indicator`
  children become visible (first rule), or if the indicator *is* the
  request-origin element itself, the second rule applies.

### Entrance Animation

```css
@keyframes fadeIn {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}
.fade-in { animation: fadeIn 0.35s ease forwards; }
```

Every HTML fragment returned by the server includes `cls="fade-in"` so it
smoothly slides into place when HTMX injects it.

### DaisyUI Theme

The `<body>` element receives `data-theme="night"` (set in the main page
route), which activates DaisyUI's built-in dark theme globally.

---

## 5. Reusable Helper Components

Three small Python functions generate recurring UI patterns to keep the main
page code DRY.

### `section_header(emoji, title, subtitle, color)`

```python
def section_header(emoji, title, subtitle, color="primary"):
    return Div(
        Span(emoji, cls="text-3xl"),
        H2(title, cls=f"text-2xl font-bold text-{color} font-mono mt-1"),
        P(subtitle, cls="text-base-content/60 text-sm mt-1"),
        cls="mb-5"
    )
```

Renders the top of each demo card: a large emoji, a coloured heading in
monospace font, and a muted subtitle. The `color` parameter maps to DaisyUI
semantic colour names (`primary`, `secondary`, `accent`, `info`, etc.).

### `attr_badge(attr, desc)`

```python
def attr_badge(attr, desc):
    return Div(
        Span(attr, cls="font-mono text-xs badge badge-htmx"),
        Span(desc, cls="text-xs text-base-content/70 ml-2"),
        cls="flex items-center gap-1 mb-1"
    )
```

Renders a pill badge (using the custom `.badge-htmx` gradient) containing the
HTMX attribute name, followed by a short description. Used at the bottom of
each card as a quick-reference legend.

### `result_box(placeholder, box_id)`

```python
def result_box(placeholder, box_id):
    return Div(
        P(placeholder, cls="text-base-content/40 italic text-sm"),
        id=box_id,
        cls="mt-3 min-h-10 p-2 rounded-lg bg-base-200"
    )
```

Renders an empty, styled container with an `id` that HTMX can target. The
italic placeholder text tells the user what to do; it is replaced by the
server's response when a request fires.

---

## 6. Critical FastHTML Routing Rule

> **Every route handler function must have a unique name.**

FastHTML determines the HTTP method for a route from the **function name**:
a function named `get` registers as GET, `post` as POST, `delete` as DELETE,
and so on. Because Python is interpreted top-to-bottom, defining two functions
with the same name means the second silently overwrites the first — only the
last definition survives.

```python
# ❌ WRONG — only the second `get` will be registered
@rt("/demo/trigger/hover")
def get(): ...          # overwritten!

@rt("/demo/trigger/delay")
def get(): ...          # this is the only one that exists

# ✅ CORRECT — unique names, method inferred from name prefix
@rt("/demo/trigger/hover")
def trigger_hover(): ...   # GET (no body params → treated as GET)

@rt("/demo/trigger/delay")
def trigger_delay(): ...   # GET
```

The exception is when the **same path** needs both GET and POST — two
different method-name functions on the same path is fine:

```python
@rt("/demo/click")
def get(): ...    # handles GET /demo/click

@rt("/demo/click")
def post(): ...   # handles POST /demo/click
```

---

## 7. Demo Routes — Explained One by One

### 7.1 `hx-get` & `hx-post`

**Routes:** `GET /demo/click`, `POST /demo/click`

```python
@rt("/demo/click")
def get():
    msgs = ["HTMX fetched this via GET — no page reload! 🎉", ...]
    return Div(
        P(random.choice(msgs), cls="font-semibold text-primary"),
        P(f"Server time: {time.strftime('%H:%M:%S')}", ...),
        cls="fade-in"
    )

@rt("/demo/click")
def post(name: str = "stranger"):
    return Div(
        P(f"Hello, {name}! Submitted via hx-post 📬", ...),
        P(f"Received at: {time.strftime('%H:%M:%S')}", ...),
        cls="fade-in"
    )
```

The GET handler returns a random message and the current server time.
FastHTML automatically type-casts route parameters: `name: str` will be
populated from query string or form data.

**How the UI wires them up:**

```python
# GET button
Button("Fetch from server",
    hx_get="/demo/click",
    hx_target="#get-result",
    hx_swap="innerHTML")

# POST — sends the value of #post-name input
Button("Submit",
    hx_post="/demo/click",
    hx_include="#post-name",   # pulls the input's value into the request body
    hx_target="#post-result",
    hx_swap="innerHTML")
```

`hx_include` tells HTMX to find the element matching `#post-name` and include
its `name`/`value` pair in the request, even though the button is not inside a
`<form>` with that input.

---

### 7.2 `hx-trigger`

**Routes:** `GET /demo/trigger/hover`, `/delay`, `/keyup`

```python
@rt("/demo/trigger/hover")
def trigger_hover():
    return Span("👀 mouseover triggered this request!", cls="...fade-in")

@rt("/demo/trigger/delay")
def trigger_delay():
    return Span("⏱️ Fired after 1 second delay!", cls="...fade-in")

@rt("/demo/trigger/keyup")
def trigger_keyup(q: str = ""):
    if not q:
        return Span("Start typing…", cls="...")
    return Div(
        Span(f'"{q}"', cls="badge badge-outline font-mono"),
        Span(f"{len(q)} chars", cls="..."),
        cls="fade-in flex items-center gap-2"
    )
```

These three handlers demonstrate three `hx-trigger` modifiers:

| UI Element | `hx-trigger` value | What it does |
|---|---|---|
| Hover zone `<div>` | `"mouseover"` | Fires on every mouse-enter |
| Warning button | `"click delay:1s"` | Waits 1 second after click before sending |
| Search input | `"keyup delay:500ms changed"` | Fires 500 ms after typing stops, only if value changed |

The `changed` modifier is particularly important for the search input — without
it, pressing an arrow key or modifier key would also fire a request even though
the search text didn't change.

The `trigger_keyup` handler receives `q` as a query parameter (FastHTML
extracts it from `?q=…` automatically). It returns early with a placeholder
when `q` is empty.

---

### 7.3 `hx-swap` & `hx-target`

**Route:** `GET /demo/swap/{mode}`

```python
@rt("/demo/swap/{mode}")
def swap_mode(mode: str):
    labels = {
        "innerHTML":   ("🔄", "text-primary",  "Inner content replaced, outer div stays."),
        "outerHTML":   ("💥", "text-secondary", "The entire element was replaced."),
        "prepend":     ("↑",  "text-warning",   "Added to the TOP of the target."),
        "append":      ("↓",  "text-success",   "Added to the BOTTOM of the target."),
        "beforebegin": ("⬆️", "text-accent",    "Inserted BEFORE the target element."),
        "afterend":    ("⬇️", "text-info",      "Inserted AFTER the target element."),
    }
    icon, color, desc = labels.get(mode, ("?", "", "Unknown mode"))
    return Div(
        Span(f'{icon} hx-swap="{mode}"', cls=f"font-mono font-bold {color}"),
        P(desc, cls="text-xs text-base-content/60 mt-1"),
        cls="fade-in"
    )
```

`{mode}` is a **path parameter** — FastHTML extracts it from the URL and passes
it as a string argument. The handler looks it up in a dict to get the
corresponding icon, colour, and description.

All six buttons in the UI target the same `#swap-demo-area` element but each
uses `innerHTML` as the swap strategy in the button definition (for
demonstration consistency). The label in the response tells the user which mode
was selected. In a real app you would use different swap modes to achieve
different DOM insertion effects:

| Mode | Use case |
|---|---|
| `innerHTML` | Replace the content inside an element (most common) |
| `outerHTML` | Replace the element itself (e.g. update a list item in place) |
| `prepend` | Add to the top of a container (e.g. newest item first) |
| `append` | Add to the bottom of a container (e.g. infinite scroll) |
| `beforebegin` | Insert a sibling before the target |
| `afterend` | Insert a sibling after the target |

---

### 7.4 `hx-indicator` & `hx-disabled-elt`

**Route:** `GET /demo/slow`

```python
@rt("/demo/slow")
def slow_response():
    time.sleep(1.5)   # simulate a slow database query or API call
    return Div(
        P("✅ Response arrived after 1.5 s", cls="text-success font-semibold"),
        P("The spinner showed while waiting.", cls="text-xs opacity-60 mt-1"),
        cls="fade-in"
    )
```

`time.sleep(1.5)` deliberately delays the response to make the loading state
visible. The button in the UI is wired up like this:

```python
Button(
    Span("Load slow response (1.5 s)"),
    Span(cls="loading loading-spinner loading-sm htmx-indicator ml-2"),
    cls="btn btn-warning gap-2",
    id="slow-btn",
    hx_get="/demo/slow",
    hx_target="#slow-result",
    hx_swap="innerHTML",
    hx_indicator="#slow-btn",    # apply .htmx-request to this element
    hx_disabled_elt="this",      # disable the button during the request
)
```

The `Span` with class `htmx-indicator` inside the button is hidden by default
(opacity 0). When the request fires, HTMX adds `htmx-request` to `#slow-btn`
(the value of `hx-indicator`), which makes `.htmx-indicator` children visible
via the CSS rule: `.htmx-request .htmx-indicator { opacity: 1; }`.

`hx_disabled_elt="this"` tells HTMX to add the `disabled` attribute to the
button itself while the request is in flight, preventing double-submission.

---

### 7.5 `hx-confirm` & `hx-delete`

**Routes:** `GET /demo/list`, `DELETE /demo/list/{idx}`

```python
items_store = ["Item Alpha", "Item Beta", "Item Gamma", "Item Delta"]

@rt("/demo/list")
def list_items():
    if not items_store:
        return P("All items deleted! Restart the server to reset.", ...)
    return Ul(
        *[Li(
            Div(
                Span(f"• {item}", cls="flex-1 text-sm"),
                Button("✕",
                    hx_delete=f"/demo/list/{i}",
                    hx_confirm=f"Delete '{item}'?",
                    hx_target="closest li",
                    hx_swap="outerHTML"),
                cls="flex items-center gap-2 py-1"
            ),
            cls="border-b border-base-200"
        ) for i, item in enumerate(items_store)],
        cls="w-full"
    )

@rt("/demo/list/{idx}")
def delete(idx: int):
    if 0 <= idx < len(items_store):
        items_store.pop(idx)
    return ""
```

`items_store` is a plain Python list acting as in-memory state (resets on
server restart). The list is rendered fresh on every GET — HTMX calls
`GET /demo/list` once on page load via `hx_trigger="load"` on the container div.

Each delete button demonstrates three things:

- `hx_delete` — issues an HTTP DELETE request (not GET or POST).
  FastHTML registers the handler because the function is named `delete`.
- `hx_confirm` — HTMX intercepts the click and calls the browser's built-in
  `window.confirm()` with this string before proceeding.
- `hx_target="closest li"` — a **relative CSS selector**. `closest` walks up
  the DOM from the button to find the nearest ancestor `<li>`. This means each
  button knows how to remove its own parent item without needing a unique id.
- `hx_swap="outerHTML"` — replaces the entire `<li>`, not just its contents.

The delete handler returns an **empty string** `""`. When HTMX receives an
empty response with `outerHTML` swap, it removes the target element from the
DOM entirely.

---

### 7.6 `hx-vals` & `hx-include`

**Route:** `GET /demo/vals`

```python
@rt("/demo/vals")
def vals_demo(color: str = "none", size: str = "none", extra: str = ""):
    children = [
        Div(style=f"background:{color};border:2px solid #6366f1",
            cls="w-16 h-16 rounded-xl mb-2"),
        P(f"color={color}  size={size}", cls="font-mono text-xs text-primary"),
    ]
    if extra:
        children.append(
            P(f'extra (hx-include) = "{extra}"',
              cls="font-mono text-xs text-secondary mt-1"))
    return Div(*children, cls="fade-in flex flex-col items-center")
```

The handler accepts three optional query parameters and renders a coloured
square plus a text readout of the received values.

**`hx-vals`** embeds a JSON object directly on the element. When the request
fires, HTMX merges this JSON into the request parameters:

```python
Button("Crimson",
    hx_get="/demo/vals",
    hx_target="#vals-result",
    hx_swap="innerHTML",
    **{"hx-vals": '{"color":"crimson","size":"medium"}'})
```

Note that `hx-vals` must be passed via `**{"hx-vals": ...}` because the
hyphen in `hx-vals` cannot be expressed as a Python keyword argument directly
(`hx_vals` would render as `hx-vals` in FastHTML, which actually does work —
but using the dict syntax is explicit and safe for JSON values).

**`hx-include`** pulls the current value of another element into the request:

```python
Button("Send",
    hx_get="/demo/vals",
    hx_include="#extra-input",   # adds extra-input's name/value to request
    **{"hx-vals": '{"color":"blueviolet","size":"large"}'})
```

Both `hx-vals` and `hx-include` can be used together — HTMX merges all sources
into the final request.

---

### 7.7 `hx-push-url`

**Routes:** `GET /demo/page-a`, `GET /demo/page-b`

```python
@rt("/demo/page-a")
def page_a():
    return Div(
        P("📄 Page A loaded as a fragment", cls="font-semibold text-primary"),
        P("URL updated via hx-push-url — no full reload.", cls="..."),
        Button("→ Load Page B",
            hx_get="/demo/page-b",
            hx_target="#boost-result",
            hx_swap="innerHTML",
            hx_push_url="/demo/page-b"),   # <-- updates the address bar
        cls="fade-in"
    )
```

These handlers return **partial HTML fragments**, not complete pages. HTMX
injects them into `#boost-result` in the main page.

`hx_push_url` tells HTMX to call `history.pushState()` after the swap,
changing the browser's address bar to `/demo/page-a` or `/demo/page-b` without
any navigation. The back and forward buttons work correctly because the history
stack is updated properly.

This is essentially what `hx-boost="true"` does automatically for regular
`<a>` links — here we are doing it explicitly on buttons to demonstrate
the mechanism.

---

### 7.8 Polling & Progress

**Routes:** `POST /demo/progress/start`, `GET /demo/progress/poll`

```python
progress_state = {"value": 0, "running": False}

def progress_widget(value, done=False):
    bar_color = "bg-success" if done else "bg-primary"
    label     = "✅ Complete!" if done else f"{value}%"
    kw = dict(id="progress-container")
    if not done:
        kw["hx_get"]     = "/demo/progress/poll"
        kw["hx_trigger"] = "load delay:300ms"
        kw["hx_swap"]    = "outerHTML"
        kw["hx_target"]  = "#progress-container"
    return Div(
        Div(
            Div(cls=f"progress-bar {bar_color} h-4 rounded-full",
                style=f"width:{value}%"),
            cls="w-full bg-base-200 rounded-full h-4"
        ),
        P(label, cls=f"text-xs text-center mt-1 font-mono"),
        **kw
    )

@rt("/demo/progress/start")
def progress_start():
    progress_state["value"]   = 0
    progress_state["running"] = True
    return progress_widget(0)

@rt("/demo/progress/poll")
def progress_poll():
    if progress_state["running"]:
        progress_state["value"] = min(
            progress_state["value"] + random.randint(8, 22), 100)
        v    = progress_state["value"]
        done = v >= 100
        if done: progress_state["running"] = False
        return progress_widget(v, done=done)
    return Div(P("Press Start to begin", ...), id="progress-container")
```

This is the most sophisticated pattern in the app — a **self-polling element**:

1. The "Start Job" button POSTs to `/demo/progress/start`, which resets state
   and returns `progress_widget(0)`.
2. The returned widget has `hx_trigger="load delay:300ms"` on itself — as soon
   as HTMX inserts it into the DOM, it fires a GET to `/demo/progress/poll`
   after 300 ms.
3. The poll handler advances the progress value and returns a new
   `progress_widget` (same id, same HTMX attributes). HTMX swaps this into
   `#progress-container` with `outerHTML`, replacing the old element.
4. Because the new element also has `hx_trigger="load delay:300ms"`, the cycle
   repeats automatically.
5. When `value >= 100`, `done=True` causes `progress_widget` to omit the HTMX
   attributes entirely — the element is now inert and polling stops.

The `progress_widget` helper builds its HTMX kwargs conditionally using a dict
`kw`, then unpacks it: `Div(..., **kw)`. This is the correct way to attach
HTMX attributes programmatically in FastHTML.

---

### 7.9 Out-of-Band Swaps (`hx-swap-oob`)

**Route:** `POST /demo/oob`

```python
oob_counter = {"n": 0}

@rt("/demo/oob")
def oob_swap():
    oob_counter["n"] += 1
    n = oob_counter["n"]
    return (
        # 1. Primary content — goes into hx-target="#oob-main"
        Div(
            P(f"Main content updated — click #{n}", cls="text-primary font-semibold"),
            P("Swapped via primary hx-target.", cls="text-xs opacity-60 mt-1"),
            cls="fade-in"
        ),
        # 2. OOB element — htmx finds #oob-counter-display anywhere on the page
        Div(
            Span(f"OOB Counter: {n}", cls="badge badge-secondary font-mono"),
            id="oob-counter-display",
            hx_swap_oob="true"
        )
    )
```

Normally, HTMX swaps a response into the single element specified by
`hx-target`. Out-of-band swaps let a response **also update other elements**
anywhere on the page.

When FastHTML returns a **tuple**, it concatenates all items into the response
body. HTMX processes the response like this:

- The first element (no `hx-swap-oob`) goes into `#oob-main` as normal.
- The second element has `hx-swap-oob="true"` and `id="oob-counter-display"`.
  HTMX scans the response for any element with `hx-swap-oob`, finds
  `#oob-counter-display` in the current page, and swaps it with the OOB
  element from the response — regardless of where on the page it lives.

This is very useful for updating a notification badge, a cart count, a status
indicator, or any other "distant" element without additional requests.

---

## 8. Main Page Route

```python
@rt("/")
def index():
    return (
        Div(...),   # Navbar
        Div(...),   # Hero
        Div(...),   # Feature grid (9 cards)
        Footer(...) # Footer
    )
```

### Returning a tuple instead of `Html(...)`

The `index` handler returns a **tuple of FT components** rather than a
hand-crafted `Html(Head(...), Body(...))` tree. This is the idiomatic FastHTML
pattern:

- FastHTML detects that the request is a normal browser GET (not an HTMX
  partial request) and **automatically wraps** the returned content in a full
  `<!DOCTYPE html><html><head>…</head><body>…</body></html>` document.
- All `Link`, `Script`, and `Style` elements passed to `fast_app(hdrs=…)` are
  automatically injected into `<head>`.
- Any `Link` or `Meta` tags returned inside the tuple are moved to `<head>`
  automatically; everything else goes into `<body>`.

This means you never need to write the HTML skeleton manually.

### DaisyUI Theme

```python
# Applied to the outermost wrapper via data-theme attribute
# In the Navbar div:
# The Body equivalent is the first returned Div with data-theme set on it,
# but in practice FastHTML sets data-theme on <body> via the Div wrapper.
```

The `data-theme="night"` attribute on the body-level element activates
DaisyUI's Night colour scheme globally, giving all DaisyUI components their
dark-mode colours without any extra CSS.

### The Feature Grid

```python
Div(
    Div(...),  # card 1: hx-get & hx-post
    Div(...),  # card 2: hx-trigger
    ...
    cls="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto px-4 pb-16"
)
```

A CSS grid with one column on mobile (`grid-cols-1`) and two columns on large
screens (`lg:grid-cols-2`). Each card is a DaisyUI `card` with `shadow-md` and
the custom `feature-card` hover effect.

---

## 9. FastHTML FT Component Patterns

### Positional children, keyword attributes

```python
Div(
    P("Hello", cls="text-sm"),   # child element (positional)
    id="my-div",                  # HTML attribute (keyword)
    cls="flex gap-2"              # 'cls' → 'class' in HTML
)
```

All FastHTML tag functions follow the same signature: positional args become
child elements, keyword args become HTML attributes. `cls` is the alias for
`class` (a Python reserved word).

### Underscore-to-hyphen conversion

FastHTML converts all underscores in keyword argument names to hyphens:

```python
# Python                      → HTML attribute
hx_get="/demo/click"          → hx-get="/demo/click"
hx_target="#result"           → hx-target="#result"
hx_swap_oob="true"            → hx-swap-oob="true"
hx_disabled_elt="this"        → hx-disabled-elt="this"
hx_push_url="/demo/page-a"    → hx-push-url="/demo/page-a"
```

This is why all HTMX attributes can be written as clean Python kwargs.

### The `**{}` dict exception

Some attributes contain characters that cannot appear in Python keyword
arguments at all (like the JSON braces in `hx-vals`). For those, use dict
unpacking:

```python
Button("Go",
    hx_get="/demo/vals",
    **{"hx-vals": '{"color":"red"}'})   # value contains {} so use dict
```

### Returning tuples

Returning a tuple from a handler concatenates the HTML of all items:

```python
return (
    Div("main content", id="main"),     # goes to hx-target
    Div("oob content", id="sidebar",
        hx_swap_oob="true")             # goes to #sidebar anywhere
)
```

FastHTML serialises each item in order; HTMX routes them by target.

---

## 10. Common Pitfalls & Lessons Learned

This app went through several debugging iterations. Here are the key mistakes
to avoid:

### ❌ Duplicate function names

```python
# WRONG — only the last `get` survives in Python
@rt("/demo/trigger/hover")
def get(): ...

@rt("/demo/trigger/delay")
def get(): ...   # silently overwrites the above
```

**Fix:** Give every handler a unique, descriptive name. FastHTML infers the
HTTP method from the name (`get`, `post`, `delete` etc.) — as long as the name
*starts with or is* one of those methods, or contains no method keyword (in
which case it defaults to GET+POST).

### ❌ Returning `Html(Head(...), Body(...))` manually

```python
# WRONG — fights with FastHTML's auto-wrapping
@rt("/")
def index():
    return Html(Head(...), Body(...))
```

**Fix:** Return a tuple of body content. FastHTML builds the document shell
automatically and injects `hdrs` into `<head>`.

### ❌ Using `**{"hx-get": ...}` dict attrs inside FT constructors for normal HTMX attrs

```python
# UNNECESSARY and fragile
Div(**{"hx-get": "/demo/click", "hx-target": "#result"})

# CORRECT — use underscore kwargs
Div(hx_get="/demo/click", hx_target="#result")
```

**Fix:** Use `hx_` underscore kwargs for all standard HTMX attributes.
Only use `**{}` dict syntax when the value itself contains special characters
(like JSON in `hx-vals`).

### ❌ HTTP method mismatch

```python
# WRONG — handler is GET but UI uses hx_post
@rt("/demo/slow")
def slow_response(): ...   # registers as GET

Button(..., hx_post="/demo/slow")   # sends POST → 405 Method Not Allowed
```

**Fix:** Match the HTTP method in both the handler name and the `hx_get` /
`hx_post` / `hx_delete` attribute on the UI element.

### ❌ Missing POST handler for form-like endpoints

```python
# WRONG — progress/start had no post() handler
@rt("/demo/progress/start")
def progress_start(): ...   # defaults to GET only if name isn't "post"

Button(..., hx_post="/demo/progress/start")  # → 405
```

**Fix:** Name POST handlers `post`, or name them uniquely and include a
`post` parameter — FastHTML checks whether parameters look like POST body data.
The cleanest approach is to name any POST-only endpoint unambiguously:
`def progress_start():` with a `POST` trigger registered because
`fast_app` registers by name (`post*` → POST method).

### ❌ `hx-boost` on individual `<a>` tags hijacking all navigation

```python
# WRONG — hx-boost on an <a> causes the link target to load via AJAX
# and replaces the ENTIRE page body, not just a target div
A("Go home", href="/", hx_boost="true")
```

**Fix:** Use `hx_get` + `hx_target` + `hx_swap` explicitly on buttons
when you want partial-page navigation. Use `hx-boost="true"` on a
**container element** only when you want all its `<a>` children to do
full-page AJAX navigation (history preserved, but whole body swapped).

---

## Running the App

```bash
# Install
pip install python-fasthtml

# Run
python main.py
# → Uvicorn starts on http://localhost:5001
```

Restart the server to reset `items_store` (the delete list) and
`progress_state` back to their defaults, since both live in memory.

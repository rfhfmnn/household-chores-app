# 🧹 Shared Household Chore Manager

A multi-tenant Django web application for coordinating and fairly allocating recurring household chores among roommates based on individual preferences rather than rigid schedules.

---

## 📋 Features

- **Multi-Tenant Architecture:** Roommates belong to isolated households (`Household`), ensuring data privacy and scoping all chores to the active household.
- **Instant Onboarding:** Sign up and immediately join an existing household or create a new one without waiting for admin approval tokens.
- **Preference-Based Bidding:** Each chore iteration (`ChoreCycle`) opens for bidding, allowing roommates to submit preference scores (1–5).
- **Automated Quorum Resolution:** As soon as all household members submit their bids, the matching engine resolves the assignment, with an automatic random tie-breaker.
- **Per-Chore Cadence Engine:** Chores have independent recurrence intervals (e.g. daily dishes, bi-weekly bathroom cleaning).
- **Overdue Tracking:** Visual badges and flags dynamically alert assignees when an assigned task exceeds its deadline.
- **Completion & Cadence Progression:** Marking a chore as completed records historical metrics and automatically triggers the next cycle.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.14+ / Django 6.1+
- **Database:** SQLite (default for development)
- **Frontend:** Semantic HTML5, Django Templates & Custom Responsive CSS
- **Package / Environment Manager:** `uv` or standard Python (`py` / `python`)

---

## 📂 Project Structure

```text
household-chores-app/
│
├── household_chores/         # Django project configuration
│   ├── settings.py           # Core settings, installed apps, templates, auth
│   ├── urls.py               # Main routing & authentication URLs
│   ├── wsgi.py               # WSGI server entry point
│   └── asgi.py               # ASGI server entry point
│
├── chores/                   # Core application
│   ├── models.py             # Household, UserProfile, Chore, ChoreCycle, Bid
│   ├── views.py              # Auth, household selection, dashboard & helpers
│   ├── forms.py              # RegisterForm, HouseholdSelectionForm
│   ├── signals.py            # Automated UserProfile creation signal
│   ├── admin.py              # Django Admin registrations with filters & metrics
│   ├── urls.py               # App-level routing
│   └── tests.py              # Comprehensive unit test suite (15 scenarios)
│
├── templates/                # Django HTML templates
│   ├── base.html             # Base layout with navbar and flash messages
│   ├── registration/         # Login and registration templates
│   ├── households/           # Household selection/join template
│   └── dashboard/            # Dashboard interface
│
├── static/
│   └── css/styles.css        # Responsive, modern design system
│
├── _docs/
│   └── plan.md               # Detailed architectural specification
│
├── backlog.md                # Development milestone tasks and checklist
├── manage.py                 # Django management CLI
└── db.sqlite3                # SQLite database (auto-created)
```

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have Python 3.12+ or [uv](https://github.com/astral-sh/uv) installed.

### 2. Install Dependencies
Using `uv`:
```bash
uv pip install django
```
Or using standard `pip`:
```bash
pip install django
```

### 3. Run Database Migrations
Initialize the SQLite database and create all tables:
```bash
uv run python manage.py migrate
# or on Windows:
py manage.py migrate
```

### 4. Create an Admin User (Optional)
To access the Django Admin panel:
```bash
uv run python manage.py createsuperuser
```

### 5. Start the Development Server
```bash
uv run python manage.py runserver
# or on Windows:
py manage.py runserver
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🧪 Running Tests

The application includes an extensive test suite covering authentication, household isolation, models, signals, constraints, and overdue calculations:

```bash
uv run python manage.py test chores
# or:
py manage.py test chores
```

**Current Test Coverage (15 tests passing):**
- Auto-creation of `UserProfile` via post-save signal.
- Authentication redirects (unauthenticated & users without household).
- User registration and duplicate username rejection.
- Household creation, instant join, and household switching.
- Chore creation and sequential cycle generation.
- Dynamic `is_overdue` status validation under all lifecycle states.
- Duplicate bid prevention (`UniqueConstraint`).
- Preference score range validation (1–5).

---

## 🗺️ Roadmap & Progress

Tracked in detail in [backlog.md](backlog.md):

- [x] **Milestone 1:** Base Setup, Authentication & Household Onboarding
- [x] **Milestone 2:** Core Data Models (`Chore`, `ChoreCycle`, `Bid`), Properties & Admin
- [ ] **Milestone 3:** Chore Creation & Cadence Initiation Views
- [ ] **Milestone 4:** Bidding Engine & Assignment Resolution Algorithm
- [ ] **Milestone 5:** Central Dashboard & Task Completion Workflow
- [ ] **Milestone 6:** Historical Activity Log & UI Polish

---

## 📄 License
This project was built as part of the AI Dev Tools Zoomcamp coursework.
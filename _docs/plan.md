# Shared Household Chore Manager — Project Specification

A multi-tenant Django web application for managing shared household chores using preference-based bidding, automatic assignment resolution, and workload tracking.

---

## 1. Executive Summary & Core Concept

* **Application Name:** Household Chore Manager (Multi-Tenant Django App)
* **Goal:** Fairly allocate recurring household chores among roommates based on individual preferences rather than rigid schedules, reducing friction and conflict.
* **Core Philosophy:** Preference/matching with fair allocation, per-chore cadences, and lightweight social accountability (overdue indicators).

---

## 2. Technical Architecture & Stack

* **Backend Framework:** Python / Django (Monolithic architecture)
* **Database:** SQLite (default for development/homework) or PostgreSQL
* **Frontend:** Django Templates + Clean, semantic CSS (e.g., custom lightweight CSS or minimal CSS framework like Pico.css / simple Bootstrap)
* **Form & Request Handling:** Standard Django Form POST requests with standard HTTP redirects/reloads
* **Multi-Tenancy Model:** Shared database, multi-household architecture scoped via ForeignKey relationships (`Household` scoping across all core models)

---

## 3. Key Architectural Decisions & Specifications

| Dimension | Selected Approach | Operational Detail |
| :--- | :--- | :--- |
| **Workload Model** | Fair-Share / Preference Matching | Balances task assignments while prioritizing roomate preferences. |
| **Cadence Engine** | Per-Chore Cadence | Each chore runs on its own independent recurrence cycle (e.g., daily dishes, bi-weekly bathroom, monthly deep clean). |
| **Bidding Strategy** | Per-Cadence Bidding | Roommates submit their preference scores/rankings for a specific chore cycle before assignment. |
| **Assignment Trigger** | First-to-Bid Threshold (Quorum) | As soon as all roommates in the household submit their bids for an open chore cycle, the matching algorithm resolves automatically. |
| **Conflict Resolution** | Random Draw Tie-Breaker | When multiple roommates place identical top bids on a chore, ties are broken via deterministic/pseudo-random draw. |
| **Accountability / Non-Completion** | Simple Overdue Flag | Tasks past their deadline display a visible "Overdue" status banner/badge. No forced lockouts or automatic reassignments. |
| **Multi-Tenancy & Onboarding** | Direct Household Picker with Instant Join | Users select or create a household upon signup and instantly join without waiting for admin approval tokens. |
| **User Interface Views** | Dashboard + Completion History | Active task view, bidding status, overdue warnings, and a historical completion log. |

---

## 4. Entity-Relationship Data Model Schema

### 4.1. `Household`
Represents an isolated living group/apartment.
* `id`: Primary Key (UUID or AutoField)
* `name`: CharField (e.g., "Apartment 4B", "Maple Street House")
* `created_at`: DateTimeField(auto_now_add=True)

### 4.2. `UserProfile` (or custom User model)
Extends standard Django authentication.
* `user`: OneToOneField(`auth.User`, on_delete=CASCADE)
* `household`: ForeignKey(`Household`, on_delete=SET_NULL, null=True, blank=True, related_name='members')
* `created_at`: DateTimeField(auto_now_add=True)

### 4.3. `Chore`
Defines the template / definition for recurring tasks.
* `household`: ForeignKey(`Household`, on_delete=CASCADE, related_name='chores')
* `title`: CharField (e.g., "Kitchen Dishes", "Trash & Recycling")
* `description`: TextField (optional instructions)
* `frequency_days`: PositiveIntegerField (cadence period in days, e.g., 1 for daily, 7 for weekly)
* `is_active`: BooleanField(default=True)
* `created_at`: DateTimeField(auto_now_add=True)

### 4.4. `ChoreCycle` (or `ChoreInstance`)
Represents an individual iteration of a chore requiring bidding or execution.
* `chore`: ForeignKey(`Chore`, on_delete=CASCADE, related_name='cycles')
* `cycle_number`: PositiveIntegerField (incremental per chore)
* `due_date`: DateTimeField
* `status`: CharField (Choices: `BIDDING`, `ASSIGNED`, `COMPLETED`)
* `assigned_to`: ForeignKey(`User`, null=True, blank=True, on_delete=SET_NULL, related_name='assigned_cycles')
* `completed_at`: DateTimeField(null=True, blank=True)
* `completed_by`: ForeignKey(`User`, null=True, blank=True, on_delete=SET_NULL, related_name='completed_cycles')

### 4.5. `Bid`
Stores a user's preference for a given chore cycle.
* `cycle`: ForeignKey(`ChoreCycle`, on_delete=CASCADE, related_name='bids')
* `user`: ForeignKey(`auth.User`, on_delete=CASCADE, related_name='bids')
* `preference_score`: PositiveSmallIntegerField (e.g., 1 = Low preference / dislike, 5 = Highly preferred)
* `submitted_at`: DateTimeField(auto_now_add=True)

*Unique constraint:* `(cycle, user)` must be unique.

---

## 5. System Logic & Workflow

### 5.1. Authentication & Onboarding
1. **Registration / Login:** User registers with username, email, and password.
2. **Household Selection:**
   * User sees a dropdown/list of existing households and an option to "Create a New Household".
   * Upon selecting or creating, the user is immediately bound to the household (`user.userprofile.household = household`).

### 5.2. Chore Lifecycle & Cadence
1. **Cycle Initialization:** When a chore is created (or when a previous cycle completes), a new `ChoreCycle` is opened in `BIDDING` status with an assigned `due_date = now() + frequency_days`.
2. **Bidding Window:**
   * Active members of the household see an open bid prompt on their dashboard.
   * Each member submits their preference score (1 to 5).

### 5.3. Assignment Trigger & Resolution (First-to-Bid Threshold)
1. **Trigger Condition:** In the `BidForm` submission view, after saving a bid:
   ```python
   total_household_members = chore_cycle.chore.household.members.count()
   total_bids = chore_cycle.bids.count()
   
   if total_bids >= total_household_members:
       resolve_assignment(chore_cycle)
   ```
2. **Resolution Algorithm:**
   * Identify the user(s) with the highest `preference_score`.
   * If there is a tie for the top score, select one user randomly using Python's `random.choice`.
   * Set `chore_cycle.assigned_to = selected_user`.
   * Update `chore_cycle.status = 'ASSIGNED'`.

### 5.4. Execution & History Logging
1. **Overdue Flagging:**
   * A dynamic model property on `ChoreCycle`:
     ```python
     @property
     def is_overdue(self):
         return self.status == 'ASSIGNED' and timezone.now() > self.due_date
     ```
   * Displayed with a red alert badge on the dashboard.
2. **Completion:**
   * The assignee clicks "Mark Completed".
   * `status` transitions to `COMPLETED`, setting `completed_at = timezone.now()`.
   * The system automatically spawns the next `ChoreCycle` in `BIDDING` status.
3. **Completion History View:**
   * Displays completed chores with assignee, completion timestamp, and whether it was finished on time.

---

## 6. Page Routes & Views

| Route | View Type | Description |
| :--- | :--- | :--- |
| `/accounts/login/` | Auth | Standard login view. |
| `/accounts/register/` | Form View | Registration form. |
| `/household/select/` | Form View | Directory/dropdown to pick or create household (instant join). |
| `/dashboard/` | Template View | Main hub: active chores, overdue badges, active bidding actions. |
| `/chores/new/` | Form View | Form to define a new chore and cadence. |
| `/chores/<id>/bid/` | Form View | Submit preference score for a specific chore cycle. |
| `/chores/<cycle_id>/complete/` | POST Action | Mark chore cycle as completed. |
| `/history/` | ListView | Table/log of completed chore cycles with filters. |

---

## 7. Implementation Roadmap

1. **Phase 1: Project Setup & Auth**
   * Initialize Django project, apps (`accounts`, `households`, `chores`).
   * Setup `UserProfile` and household picker with instant join.
2. **Phase 2: Chore CRUD & Cadence Models**
   * Implement `Chore`, `ChoreCycle`, and `Bid` models with migrations.
   * Add chore creation interface.
3. **Phase 3: Bidding & Matching Engine**
   * Build bidding views and form handling.
   * Implement the automated threshold check and random-draw tie-breaker resolver.
4. **Phase 4: Dashboard & Overdue Status**
   * Build dashboard template displaying active assignments, overdue items, and pending bids.
   * Add completion action handler that triggers subsequent cycle creation.
5. **Phase 5: History Log & UI Polish**
   * Implement completion history view with timestamp and status logs.
   * Apply clean CSS styling, alerts, and navigation bar.
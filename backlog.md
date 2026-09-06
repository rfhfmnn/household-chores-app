# Project Backlog: Household Chore Manager

Based on the specification in `_docs/plan.md`, this backlog outlines the incremental tasks required to build the multi-tenant Django application.

---

## Milestone 1: Base Setup, Authentication & Onboarding

- [x] **Task 1.1: Base Configuration & Templates Setup**
  - Configure `TEMPLATES['DIRS']` and static files settings in `household_chores/settings.py`.
  - Create base template (`templates/base.html`) with semantic layout, navigation header, and message alert styling.
  - *Acceptance Criteria:* Base template renders cleanly with responsive styling and a navigation placeholder.

- [x] **Task 1.2: User Authentication (Login / Register / Logout)**
  - Implement registration view and form (`/accounts/register/`).
  - Configure standard Django login and logout views (`/accounts/login/`, `/accounts/logout/`).
  - Create authentication templates (`templates/registration/login.html`, `register.html`).
  - *Acceptance Criteria:* A new user can sign up, log in, and log out with appropriate session redirects.

- [x] **Task 1.3: Household & UserProfile Models**
  - Create `Household` model (`name`, `created_at`).
  - Create `UserProfile` model with a OneToOne relationship to `auth.User` and a ForeignKey to `Household` (`related_name='members'`).
  - Set up Django signal (`post_save` on `User`) to auto-create `UserProfile`.
  - *Acceptance Criteria:* Migrations run successfully; each user has an associated profile linked to a household.

- [x] **Task 1.4: Household Selection & Instant Join**
  - Build household picker view and form (`/household/select/`) with options to:
    - Choose an existing household from a list/dropdown.
    - Create a new household and join immediately.
  - Add middleware or helper decorator to redirect users without a household to `/household/select/`.
  - *Acceptance Criteria:* After registration, users cannot access chores without joining/creating a household.

---

## Milestone 2: Core Data Models & Administration

- [ ] **Task 2.1: Core Chore Models (`Chore`, `ChoreCycle`, `Bid`)**
  - Define `Chore`: `household` (FK), `title`, `description`, `frequency_days`, `is_active`, `created_at`.
  - Define `ChoreCycle`: `chore` (FK), `cycle_number`, `due_date`, `status` (`BIDDING`, `ASSIGNED`, `COMPLETED`), `assigned_to` (FK User), `completed_at`, `completed_by` (FK User).
  - Define `Bid`: `cycle` (FK ChoreCycle), `user` (FK User), `preference_score` (1–5), `submitted_at`.
  - Add unique constraint: `UniqueConstraint(fields=['cycle', 'user'], name='unique_cycle_user_bid')`.
  - *Acceptance Criteria:* Models migrate cleanly to SQLite with proper relationships and index constraints.

- [ ] **Task 2.2: Model Properties & Helper Methods**
  - Add `@property def is_overdue(self)` on `ChoreCycle`: returns `True` if `status == 'ASSIGNED'` and `due_date < timezone.now()`.
  - Add helper method on `Chore` to spawn an initial or recurring `ChoreCycle`.
  - *Acceptance Criteria:* Unit tests/checks confirm `is_overdue` behaves accurately with past/future dates.

- [ ] **Task 2.3: Django Admin Registration**
  - Register `Household`, `UserProfile`, `Chore`, `ChoreCycle`, and `Bid` in `chores/admin.py`.
  - Configure list displays, search fields, and household filters for administrative oversight.
  - *Acceptance Criteria:* All models can be viewed and managed via the `/admin/` portal.

---

## Milestone 3: Chore Management & Cadence Initiation

- [ ] **Task 3.1: Chore Creation View (`/chores/new/`)**
  - Build `ChoreForm` (fields: `title`, `description`, `frequency_days`).
  - Implement form view ensuring the new chore is automatically assigned to `request.user.userprofile.household`.
  - *Acceptance Criteria:* Submitting the form saves the chore scoped to the current user's household.

- [ ] **Task 3.2: First ChoreCycle Generation**
  - Upon creating a new `Chore`, automatically instantiate cycle #1 with:
    - `status = 'BIDDING'`
    - `cycle_number = 1`
    - `due_date = timezone.now() + timedelta(days=frequency_days)`
  - *Acceptance Criteria:* Newly created chore immediately displays an open cycle waiting for bids.

---

## Milestone 4: Bidding Engine & Assignment Resolution

- [ ] **Task 4.1: Bidding View & Form (`/chores/<cycle_id>/bid/`)**
  - Create `BidForm` with rating selection (1 to 5).
  - Enforce permission checks: only members of the chore's household can submit bids.
  - Prevent duplicate bids from the same user for the same cycle.
  - *Acceptance Criteria:* User can submit a preference score for an active bidding cycle.

- [ ] **Task 4.2: First-to-Bid Quorum Check & Trigger**
  - Following each bid submission, compare total bids received vs. total active household members:
    ```python
    if chore_cycle.bids.count() >= chore_cycle.chore.household.members.count():
        resolve_assignment(chore_cycle)
    ```
  - *Acceptance Criteria:* System automatically detects when all roommates have voted.

- [ ] **Task 4.3: Resolution Algorithm with Random Tie-Breaker**
  - Implement `resolve_assignment(chore_cycle)` logic:
    - Find all bids matching the maximum `preference_score`.
    - If multiple top bidders exist, choose one using `random.choice`.
    - Set `chore_cycle.assigned_to = selected_user` and `chore_cycle.status = 'ASSIGNED'`.
  - *Acceptance Criteria:* Cycle transitions to `ASSIGNED` status with a fairly selected assignee; ties are resolved without error.

---

## Milestone 5: Dashboard & Execution Workflow

- [ ] **Task 5.1: Central Dashboard View (`/dashboard/`)**
  - Build dashboard view aggregating household context:
    - **Pending Bids:** Cycles currently in `BIDDING` where the logged-in user hasn't submitted a bid.
    - **My Assigned Chores:** Cycles assigned to the current user, displaying due date and dynamic `is_overdue` alert badges.
    - **Household Feed:** Other active assignments across household members.
  - *Acceptance Criteria:* Dashboard shows current status, alerts for overdue tasks, and action buttons for pending bids.

- [ ] **Task 5.2: Completion Action & Subsequent Cycle Spawning (`/chores/<cycle_id>/complete/`)**
  - Implement POST endpoint for the assignee to mark a task completed.
  - Update `chore_cycle.status = 'COMPLETED'`, `completed_at = timezone.now()`, and `completed_by = request.user`.
  - Automatically instantiate the next `ChoreCycle` (`cycle_number + 1`) in `BIDDING` status.
  - *Acceptance Criteria:* Completing a task archives it and opens a new bidding cycle for the household.

---

## Milestone 6: History Log & UI Polish

- [ ] **Task 6.1: Completion History View (`/history/`)**
  - Create list view querying `ChoreCycle` objects with `status == 'COMPLETED'` for the household.
  - Display chore title, assigned user, completed timestamp, and whether completed on time (`completed_at <= due_date`).
  - *Acceptance Criteria:* Household members can view a chronological log of all completed chores.

- [ ] **Task 6.2: UI Polish & Responsive Design**
  - Apply clean modern CSS styles (cards, alert badges for overdue status, accessible forms, responsive tables).
  - Ensure intuitive navigation between Dashboard, New Chore, and History.
  - *Acceptance Criteria:* Interface is clean, responsive, and visually highlights critical items (bidding needed, overdue chores).

- [ ] **Task 6.3: Verification & Edge Case Testing**
  - Validate multi-tenant isolation: users cannot see or interact with chores from another household.
  - Test edge cases (single-member households, tie-breaker handling, duplicate bid prevention).
  - *Acceptance Criteria:* All end-to-end flows pass manual and automated verification.

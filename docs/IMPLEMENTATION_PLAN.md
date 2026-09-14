# Implementation plan

Build order for the MVP in [README.md](../README.md). Vocabulary:
[CONTEXT.md](../CONTEXT.md). Style: [CODING_STANDARDS.md](../CODING_STANDARDS.md).

```
backend/          FastAPI service, owns the rules and persistence
frontend/         React + TypeScript + Vite web client
deploy/           docker-compose.yml, Keycloak realm import
```

## Stack

| Area | Decision |
| --- | --- |
| Backend | Python 3.12, FastAPI, `pip` + `venv` |
| Database | One PostgreSQL 16 instance, two databases in it: `mxa` and `keycloak` |
| ORM | SQLAlchemy 2.0 typed models, Alembic |
| Frontend | React 18, TypeScript, Vite, `react-router-dom`, plain CSS, `yarn` |
| Frontend fetching | `fetch` in `services/`, `useState`/`useEffect` in `hooks/` — no query library |
| Auth | Keycloak OIDC, PKCE in the browser, JWT validated against JWKS on the API |
| Week resolution | Client sends seconds since epoch, server resolves it to that week's Monday (ADR 0002) |
| Run | `docker compose` boots Postgres, Keycloak, backend and frontend |
| Tests | `pytest`, `vitest` |
| Lint | `ruff`, `eslint` + `prettier` |

## The rules

Both read the **daily total** — every line item's hours entry for one day,
summed — not individual entries.

**Rejection.** An entry is at least 0. A day with any hours must total more
than 0 and at most 24; an untouched day is skipped. Since entries cannot be
negative, the check to write is the 24 cap. Enforced on save and on submit.

**Highlighting.** A weekday whose daily total is not exactly 8 is a flagged
day. A warning only — never blocks a save or a submit. Saturday and Sunday are
never flagged, and the grid hides them unless asked.

A weekday of 0 is flagged but submittable. A Sunday of 12 is legal and
unflagged. A Monday of 25 is refused.

ADR 0001 puts these rules in the browser and the API. Both sides test the same
boundaries (Phase 1, Phase 8): exactly 24, exactly 8, a weekday of 0, two line
items summing to 25 on one day, an untouched weekend, `7.5 + 0.5 == 8`.

## Data model

Hours are `NUMERIC(4,2)`. `week_start` is always a Monday.

**employees** — Keycloak subjects, upserted on first authenticated request.

| column | type | notes |
| --- | --- | --- |
| `id` | UUID PK | the Keycloak `sub` |
| `email` | text | |
| `display_name` | text | |

**projects**

| column | type | notes |
| --- | --- | --- |
| `id` | UUID PK | |
| `code` | char(6) | UNIQUE |
| `name` | text | |
| `manager_id` | UUID | FK employees.id — the manager who created it |
| `description` | text | |
| `start_date` | date | |
| `created_at` | timestamptz | |

The README's "manager name" is the creating manager, so it is a foreign key
and the API returns `managerName` through the join.

**timesheets**

| column | type | notes |
| --- | --- | --- |
| `id` | UUID PK | |
| `employee_id` | UUID | FK employees.id |
| `week_start` | date | a Monday |
| `status` | text | `draft` \| `submitted` \| `approved` \| `rejected` |
| `submit_message` | text null | employee's note on the last submit |
| `review_message` | text null | manager's note on the approve or reject |
| `submitted_at` | timestamptz null | |
| `reviewed_at` | timestamptz null | |
| `reviewed_by` | UUID null | FK employees.id |

UNIQUE `(employee_id, week_start)`. Two message columns so a rejection reason
survives the employee's next submit.

**timesheet_line_items**

| column | type | notes |
| --- | --- | --- |
| `id` | UUID PK | |
| `timesheet_id` | UUID | FK timesheets.id, ON DELETE CASCADE |
| `project_id` | UUID | FK projects.id |
| `hours_monday` … `hours_sunday` | NUMERIC(4,2) | NOT NULL default 0, CHECK `>= 0 AND <= 24` |

UNIQUE `(timesheet_id, project_id)`. Seven columns rather than a child table:
the week is the only period, so the shape is fixed.

**Transitions.** `draft → submitted`, `submitted → approved` (terminal),
`submitted → rejected`, `rejected → submitted`. Editable in `draft` and
`rejected` only; anything else is a 409.

## API

Under `/api`, all requiring `Authorization: Bearer <token>`. camelCase over the
wire. Hours keyed `monday` … `sunday`. Errors are
`{"detail": "<lowercase sentence>"}`.

| Method | Path | Role | Purpose |
| --- | --- | --- | --- |
| GET | `/api/me` | both | `{employeeId, displayName, role}` |
| POST | `/api/projects` | manager | create; response carries the generated code |
| GET | `/api/projects` | manager | own projects with codes |
| GET | `/api/projects/by-code/{code}` | both | resolve a code to a project name |
| GET | `/api/timesheets?at={epochSeconds}` | employee | own timesheet for that week |
| GET | `/api/timesheets/{status}` | both | timesheets in that status |
| POST | `/api/timesheets/{status}` | both | write a timesheet into that status |

No project list for employees — they reference a project by code only.

### Timesheet representation

Returned by every timesheet endpoint. `dailyTotals` and `flaggedDays` are
computed, never stored. `id` is `null` for a week never saved, so the client
renders an empty grid without special-casing a 404.

```json
{
  "id": "0d7c…",
  "weekStart": "2026-09-14",
  "status": "draft",
  "employeeName": "Alice Dupont",
  "lineItems": [
    {
      "projectCode": "K7M2QX",
      "projectName": "Northwind migration",
      "hours": { "monday": 8, "tuesday": 8, "wednesday": 8, "thursday": 8, "friday": 4, "saturday": 0, "sunday": 0 }
    }
  ],
  "dailyTotals": { "monday": 8, "tuesday": 8, "wednesday": 8, "thursday": 8, "friday": 4, "saturday": 0, "sunday": 0 },
  "totalHours": 36,
  "flaggedDays": ["friday"],
  "submitMessage": null,
  "reviewMessage": null,
  "submittedAt": null,
  "reviewedAt": null
}
```

### GET `/api/timesheets?at={epochSeconds}`

`at` is an integer, seconds since epoch, default now. The server resolves it to
the Monday of that week. Always 200.

### GET `/api/timesheets/{status}`

Full representations, newest week first. Employee sees own; manager sees all.
`/api/timesheets/submitted` is the review queue — whole timesheets, so queue
and detail are one request.

Every manager sees every submitted timesheet; see
[techdebts.md](./techdebts.md). No project-based filtering.

### POST `/api/timesheets/{status}`

One endpoint per transition. `message` is always optional.

| `status` | Role | Required body | Effect |
| --- | --- | --- | --- |
| `draft` | employee | `at`, `lineItems` | upsert the week, stay editable |
| `submitted` | employee | `at`, `lineItems` | save then submit; `message` → `submitMessage` |
| `approved` | manager | `timesheetId` | approve; `message` → `reviewMessage` |
| `rejected` | manager | `timesheetId` | reject; `message` → `reviewMessage` |

```json
{
  "at": 1758099600,
  "lineItems": [
    { "projectCode": "K7M2QX", "hours": { "monday": 8, "tuesday": 0, "wednesday": 0, "thursday": 0, "friday": 0, "saturday": 0, "sunday": 0 } }
  ],
  "message": "short week, was on leave thursday"
}
```

`lineItems` replaces the line items wholesale — one left out is deleted.
Submit saves and transitions in one call, so the grid cannot submit a stale
version. Validate the required fields per status in the route.

| Status | When | `detail` |
| --- | --- | --- |
| 403 | role does not match the status | `"only a manager can approve a timesheet"` |
| 404 | unknown project code | `"no project has code k7m2qz"` |
| 404 | unknown `timesheetId` | `"no timesheet with that id"` |
| 409 | writing over a `submitted` or `approved` timesheet | `"a submitted timesheet cannot be edited"` |
| 409 | approving or rejecting anything but `submitted` | `"only a submitted timesheet can be approved"` |
| 422 | a daily total exceeds 24 | `"monday totals 26 hours; a day cannot exceed 24"` |
| 422 | duplicate project code | `"project code k7m2qx is listed twice"` |
| 422 | negative hours | `"hours cannot be negative"` |
| 422 | submit with no line items | `"a timesheet needs at least one line item before it can be submitted"` |
| 422 | required field missing for that status | `"approving a timesheet needs a timesheetId"` |

Flagged days are never an error — they come back on the 200.

## Project codes

Six characters from uppercase letters and digits, via `secrets.choice`. Insert,
regenerate on a unique violation, 500 after five attempts. Upper-case input on
lookup so codes match case-insensitively.

## Phases

Phases 1, 2, 3, 7 and 8 can start as soon as Phase 0 lands.

```
Phase 0 ──┬── Phase 1 ──┬── Phase 4 ── Phase 5 ── Phase 6
          ├── Phase 2 ──┤
          ├── Phase 3 ──┘
          └── Phase 7 ──┬── Phase 9 ── Phase 10 ── Phase 11 ── Phase 12
                        └── Phase 8 ──┘
```

### Phase 0 — Scaffolding

- `backend/requirements.txt`: fastapi, uvicorn, sqlalchemy, alembic, psycopg,
  pydantic-settings, pyjwt, httpx; `requirements-dev.txt` adds pytest.
  Plus a `Dockerfile`.
- `frontend/package.json`: vite react-ts, react-router-dom, oidc-client-ts,
  react-oidc-context; dev vitest, eslint, prettier, managed with `yarn`. Plus a
  `Dockerfile`.
- `deploy/docker-compose.yml`, four services:
  - `postgres` — an init script creating `mxa` and `keycloak`.
  - `keycloak` — on the `keycloak` database, realm import mounted.
  - `backend` — runs the Alembic migration then uvicorn, on `:8000`.
  - `frontend` — Vite dev server on `:5173`.

  Health checks so `backend` waits on `postgres` and `keycloak`.
- `deploy/keycloak/realm-mxa.json`: realm `mxa`, public client `mxa-web` with
  PKCE and `http://localhost:5173/*` redirects, audience mapper for `mxa-api`,
  realm roles `employee` and `manager`, one seeded employee and one seeded
  manager. Local development only — say so in the README.
- Root `Makefile`, two targets: `up` (compose up, build) and `test` (pytest and
  vitest).
- Settings from the environment: `DATABASE_URL`, `KEYCLOAK_ISSUER`,
  `KEYCLOAK_AUDIENCE`, `CORS_ORIGINS`. No default that differs from a deployed
  value. `docker-compose.yml` reads its own values (DB and Keycloak admin
  credentials, these four) from `deploy/.env`, gitignored, with
  `deploy/.env.example` checked in; the two credential passwords are stored
  base64-encoded there and decoded by the `Makefile` before `docker compose`
  runs.
- README **Setup** section, replacing TBD.

_Done:_ `make up` on a clean machine serves the app at `:5173` against a
migrated database, and `make test` is green.

### Phase 1 — Backend domain core

`backend/app/domain/`, pure Python — no FastAPI, no SQLAlchemy imports.

- `week.py` — `DAYS` (Monday first), `WEEKDAYS`,
  `week_start_for(epoch_seconds)`.
- `hours.py` — `LineItemHours`, `daily_totals`, `days_over_limit`,
  `flagged_days`. `Decimal` throughout.
- `project_code.py` — `generate_project_code()`.
- `review.py` — `EDITABLE_STATUSES`, `submit`, `approve`, `reject`, each
  returning the next status and raising on an illegal transition.

_Done:_ `backend/tests/domain/` covers the boundaries under **The rules**,
`week_start_for` across a week and a year boundary, a generated code being six
characters, and every legal and illegal transition — all with no database
running.

### Phase 2 — Persistence

`app/db.py` (engine, session factory, `get_session`), `app/models.py` (the four
tables, `Mapped[...]` style), initial Alembic migration with the CHECK and
UNIQUE constraints. One `session.commit()` per request, at the end of the
handler.

_Done:_ `alembic upgrade head` builds the schema clean; a test writes a
timesheet with two line items and reads it back.

### Phase 3 — Authentication and roles

`app/auth.py`: cache the realm JWKS, validate the token (signature, `iss`,
`aud`, `exp`), read realm roles, expose `current_employee` (upserting the
subject into `employees`), `require_employee`, `require_manager`. Timeout and
retry the JWKS fetch. A token with both roles or neither is a 403 — do not pick
one. `GET /api/me` ships here.

_Done:_ no token 401, wrong role 403, employee token upserts a row — tested
with a locally signed key, not a live Keycloak.

### Phase 4 — Projects API

`app/api/projects.py` and its schemas. Manager-only creation; the manager comes
from the token, not the body. A `code` in the request body is ignored.

_Done:_ tests cover a six-character code on create, `managerName` from the
join, 403 for an employee, a client-supplied code never reaching the database,
case-insensitive lookup, 404 on an unknown code.

### Phase 5 — Timesheets API, employee side

`app/api/timesheets.py`: `GET /api/timesheets`, `GET /api/timesheets/{status}`,
`POST /api/timesheets/{status}` for `draft` and `submitted`. Resolve the week,
load or create, resolve project codes, run the domain rules, write, serialise
with `dailyTotals` and `flaggedDays`. Scope every query by
`current_employee.id`.

_Done:_ tests cover each relevant error row, flagged days on a 200, a re-save
deleting a dropped line item, an untouched weekend not blocking submit, a day
over 24 refused on both statuses, an empty timesheet refused on submit, 409
editing after submit, 200 editing after reject, a mid-week timestamp resolving
to the right Monday, and one employee unable to read another's week.

### Phase 6 — Review API, manager side

The same handler plus `approved` and `rejected`; open
`GET /api/timesheets/{status}` to managers across all employees.

_Done:_ tests cover only `submitted` in the submitted list, status moves with
`reviewMessage` stored, 409 approving an approved timesheet, 403 for an
employee, and a rejected timesheet editable by its employee again.

### Phase 7 — Frontend foundation

Vite app; `react-oidc-context` on the `mxa-web` client with PKCE;
`services/api.ts` attaching the token and turning `{"detail": …}` into a thrown
`ApiError` with status and detail; `types/` for wire shapes; a role-aware shell
from `GET /api/me` — `/timesheet` for employees, `/projects` and `/review` for
managers. Named exports; `hooks/` state, `services/` HTTP, `types/` types.

_Done:_ the seeded employee lands on the grid, the seeded manager on the queue,
and an expired token returns the user to Keycloak.

### Phase 8 — Frontend rule mirror

`frontend/src/domain/hours.ts` and `week.ts` — same functions and day ordering
as Phase 1. Compare on a rounded value so `7.5 + 0.5` reads as 8.

_Done:_ `hours.test.ts` and `week.test.ts` assert the same outcomes as the
pytest domain suite for every case under **The rules**.

### Phase 9 — Week grid

`pages/TimesheetWeekPage.tsx` with `components/WeekGrid.tsx`,
`LineItemRow.tsx`, `DailyTotalsRow.tsx`, `AddLineItemForm.tsx`.

- A row per line item, a column per day, Monday first, date under each day
  name. Monday to Friday by default, with a "show weekend" toggle.
- Totals row recomputed as the employee types, from `domain/hours.ts`.
- A flagged column is marked by background *and* text, not colour alone, with a
  legend saying a weekday should total 8 hours. Never disables Save or Submit.
- A day over 24 blocks Submit and says which day and by how much.
- Adding a line item takes a code, resolves it via
  `/api/projects/by-code/{code}`, shows the project name or "no project has
  that code".
- Previous/next week, this week on load; navigation sends epoch seconds and
  lets the server pick the Monday.
- Optional message on Submit.
- Submitted and approved are read-only and say so. Rejected is editable and
  shows `reviewMessage`.

_Done:_ an employee fills a week, sees Friday flagged at 4 hours, is blocked at
25 hours on a day, submits with a message, and finds the grid read-only.

### Phase 10 — Projects page

`pages/ProjectsPage.tsx`, `components/ProjectForm.tsx`: name, description,
start date — the manager is the signed-in user, not an input — plus the list of
projects with codes. The new code is shown prominently with a copy affordance.
No code input anywhere.

_Done:_ a manager creates a project, reads the code off the screen, and an
employee adds a line item with it.

### Phase 11 — Review pages

`pages/ReviewQueuePage.tsx`: employee name, week, total hours, flagged-day
indicator, `submitMessage`. `pages/TimesheetReviewPage.tsx`: the employee's
grid read-only with flagged days marked, Approve and Reject with an optional
message. Either outcome removes it from the queue.

_Done:_ a manager opens a submitted timesheet, sees the flagged days, approves
and it leaves the queue; rejecting with a message returns it to the employee as
editable with the message shown.

### Phase 12 — Wiring and setup

End-to-end from `make up` on a clean machine: project creation → code → line
items → submit → approve. Finish README **Setup** with the real commands, the
two dev logins and the ports. Record anything left undone in
[techdebts.md](./techdebts.md).

_Done:_ someone new to the repo follows the README to a working approve.
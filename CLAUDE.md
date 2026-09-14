# CLAUDE.md

Timesheet platform for a small consulting firm.

# Documents
## Reading CODING_STANDARDS.md
Apply its principles. Ignore its paths, service names, and stack references
until this repo has its own.

## Project documents
- Read the [README.md](./README.md) for the project starting point
- [Implementation plan](./docs/IMPLEMENTATION_PLAN.md)
- [ADR](./docs/adr)
- [Techdebt](./docs/techdebts.md)

## Domain rules

The rules that are easy to get subtly wrong. Enforce them consistently
wherever they appear — API, UI, and tests.

**Roles.** Two: employee and manager. Keycloak is the IAM for the MVP, and
roles come from it.

**Projects.** Created by managers only. Fields: project name, manager name,
description, start date. The platform generates a 6-character project code
and displays it — the manager never supplies one. Employees reference a
project by that code.

**Timesheets.** One week is the period. A timesheet holds line items; each
line item is one project code with an hours entry per day of that week,
minimum 0. Whole hours only — no fractions.

**The two hour rules are different, and the difference matters:**

- More than 24 hours on a single day, summed across every line item, is
  **rejected**. A validation error, not a warning.
- A day totalling anything other than 8 hours is **highlighted**. A warning
  only — the employee can still submit.

**Lifecycle.** An employee submits a timesheet; a manager sees submitted
timesheets and approves or rejects. Those two outcomes are the whole review
model.

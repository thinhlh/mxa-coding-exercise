# MXA Timesheet

Timesheet platform for a small consulting firm. Employees record the hours they
work against projects, one week at a time, and managers approve or reject what
they submit.

## Language

### People

**Employee**:
A person who records hours. One of the two roles; every user is an employee or
a manager, never both.
_Avoid_: consultant, staff, user, resource

**Manager**:
A person who creates projects and reviews submitted timesheets.
_Avoid_: approver, supervisor, admin, lead

### Recording time

**Timesheet**:
One employee's hours for one week. The unit that gets submitted, approved and
rejected — there is no smaller thing a manager acts on.
_Avoid_: timecard, time report, submission

**Week**:
Monday to Sunday. The only period a timesheet covers.
_Avoid_: period, pay period, cycle, sprint

**Line item**:
One project code within a timesheet, holding an hours entry for each day of the
week. An employee adds a line item by entering a project code.
_Avoid_: row, task, activity, booking

**Hours entry**:
The hours recorded on one line item for one day. Minimum 0.
_Avoid_: cell, slot, unit

**Daily total**:
The sum of every line item's hours entry for a single day. Both hour rules judge
this number, not the individual entries.
_Avoid_: day sum, total

### Projects

**Project**:
Work an employee books hours against. Created by a manager, who supplies a
project name, manager name, description and start date.
_Avoid_: client, engagement, job, matter

**Project code**:
The six-character identifier the platform generates for a project and displays
to its manager. Employees reference a project by this code and nothing else. No
part of it is ever supplied by a person.
_Avoid_: project ID, project number, code prefix

### Review

**Submit**:
The employee sends a timesheet to be reviewed, after which it cannot be edited.
_Avoid_: send, file, lock, finalise

**Approve**:
A manager accepts a submitted timesheet. Terminal.

**Reject**:
A manager declines a submitted timesheet, returning it to the employee to edit
and submit again.
_Avoid_: return, send back, decline, deny

**Flagged day**:
A weekday whose daily total is not exactly 8 hours. A warning shown to the
employee and the reviewing manager — it never prevents submission. Saturday and
Sunday are never flagged.
_Avoid_: violation, error, exception

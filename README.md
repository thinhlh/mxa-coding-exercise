# Timesheet platform

Timesheet platform to help consultants at a small firm to bill their time to clients.
The timesheet should help consultant capture time against billable work as they go and get a period's timesheet into a state where it can be submitted for approval.

# Specificications

The specifications and features list are declared below. The product is aimed for MVP with core feature to be delivered.

## Actors

The timesheet platforms has 2 main actors

### Consultants/Employees

There are the users that use the timesheet, to log their working hour to the system.

### Manager

- Manager will create a project with a project code. For each time the consumer log there working hour, they will enter this project code
- Manager also will be in charge for approval/reject the submitted timesheet at the end of the period

## Authentication/Authorization

The timesheet need to know about who is interacting with the platform. There are 2 roles: employees/manager.
Keycloak should be used as IAM for MVP

## Project creation

- The manager will have permission to create the project. The project they created will generate a 6 characters code for the employees to enter into the timesheet. Project only need some below information for MVP:

1. Project name
2. Manager name
3. Description
4. Start date

- The platform will auto gen a project code and show that.

## Timesheet logging

- The employees will be able to log the timesheet on their working hour. Their timesheet can be submitted during a short period (weekly).
- Each time sheet will allow the employees to
  - Add a new line item to add to their timesheet. This lineitem imply the project code.
  - For each day in a week, they can enter the hour they work for the project, minimum 0
- They can submit the timesheet to the manager for review.

## Timesheet review

- The timesheet submitted by the employee will be visible to the manager section so that they can review them. Manager can either approve or reject the time sheet

# Functional requirements

- All functional required must be correct.
- Application should be tested, from unit test
- Employees can not submit more than 24 hours a day. Day with != 8hours will be highlighted
- Components should not be tighten since later on, I want to build interfaces to interact with the timesheet, such as genAI, mobile apps,... not just limited to web.

# Non functional requirements

- This is MVP focused. Application & code should be simple, human readable, easy to read, no hacky code.

# Setup

TBD

# Assumptions, Tradeoffs & Propsoal

This page is hand-written, dedicated to decision/assumption that has been made in order

# Assumption

- Assuming that a consultant can work on multi project perday
- Each project can by created & owned by that manager. And that manager can approve for the timesheet.\
- Assuming we can skip the overtime flow for this platform and can add for now. We are assuming that each employee should work for 8 hours a day.
- Project creation with generated project code
- Weekend work is optional. Employees/consultants will not be flagged if they works different than 8 hours.

# Tradeoffs

Due to time constraints, tradeoffs & evaluation need to be decided depends on the effort & priority. I prioritize the flow for auth & timesheet first, then approval & other extension features

- Authentication using keycloak for fast spin up
- We use docker compose for local spin up, this is the dev setup & not ready for production.
- We use local postgres backend for this exercise only.

# Proposal

- genAI implementation as MCP for the consultant to chat & submit timesheet
- Missing the overtime calculation, reject & re submit
- Full deployment with DB,BE,FE, Auth, CI/CD pipeline or comparing cost with third party.
- Link with internal tools like submit casing, exceptional approval, etc.
- Cron job check for in draft request and send notification before deadline

# Techdebts

- Because there is a case that a consultant can work on multiple projects and that need approval from other managers, I am assuming that 1 manager can approve the timesheet.
- Not yet check if the users timesheet lineitem should be before the time.
- A page where the managers can view list of submitted timesheets for the projects.
- Should need more time to optimize & deeply review the code

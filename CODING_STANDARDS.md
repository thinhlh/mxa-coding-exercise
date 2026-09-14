# Coding Standards

How code is written in this repo.

Everything here is a default, not a law. Break a rule when you can say why in
one sentence — then say it, in the PR description, not in a comment.

## 1. Don't over-engineer

Build what is asked for, working, and nothing beyond it.

- **No speculative abstraction.** No base class, registry, strategy, factory,
  or config flag for a second case that does not exist yet. Write the one case.
- **Duplicate twice before you abstract.** Two similar blocks are fine. The
  third is the signal — and the abstraction should then be obvious, not invented.
- **No defensive scaffolding.** No try/except that swallows and logs so the
  caller "keeps working", no `getattr(x, "y", None)` on types you control, no
  null-checks for things that cannot be null. Let it raise.
- **Prefer deleting to adding.** A refactor should end with fewer lines than it
  started with. If it ends with more, say what the extra lines buy.
- **One indirection layer, not three.** Route → module function → DB. Don't add
  a service class that only forwards to a repository that only forwards to the
  ORM.
- **No new dependency** for something 20 lines of stdlib does.

## 2. Best practice, with the tradeoff stated

Apply the practice when it pays here, at this size, on this branch. When a
practice and simplicity collide, choose deliberately and record the choice
where a reviewer will see it — the PR description, or `docs/techdebts.md` if we
are knowingly carrying debt.

Worked examples of the judgement:

- **Transactions**: one `session.commit()` per request at the end of the
  handler. Don't reach for a unit-of-work wrapper.
- **Validation**: Pydantic schemas at the API boundary only. Inside the
  service, trust your own types.
- **Retries / timeouts**: on every outbound call to LiteLLM, Keycloak, S3, k8s,
  and agent pods. Not on in-process calls.
- **Caching**: only with a measurement behind it. Say what was slow.
- **Config**: a new env var is a one-line addition to `configs.<service>` in
  `deployment/app/values.<env>.yaml` (see `CLAUDE.md`). Never a template edit,
  never a hardcoded default that silently differs from prod.
- **Security is not negotiable** in this trade-off. Agent pods run untrusted
  producer code: no AWS credentials, no internal API keys, no master LiteLLM
  key ever reaches them. Never widen that boundary for convenience.

## 3. Comments: let the code speak

Default to zero comments. Naming and structure carry the meaning.

Delete on sight:

```python
# Get the user from the database
user = session.get(User, username)

# Loop over agents
for agent in agents:
```

Keep only these four kinds:

1. **Module docstring** — one line saying what the module owns. Every Python
   module here has one; match that.
2. **Why, never what** — a non-obvious constraint the code cannot state itself:
   `# LiteLLM assigns its own agent_id; ours is rejected by /a2a/{id}`.
3. **Public contract** — a docstring on a function whose behaviour surprises
   its signature (a local-dev bypass, a lazy upsert side-effect).
4. **Deliberate suppression** — `# noqa: BLE001 — broad by design (jwt errors)`.

Never:

- Commented-out code. Delete it; git remembers.
- Section banners (`# ---- helpers ----`).
- Changelog comments (`# added retry`, `# was 30s before`). That's the commit.
- A comment restating a docstring, or a docstring restating the signature.
- `TODO` without an owner and a reason. Prefer an entry in `docs/techdebts.md`.

## 4. No ticket or task references in code

Code and comments must never mention a ticket, issue, plan file, branch name,
phase number, or PR — unless the user explicitly asked for that reference.

```python
# AGM-214: normalize the agent id           ← no
# TD-4 phase 2 cleanup                      ← no
# per plans/billing-refactor.md step 3      ← no
```

Ticket context belongs in the commit message and PR description. A reader of
the code six months from now has no access to the tracker, so any reason worth
keeping must be written out as a reason:

```python
# LiteLLM rejects our agent id on /a2a/{id}, so store the one it assigns.
```

Same rule for identifiers: no `handle_agm214_case`, no `phase2_registry`,
no `v2_new` suffixes.

## 5. Write for the reviewer

The reader is a person on a diff, not an author with the whole file in their
head.

- **Small, single-purpose diffs.** One concern per commit. Don't reformat
  untouched lines or rename things in passing — it hides the real change.
- **Shallow functions.** Under ~40 lines, one level of abstraction, early
  returns over nested `if`. If you need a comment to explain a block, extract
  it into a named function instead.
- **Names are the documentation.** `resolve_litellm_key`, not `process`. No
  `data`, `info`, `tmp`, `mgr`, `do_it`. Spell it out; length is cheap.
- **Domain vocabulary, consistently**: agent, flow, producer, consumer,
  publish, deploy, invoke, snapshot. Don't invent a synonym for one that exists.
- **Match the file you are in.** Conventions here that are already established:
  `from __future__ import annotations`, relative imports inside the package,
  typed signatures, `logging.getLogger(__name__)` and lazy `%s` log args,
  `HTTPException` with a lowercase detail string at the boundary; in the UI,
  hooks in `hooks/`, HTTP in `services/`, types in `types/`, named exports,
  camelCase over the wire where the backend already uses it (`isFavorite`).
- **Errors say what failed and what to do.** Not `"error"`. Not a stack trace
  in a user-facing string, and never a token, key, or email in a log line.
- **Docs travel with the change.** Behaviour described in `docs/**` or
  `CLAUDE.md` must be updated in the same commit — this is a hard rule here.

## 6. Tests

Don't add tests unless asked.

## 7. Do not involve AI agent in commit author & message

Do not involve or add any AI agent as author or commit message

## 8. Do not use hacky code

Identify hacky code and do not make changes over them. Rather than that, propose tradeoff and action needed.

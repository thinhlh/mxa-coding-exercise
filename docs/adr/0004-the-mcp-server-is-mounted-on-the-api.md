# The MCP server is mounted on the API

A genAI client needs the same two things the browser needs — the hour rules applied
to what it writes, and a real employee behind the request. Running it as its own
service would mean a second copy of the rules and a second answer to who is calling,
and the two would drift.

So the MCP server is mounted on the FastAPI app and takes the same `Authorization:
Bearer` token the REST API already takes. A `TokenVerifier` hands that token to the
same JWKS check `current_employee` runs, so the role still comes from
`realm_access.roles` and a tool reaches nothing a browser request could not. The
tools are a vocabulary over the endpoints, not a second way into the data.

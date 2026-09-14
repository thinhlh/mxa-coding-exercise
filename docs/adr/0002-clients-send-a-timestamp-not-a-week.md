# Clients send a timestamp, not a week

A client picking the week itself has to know that a week starts on Monday and
get the arithmetic right — and every client the README expects, web, mobile and
genAI, would have to get it right the same way.

So a client sends `at`: seconds since epoch, anywhere inside the week it means.
The server resolves it to that week's Monday. There is no invalid week to
reject and no week-boundary rule outside the backend.

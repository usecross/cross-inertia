---
release type: patch
---

Callable props now resolve outside the event loop on sync requests. Sync
callables, including those in `optional`, `always`, `defer` and `once`, run in
the request's own thread, so Django ORM queries work in them instead of raising
`SynchronousOnlyOperation`. Only a coroutine a callable returns gets an event
loop. Async callables resolve as before.

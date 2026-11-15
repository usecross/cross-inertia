---
release type: patch
---

Callable props now resolve outside the event loop on sync requests. Sync
callables, including those in `optional`, `always`, `defer` and `once`, run in
the request's own thread, so Django ORM queries work in them instead of raising
`SynchronousOnlyOperation`. Only coroutines that callables return get an event
loop, and all of them in one render share it, so a task or client one async
prop creates still works in the next. Plain values and sync callables never
create a loop or a thread. Async callables resolve as before.

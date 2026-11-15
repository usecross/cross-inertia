---
release type: patch
---

Props in a sync render share one context again, as they did before 0.22.2. A
`ContextVar` that one prop sets is visible to later props, including async ones,
and async props see the context the request set before rendering, even inside a
running event loop. Changes still do not leak back to the caller. On Python
3.10, an async prop's own changes stay inside that prop.

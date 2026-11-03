---
release type: minor
---

Adds live props (Inertia v3). `live(value, channel, *events)` marks a prop the
client keeps up to date: every page lists each live prop's channels and events
in `liveProps`, and the client refreshes the prop when one of those events is
broadcast. `cross_inertia.broadcasting` publishes events over the Pusher HTTP
API (Pusher, Laravel Reverb, Soketi), optionally with the props' new values, and
signs private and presence channel subscriptions. Django gets `broadcast()`,
`abroadcast()` and `channel_auth_view()` in `cross_inertia.django.broadcasting`,
configured by `CROSS_INERTIA["BROADCASTING"]`.

Also, callable props now resolve outside the event loop on sync requests, so
Django ORM queries work in them (including in `optional`, `always`, `defer` and
`once`) instead of raising `SynchronousOnlyOperation`.

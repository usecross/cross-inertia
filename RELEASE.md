Release type: patch

Fix Vite health check endpoint

Use `/@vite/client` endpoint for health checks instead of root path (`/`).
The root path may return 404 depending on Vite configuration, but `/@vite/client`
always returns 200 when Vite is running.

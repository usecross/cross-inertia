

0.14.0 - 2026-02-03
-------------------

Make `vite_port="auto"` the default

- Change default `vite_port` from `5173` to `"auto"` so Vite automatically finds an available port
- Fix port detection to check both IPv4 and IPv6, preventing false positives when servers listen on IPv6
- All Vite-related classes and functions now read from config when port is not specified

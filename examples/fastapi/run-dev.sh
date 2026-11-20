#!/bin/bash
# Development runner script for the Inertia FastAPI example

set -e -o pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

export INERTIA_VITE_PORT="${INERTIA_VITE_PORT-5173}"
if [[ ! $INERTIA_VITE_PORT =~ ^[0-9]{1,5}$ ]] ||
    (( 10#$INERTIA_VITE_PORT < 1 || 10#$INERTIA_VITE_PORT > 65535 )); then
    printf 'INERTIA_VITE_PORT must be an integer from 1 to 65535 (got %q).\n' "$INERTIA_VITE_PORT" >&2
    exit 1
fi
vite_url="http://127.0.0.1:$((10#$INERTIA_VITE_PORT))"
api_port="${FASTAPI_PORT:-8000}"

# Use an installed Node when a global Vite+ shim would provision its own runtime.
case "$(command -v node)" in
    */.vite-plus/bin/node)
        while IFS= read -r node_path; do
            case "$node_path" in
                */.vite-plus/bin/node) continue ;;
            esac
            export PATH="${node_path%/*}:$PATH"
            break
        done < <(type -aP node)
        ;;
esac

if [ ! -x node_modules/.bin/vite ]; then
    echo "Installing frontend dependencies..."
    if command -v bun > /dev/null; then
        bun install --frozen-lockfile
    else
        npm install
    fi
fi

vite_headers() {
    curl --noproxy '*' --fail --silent --max-time 1 --dump-header - \
        "$vite_url/@vite/client" -o /dev/null
}

if vite_headers >/dev/null; then
    echo "A server is already serving Vite assets at $vite_url. Stop it or set INERTIA_VITE_PORT." >&2
    exit 1
fi

cleanup() {
    for pid in ${vite_pid:+"$vite_pid"} ${api_pid:+"$api_pid"}; do
        kill -TERM -- "-$pid" 2>/dev/null || true
        kill -CONT -- "-$pid" 2>/dev/null || true
    done
    wait
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Give each server its own process group so cleanup includes its children.
set -m
launcher_id="$$-$RANDOM-$RANDOM"
INERTIA_VITE_LAUNCHER_ID="$launcher_id" node_modules/.bin/vite </dev/null &
vite_pid=$!

deadline=$((SECONDS + 30))
while kill -0 "$vite_pid" 2>/dev/null; do
    # Another launcher can win the bind while this Vite process is starting.
    if vite_headers | tr -d '\r' | grep -Fxi "X-Inertia-Vite-Launcher: $launcher_id" >/dev/null; then
        break
    fi
    if (( SECONDS >= deadline )); then
        echo "Vite did not become ready at $vite_url within 30 seconds." >&2
        exit 1
    fi
    sleep 0.2
done

if ! kill -0 "$vite_pid" 2>/dev/null; then
    echo "Vite stopped before it was ready." >&2
    exit 1
fi

echo "Open http://127.0.0.1:$api_port once FastAPI starts. Press Ctrl+C to stop both servers."
UV_PYTHON="${UV_PYTHON:->=3.12,<3.15}" \
    uv run --locked fastapi dev main.py --host 127.0.0.1 --port "$api_port" </dev/null &
api_pid=$!

while kill -0 "$vite_pid" 2>/dev/null && kill -0 "$api_pid" 2>/dev/null; do
    sleep 0.2
done
echo "A development server stopped unexpectedly." >&2
exit 1

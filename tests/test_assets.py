"""Tests for Vite manifest asset resolution."""

from cross_inertia._assets import (
    build_asset_url,
    normalize_entry_key,
    resolve_manifest_entry,
)


class TestNormalizeEntryKey:
    def test_strips_dot_slash_prefix(self):
        assert normalize_entry_key("./src/main.tsx") == "src/main.tsx"

    def test_backslash_to_forward_slash(self):
        assert normalize_entry_key("src\\main.tsx") == "src/main.tsx"

    def test_no_op_for_clean_key(self):
        assert normalize_entry_key("src/main.tsx") == "src/main.tsx"

    def test_preserves_keys_starting_with_s(self):
        """Regression: lstrip('./') would strip leading 's' from 'static/...'."""
        assert normalize_entry_key("static/app.tsx") == "static/app.tsx"

    def test_preserves_dotdot_prefix(self):
        assert normalize_entry_key("../foo.tsx") == "../foo.tsx"


class TestResolveManifestEntry:
    def test_exact_match(self):
        manifest = {"frontend/app.tsx": {"file": "assets/app.js"}}
        key, entry = resolve_manifest_entry(manifest, "frontend/app.tsx")
        assert key == "frontend/app.tsx"
        assert entry["file"] == "assets/app.js"

    def test_normalized_key_match(self):
        manifest = {"./src/main.tsx": {"file": "assets/main.js"}}
        key, entry = resolve_manifest_entry(manifest, "src/main.tsx")
        assert key == "./src/main.tsx"
        assert entry["file"] == "assets/main.js"

    def test_basename_match_single(self):
        manifest = {"src/app.tsx": {"file": "assets/app.js"}}
        key, entry = resolve_manifest_entry(manifest, "frontend/app.tsx")
        assert key == "src/app.tsx"
        assert entry["file"] == "assets/app.js"

    def test_basename_match_ambiguous_returns_none(self):
        manifest = {
            "src/app.tsx": {"file": "assets/app1.js"},
            "lib/app.tsx": {"file": "assets/app2.js"},
        }
        key, entry = resolve_manifest_entry(manifest, "frontend/app.tsx")
        assert key is None
        assert entry is None

    def test_is_entry_match(self):
        manifest = {
            "src/main.tsx": {"file": "assets/main.js", "isEntry": True},
            "src/vendor.js": {"file": "assets/vendor.js"},
        }
        key, entry = resolve_manifest_entry(manifest, "totally/different.tsx")
        assert key == "src/main.tsx"
        assert entry["file"] == "assets/main.js"

    def test_sole_entry_fallback(self):
        manifest = {"only-entry.tsx": {"file": "assets/only.js"}}
        key, entry = resolve_manifest_entry(manifest, "no/match.tsx")
        assert key == "only-entry.tsx"
        assert entry["file"] == "assets/only.js"

    def test_no_match_returns_none(self):
        manifest = {
            "a.tsx": {"file": "a.js"},
            "b.tsx": {"file": "b.js"},
        }
        key, entry = resolve_manifest_entry(manifest, "c.tsx")
        assert key is None
        assert entry is None

    def test_skips_non_dict_entries(self):
        manifest = {
            "frontend/app.tsx": "not-a-dict",
            "src/main.tsx": {"file": "assets/main.js"},
        }
        key, entry = resolve_manifest_entry(manifest, "frontend/app.tsx")
        # Exact match fails because value is not a dict; falls through to sole entry
        assert key == "src/main.tsx"


class TestBuildAssetUrl:
    def test_basic(self):
        assert (
            build_asset_url("/static/build", "assets/app.js")
            == "/static/build/assets/app.js"
        )

    def test_strips_trailing_slash_from_prefix(self):
        assert (
            build_asset_url("/static/build/", "assets/app.js")
            == "/static/build/assets/app.js"
        )

    def test_strips_leading_slash_from_path(self):
        assert (
            build_asset_url("/static/build", "/assets/app.js")
            == "/static/build/assets/app.js"
        )

    def test_both_slashes(self):
        assert (
            build_asset_url("/static/build/", "/assets/app.js")
            == "/static/build/assets/app.js"
        )

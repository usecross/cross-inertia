# Cross-Inertia TODO & Framework Support

This document tracks both tasks and framework support status for the cross-inertia project.

---

## 🏗️ Current Tasks

### ✅ Completed
- [x] Fix template HTML escaping issue in tests (Nov 2024)
- [x] Integrate lia-web for framework abstraction (Nov 2024)
- [x] Update tests to use lia adapters (Nov 2024)
- [x] Build system migration (uv_build → hatchling) (Nov 2024)

### 🚧 In Progress
- [ ] None currently

### 📋 Backlog

#### High Priority
- [ ] **Asset version mismatch handling** (Critical for production)
  - Implement 409 Conflict response when version changes
  - Check `X-Inertia-Version` header
  - Return `X-Inertia-Location` for forced reload
  - Effort: 2-3 hours
  - See: `tests/test_assert_versioning.py` (currently skipped)
  - Reference: [Inertia Protocol - Asset Versioning](https://inertiajs.com/the-protocol#asset-versioning)

- [ ] **Partial reloads**
  - Check `X-Inertia-Partial-Data` and `X-Inertia-Partial-Component` headers
  - Filter props to only include requested keys
  - Effort: 6-8 hours
  - See: `tests/test_partial_reloads.py` (currently skipped)
  - Reference: [Partial Reloads](https://inertiajs.com/partial-reloads)

- [ ] **Missing page object fields**
  - Add `encryptHistory`, `clearHistory`, `mergeProps`, etc.
  - Required for advanced features
  - Effort: 1-2 hours
  - Reference: [Page Object](https://inertiajs.com/the-protocol#the-page-object)

#### Medium Priority
- [ ] **Shared data middleware**
  - Implement middleware for auth, flash messages, global data
  - Effort: 4-5 hours
  - Reference: [Shared Data](https://inertiajs.com/shared-data)

- [ ] **External redirects**
  - Implement 409 + `X-Inertia-Location` for external URLs
  - OAuth, logout flows
  - Effort: 1-2 hours
  - Reference: [External Redirects](https://inertiajs.com/redirects#external-redirects)

- [ ] **Lazy props evaluation**
  - Implement lazy prop wrapper
  - Only evaluate when needed for partial reloads
  - Effort: 3-4 hours
  - Reference: [Lazy Evaluation](https://inertiajs.com/partial-reloads#lazy-data-evaluation)

- [ ] **Deferred props**
  - Progressive data loading after initial render
  - Effort: 6-8 hours
  - Reference: [Deferred Props](https://inertiajs.com/deferred-props)

- [ ] **Merging props (infinite scroll)**
  - Support for `mergeProps`, `prependProps`, `deepMergeProps`
  - Effort: 4-5 hours
  - Reference: [Merging Props](https://inertiajs.com/merging-props)

#### Low Priority
- [ ] **Error bags**
  - Multiple forms on one page
  - Check `X-Inertia-Error-Bag` header
  - Effort: 1-2 hours
  - Reference: [Error Bags](https://inertiajs.com/validation#error-bags)

- [ ] **Prefetch support**
  - Detect `Purpose: prefetch` header
  - Effort: 2-3 hours
  - Reference: [Prefetching](https://inertiajs.com/prefetching)

- [ ] **History encryption**
  - Support `encryptHistory` and `clearHistory`
  - For sensitive data in history
  - Effort: 3-4 hours
  - Reference: [History Encryption](https://inertiajs.com/history-encryption)

- [ ] **Polling support**
  - Auto-refresh data (mostly client-side)
  - Effort: Low (client-side mostly)
  - Reference: [Polling](https://inertiajs.com/polling)

---

## 📦 Framework Support Status

Cross-inertia uses [lia](https://github.com/patrick91/lia) for framework abstraction, enabling support for multiple Python web frameworks.

### ✅ Supported Frameworks

#### FastAPI / Starlette
- **Status:** ✅ Fully Supported
- **Adapter:** `StarletteRequestAdapter`
- **Since:** v0.1.0
- **Notes:** Primary development target
- **Tested:** ✅ Yes

### 🚧 Framework Support Roadmap

The following frameworks are supported by lia and can be integrated:

#### Flask
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`FlaskHTTPRequestAdapter`, `AsyncFlaskHTTPRequestAdapter`)
- **Effort:** Medium (2-3 days)
- **Requirements:**
  - [ ] Adapt template rendering for Flask (Jinja2 is compatible)
  - [ ] Create Flask-specific dependency injection pattern
  - [ ] Add Flask integration tests
  - [ ] Update documentation

#### Django
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`DjangoHTTPRequestAdapter`, `AsyncDjangoHTTPRequestAdapter`)
- **Effort:** Medium-High (3-4 days)
- **Requirements:**
  - [ ] Adapt template rendering for Django templates
  - [ ] Create Django middleware/decorator pattern
  - [ ] Handle Django's CSRF token
  - [ ] Add Django integration tests
  - [ ] Update documentation

#### Sanic
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`SanicHTTPRequestAdapter`)
- **Effort:** Medium (2-3 days)
- **Requirements:**
  - [ ] Adapt template rendering
  - [ ] Create Sanic-specific dependency injection
  - [ ] Add Sanic integration tests
  - [ ] Update documentation

#### Aiohttp
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`AiohttpHTTPRequestAdapter`)
- **Effort:** Medium (2-3 days)
- **Requirements:**
  - [ ] Adapt template rendering
  - [ ] Create aiohttp-specific middleware pattern
  - [ ] Add aiohttp integration tests
  - [ ] Update documentation

#### Quart
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`QuartHTTPRequestAdapter`)
- **Effort:** Low-Medium (1-2 days)
- **Requirements:**
  - [ ] Adapt template rendering (similar to Flask)
  - [ ] Create Quart-specific dependency injection
  - [ ] Add Quart integration tests
  - [ ] Update documentation

#### Litestar
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`LitestarRequestAdapter`)
- **Effort:** Medium (2-3 days)
- **Requirements:**
  - [ ] Adapt template rendering
  - [ ] Create Litestar-specific dependency injection
  - [ ] Add Litestar integration tests
  - [ ] Update documentation

#### Chalice (AWS Lambda)
- **Status:** 🔴 Not Yet Supported
- **Adapter Available:** ✅ Yes (`ChaliceHTTPRequestAdapter`)
- **Effort:** Medium-High (3-4 days)
- **Requirements:**
  - [ ] Adapt for serverless environment
  - [ ] Handle asset loading in Lambda
  - [ ] Special considerations for static files
  - [ ] Add Chalice integration tests
  - [ ] Update documentation

### 🎯 Framework Support Implementation Plan

#### Phase 1: Core Framework Support (v0.5.0)
**Goal:** Support the top 3 Python web frameworks

1. **Flask** (Most popular traditional framework)
   - Widest adoption
   - Similar to FastAPI in simplicity
   - Jinja2 compatible

2. **Django** (Most popular full-stack framework)
   - Large enterprise user base
   - Different template system
   - More complex integration

3. **Sanic** (Popular async framework)
   - Similar to FastAPI
   - Growing adoption
   - Async-first

**ETA:** 2-3 weeks of focused work

#### Phase 2: Extended Support (v0.6.0)
**Goal:** Support additional async frameworks

4. **Aiohttp**
5. **Quart**
6. **Litestar**

**ETA:** 1-2 weeks of focused work

#### Phase 3: Serverless Support (v0.7.0)
**Goal:** Support AWS Lambda deployment

7. **Chalice**

**ETA:** 1 week of focused work

### 🔧 Framework Integration Checklist

For each new framework, complete:

- [ ] **Request Adapter Integration**
  - [ ] Create framework-specific initialization
  - [ ] Test all request properties (headers, url, method, etc.)
  - [ ] Handle framework-specific quirks

- [ ] **Template Rendering**
  - [ ] Integrate with framework's template system
  - [ ] Ensure `{{ vite() }}` function works
  - [ ] Test HTML response generation

- [ ] **Response Generation**
  - [ ] Test JSON responses for Inertia requests
  - [ ] Test HTML responses for initial loads
  - [ ] Verify all headers are set correctly

- [ ] **Dependency Injection / Middleware**
  - [ ] Create framework-specific pattern for getting Inertia instance
  - [ ] Document the pattern
  - [ ] Provide example usage

- [ ] **Testing**
  - [ ] Port all existing tests to new framework
  - [ ] Add framework-specific tests
  - [ ] Ensure 100% test coverage

- [ ] **Documentation**
  - [ ] Add installation instructions
  - [ ] Add quick start guide
  - [ ] Add example project
  - [ ] Update README.md

- [ ] **Examples**
  - [ ] Create minimal example project
  - [ ] Show common patterns
  - [ ] Include in `/examples` directory

---

## 🗺️ Version Roadmap

### v0.2.0 - "Production Ready"
- [ ] Asset version mismatch handling
- [ ] Page object missing fields
- [ ] External redirects
- [ ] Basic integration tests
- [ ] Performance benchmarks

### v0.3.0 - "Performance"
- [ ] Partial reloads
- [ ] Lazy props evaluation
- [ ] Shared data middleware

### v0.4.0 - "Advanced Features"
- [ ] Deferred props
- [ ] Merging props
- [ ] Error bags
- [ ] Prefetching support

### v0.5.0 - "Multi-Framework"
- [ ] Flask support
- [ ] Django support
- [ ] Sanic support

### v0.6.0 - "Extended Framework Support"
- [ ] Aiohttp support
- [ ] Quart support
- [ ] Litestar support

### v0.7.0 - "Serverless"
- [ ] Chalice support
- [ ] AWS Lambda optimizations

### v1.0.0 - "Stable Release"
- [ ] All high/medium priority features
- [ ] Support for 3+ frameworks
- [ ] 100% test coverage
- [ ] Published to PyPI
- [ ] API stability guarantee

**Estimated Timeline:** 6-8 months of focused development

---

## 🤝 Contributing

Want to help? Here's what we need:

### 🔥 Hot Tasks (Most Valuable)
1. **Asset version mismatch** - Critical for production (2-3 hours)
2. **Flask support** - Most requested framework (2-3 days)
3. **Partial reloads** - Major performance win (6-8 hours)

### 🌟 Good First Issues
- External redirects (1-2 hours)
- Error bags (1-2 hours)
- Page object fields (1-2 hours)
- Quart support (1-2 days, similar to Flask)

### 📋 Process
1. Pick a task from this TODO
2. Check if there are related skipped tests
3. Read the Inertia.js documentation
4. Implement following existing patterns
5. Write/update tests
6. Update this TODO
7. Submit a PR

---

## 📊 Progress Tracking

### Overall Completion
- **Core Features:** 60% complete
- **Production Critical:** 0% complete
- **Advanced Features:** 0% complete
- **Framework Support:** 10% complete (1 of 8 frameworks)

### By Priority
- 🔴 **High Priority:** 0/3 complete
- 🟡 **Medium Priority:** 0/5 complete
- 🟢 **Low Priority:** 0/4 complete

### By Framework
- ✅ **FastAPI/Starlette:** Fully supported
- 🔴 **All Others:** Not yet supported

---

## 📝 Notes

### Design Decisions
- **Template rendering:** Keep outside of lia, framework-specific in cross-inertia
- **Request handling:** Use lia adapters for all framework differences
- **Response generation:** Framework-agnostic where possible, specific converters where needed

### Future Considerations
- Consider SSR support (requires Node.js runtime)
- Consider WebSocket support for live updates
- Consider GraphQL integration patterns

---

**Last Updated:** November 2024
**Version:** 0.1.0 (Alpha)

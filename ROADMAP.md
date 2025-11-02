# Cross-Inertia Roadmap

This document provides a high-level overview of the project roadmap. For detailed tasks and progress, see [GitHub Issues](https://github.com/patrick91/cross-inertia/issues).

---

## 📦 Framework Support Status

### ✅ Supported
- **FastAPI / Starlette** - Fully supported and tested

### 🚧 Planned
See [GitHub Issues](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3Aframework-support) for framework support requests:
- [Flask](https://github.com/patrick91/cross-inertia/issues/7)
- [Django](https://github.com/patrick91/cross-inertia/issues/8)

---

## 🗺️ Version Milestones

### v0.2.0 - "Production Ready" ✅ COMPLETE
All production-critical features implemented:
- ✅ Asset version mismatch handling
- ✅ External redirects  
- ✅ Partial reloads
- ✅ Shared data
- ✅ History encryption
- ✅ E2E integration tests

### v0.3.0 - "Performance"
Focus on optimization and developer experience:
- [Lazy props evaluation](https://github.com/patrick91/cross-inertia/issues/2)
- [Deferred props](https://github.com/patrick91/cross-inertia/issues/3)
- Performance benchmarks

### v0.4.0 - "Advanced Features"
Additional Inertia.js protocol features:
- [Merging props (infinite scroll)](https://github.com/patrick91/cross-inertia/issues/4)
- [Error bags](https://github.com/patrick91/cross-inertia/issues/5)
- [Prefetching support](https://github.com/patrick91/cross-inertia/issues/6)

### v0.5.0 - "Multi-Framework"
Expand framework support:
- Flask support
- Django support  
- Sanic support

### v1.0.0 - "Stable Release"
Production-ready stable release:
- All high/medium priority features
- Support for 3+ frameworks
- 80%+ test coverage
- Published to PyPI
- API stability guarantee

---

## 📊 Current Status

**Latest Version:** v0.2.0 (Production Ready)

**Core Protocol:** 95% complete
- ✅ Request/response handling
- ✅ Partial reloads
- ✅ History encryption
- ✅ External redirects
- 🚧 Advanced features (lazy/deferred props, merging)

**Framework Support:** 12% complete (1 of 8 planned frameworks)
- ✅ FastAPI/Starlette
- 🚧 Flask, Django, Sanic, etc. (planned)

**Test Coverage:** 71%
- Unit tests: 37 passing
- E2E tests: 15 (local only)
- CI/CD: ✅ Automated on Python 3.10-3.14

---

## 🤝 Contributing

See [GitHub Issues](https://github.com/patrick91/cross-inertia/issues) for available tasks.

### Good First Issues
Look for issues labeled [`good first issue`](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22):
- [Error bags](https://github.com/patrick91/cross-inertia/issues/5)
- [Prefetching support](https://github.com/patrick91/cross-inertia/issues/6)

### High Priority
Check [`high-priority`](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3Ahigh-priority) label for critical features.

---

## 📝 Notes

### Design Philosophy
- **Framework abstraction:** Use [lia](https://github.com/patrick91/lia) for request/response handling
- **Protocol compliance:** Follow [Inertia.js protocol](https://inertiajs.com/the-protocol) specification
- **Developer experience:** Simple, Pythonic API with type hints

### Future Considerations
- SSR support (requires Node.js runtime)
- WebSocket support for live updates
- GraphQL integration patterns

---

**Last Updated:** November 2024  
**Maintained by:** [@patrick91](https://github.com/patrick91)

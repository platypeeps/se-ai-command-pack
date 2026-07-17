# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

This directory documents the actual Python installer and content-pack
conventions. The project has no server API or database; the corresponding
guides state how the CLI handles filesystem state and operational output.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Module organization and file layout | Complete |
| [Database Guidelines](./database-guidelines.md) | Filesystem receipt state; database is not applicable | Complete |
| [Error Handling](./error-handling.md) | CLI failure types and propagation | Complete |
| [Quality Guidelines](./quality-guidelines.md) | Code standards, tests, and lifecycle contracts | Complete |
| [Logging Guidelines](./logging-guidelines.md) | CLI operational output; persistent logging is not used | Complete |

---

Each guide references concrete repository modules and should be updated when a
new pattern becomes established. Keep the guidance descriptive of shipped code,
not aspirational architecture.

---

**Language**: All documentation should be written in **English**.

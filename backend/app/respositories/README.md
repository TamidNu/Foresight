## Purpose
This folder encapsulates all database access using SQLAlchemy.  
Repositories are the only place in the codebase that should interact with the database directly.

## Responsibilities
- Provide CRUD operations and queries for a single aggregate (inventory, prices, etc.).
- Map ORM models into simple objects or DTOs used by services.
- Keep persistence logic consistent and reusable.

## What not to do
- Business rules (guardrails, optimizers, feature calculations).
- API/HTTP concerns.
- Returning open DB cursors or leaking transactions upward.
## Purpose
This folder defines the **data shapes** used across the app.  
It includes both:
- ORM models (SQLAlchemy) mapping to database tables.
- DTOs (Pydantic schemas) for request/response validation and service outputs.

## Responsibilities
- Keep table definitions in `orm.py`.
- Define Pydantic schemas in `dto.py`.
- Provide consistent, typed data structures for controllers, services, and repositories.

## What not to do
- Business logic or service orchestration.
- Direct database queries (belongs in repositories).
- API route definitions (belongs in controllers).
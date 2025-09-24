## Purpose
This folder defines the "shapes" of our data.  
It contains two types of models:
1. **ORM models**: Database tables written with SQLAlchemy.
2. **DTOs (Data Transfer Objects)**: Pydantic schemas for sending/receiving JSON in our API.

## Responsibilities
- Keep database table definitions in `orm.py`.
- Keep Pydantic schemas for API requests/responses in `dto.py`.
- Make sure services and controllers use DTOs when passing data around.

## What NOT to do
- Don’t put pricing rules or business logic here.
- Don’t write SQL or queries here (belongs in repositories).
- Don’t define API routes here (belongs in controllers).

> Models are just blueprints: they describe what the data looks like, not what to do with it.
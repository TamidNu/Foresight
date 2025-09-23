## Purpose
This folder contains all HTTP entrypoints for the backend (FastAPI routers).  
Controllers are responsible only for handling API requests and responses.

## Responsibilities
- Define routes and endpoints.
- Validate incoming request parameters or bodies.
- Call the appropriate Service method.
- Return a DTO or error response.

## What not to do
- Business logic inside controllers (e.g., pricing math, guardrails).
- Direct database queries or ORM calls.
- Calling ML models or other external services directly.
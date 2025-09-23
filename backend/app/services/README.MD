## Purpose
This folder contains the **business logic** of the application.  
Each Service coordinates one complete use case (e.g., computing a room price).

## Responsibilities
- Implement one method per use case (price one room, reprice range, retrain model, etc.).
- Orchestrate multiple repositories and rules.
- Apply guardrails and domain logic consistently.
- Control transaction boundaries (when to commit).
- Return DTOs to controllers.

## What not to do
- Exposing raw ORM entities to controllers.
- Embedding HTTP or routing logic here.
- Mixing persistence logic (belongs in repositories).
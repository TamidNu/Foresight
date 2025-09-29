## Purpose
This folder holds the **real logic** of the app.  
Services describe how the system actually works: they connect the database, rules, and external APIs to complete a use case (like “calculate the price for one room on one night”). This will handle all the manipulating of data within our application.

## Responsibilities
- Handle one clear job per method (e.g., `price_one_room`, `reprice_range`).
- Call repositories to get or save data.
- Call helper functions to compute features, apply guardrails, or run the model.
- Decide when and how data is updated.
- Return a clean result (usually a DTO object) back to the controller.
- Can still interact with DB and external APIs but indirectly via repositories

## What NOT to do
- Don’t write SQL here (leave that to repositories).
- Don’t handle HTTP requests directly (that’s the controller’s job).
- Don’t return raw database objects to the controller (convert them to DTOs first).

> Think of services as the "brains" of the app — they know the steps to take, but they don’t care how the DB is queried or how HTTP works.
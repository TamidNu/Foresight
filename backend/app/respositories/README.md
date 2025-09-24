## Purpose
This folder is the "database layer" of the app.  
Repositories are the only part of the code that should directly talk to the database or external APIs (like Guestline). They provide simple methods that services can use, without services needing to know the details.

## Responsibilities
- Write and read data from the database.
- Wrap external API calls (e.g., Guestline PMS client) into easy-to-use methods.
- Return plain Python objects or Data Transfer Objects (DTOs) that services can work with.

## What NOT to do
- Don’t put business logic here (no pricing rules or calculations).
- Don’t handle HTTP requests from the frontend (controllers do that).
- Don’t return raw ORM objects to controllers.

> Repositories are like waiters: they fetch the data you ask for and bring it back cleanly, but they don’t cook the meal.
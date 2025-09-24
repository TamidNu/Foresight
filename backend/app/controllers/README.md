## Purpose
This folder will hold the REST endpoint of our application. 
Think of controllers as the "front door" of the backend: they decide how outside requests (from the frontend, or from Guestline webhooks) are received and how responses are sent back.

## Responsibilities
- Only handles incoming HTTP requests from frontend or webhookes
- Define routes like `/pricing/price` or `/pricing/reprice`.
- Take query parameters or request bodies from the frontend.
- Hand off the work to a **service** (don’t do the work yourself).
- Send the service’s result back as JSON.

## What NOT to do
- Don't make any outbound API calls
- Don’t write business logic here (e.g., calculating prices or applying rules).
- Don’t talk to the database here.
- Don’t call external APIs (like Guestline) directly from here.

> If you’re writing more than a few lines in a controller, you’re probably putting code in the wrong place.
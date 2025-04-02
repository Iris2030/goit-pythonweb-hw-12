API Documentation
================

FastAPI application entry point.

This module initializes the FastAPI app and includes routes for user authentication, 
profile management, and contact management. It also configures rate limiting for requests.

Functions:
    - rate_limit_handler: Handles rate limit exceeded errors with a custom message.

Authentication Endpoints
-------------------------
**POST** `/auth/register/`  
Register a new user in the system.

**POST** `/auth/login`  
Log a user into the system and return an access token.

**GET** `/auth/confirmed_email/{token}`  
Confirm a user's email address by verifying the token.

**POST** `/auth/verify-email/{token}`  
Verify the user's email using the provided token.

**GET** `/users/me`  
Retrieve the current authenticated user.

**PATCH** `/users/avatar`  
Update the user's avatar.

Contacts Endpoints
-------------------
**POST** `/contacts/`  
Create a new contact.

**GET** `/contacts/`  
Retrieve a list of contacts.

**GET** `/contacts/{contact_id}`  
Retrieve a single contact by its ID.

**PUT** `/contacts/{contact_id}`  
Update an existing contact's details.

**DELETE** `/contacts/{contact_id}`  
Delete a contact by its ID.

**GET** `/contacts/upcoming-birthdays/`  
Retrieve a list of contacts with upcoming birthdays.

Rate Limiting
-------------
The application includes rate limiting using the `slowapi` package. Certain routes have a limit on how many requests can be made within a specific time period, such as 5 requests per minute.

Notes
-----
- All API endpoints expect and return JSON formatted data.
- Authentication is required for most routes, and tokens are passed via the `Authorization` header as a bearer token.


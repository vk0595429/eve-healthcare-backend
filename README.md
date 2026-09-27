# Eve Healthcare - Backend Engineering Assignment

A backend service for diagnostic test bookings and simulated payments, built for the **Eve Healthcare SDE Intern - Backend Engineering Assignment**.

The project focuses on REST API development, PostgreSQL database design, JWT authentication, booking and payment workflows, webhook idempotency, validation, authorization, transactions, and automated testing.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django REST Framework Simple JWT
- python-dotenv

---

## Features

- User signup
- JWT-based authentication
- JWT token refresh
- Diagnostic centre management
- Diagnostic test management
- Centre-specific test pricing
- Authenticated booking creation
- Users can view only their own bookings
- Automatic booking amount calculation
- Booking status management
- Simulated payment processing
- Successful and failed payment handling
- Payment webhook handling
- Idempotent webhook processing
- Authorization checks
- Database transactions for payment processing
- Automated API tests

---

## Project Structure

```text
eve-healthcare-backend/
│
├── accounts/
├── diagnostics/
├── bookings/
├── payments/
├── config/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Application Responsibilities

| App | Responsibility |
|---|---|
| `accounts` | User signup and JWT authentication |
| `diagnostics` | Diagnostic centres, tests, and centre-specific prices |
| `bookings` | Diagnostic test bookings and booking status |
| `payments` | Simulated payments and payment webhooks |
| `config` | Django project configuration |

---

# Database Design

The main relationships are:

```text
User
  │
  └── Booking
        │
        └── CentreTest
              │
              ├── DiagnosticCentre
              │
              └── DiagnosticTest

Booking
  │
  └── Payment
```

## DiagnosticCentre

Stores information about a diagnostic centre.

Fields:

- `id`
- `name`
- `location`

## DiagnosticTest

Stores the diagnostic tests available in the system.

Fields:

- `id`
- `name`

## CentreTest

`CentreTest` connects a diagnostic centre with a diagnostic test and stores the price for that particular centre.

Fields:

- `id`
- `centre`
- `test`
- `price`

A unique constraint is applied to `centre + test`. This prevents the same diagnostic test from being added multiple times to the same centre.

## Booking

A booking represents a patient's appointment for a diagnostic test.

Fields:

- `id`
- `user`
- `centre_test`
- `appointment_datetime`
- `amount`
- `status`
- `created_at`
- `updated_at`

Possible booking statuses:

```text
PENDING
CONFIRMED
FAILED
CANCELLED
```

The booking amount is copied from the selected `CentreTest` when the booking is created.

## Payment

A payment belongs to a booking.

Fields:

- `id`
- `booking`
- `event_id`
- `amount`
- `status`
- `provider_reference`
- `created_at`

Possible payment statuses:

```text
SUCCESS
FAILED
```

The `event_id` field is unique and is used to make payment webhook processing idempotent.

---

# Authentication

The API uses JWT authentication through Django REST Framework Simple JWT.

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

---

# API Endpoints

## Authentication

### Signup

```http
POST /api/auth/signup/
```

Example:

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "StrongPassword123"
}
```

### Login

```http
POST /api/auth/login/
```

Example:

```json
{
    "username": "john",
    "password": "StrongPassword123"
}
```

### Refresh Token

```http
POST /api/auth/token/refresh/
```

---

# Diagnostic Centres

### List Centres

```http
GET /api/diagnostics/centres/
```

### Create Centre

```http
POST /api/diagnostics/centres/
```

Example:

```json
{
    "name": "City Diagnostics",
    "location": "Chandigarh"
}
```

---

# Diagnostic Tests

### List Tests

```http
GET /api/diagnostics/tests/
```

### Create Test

```http
POST /api/diagnostics/tests/
```

Example:

```json
{
    "name": "Complete Blood Count"
}
```

---

# Centre Tests

### List Centre Tests

```http
GET /api/diagnostics/centre-tests/
```

### Create Centre Test

```http
POST /api/diagnostics/centre-tests/
```

Example:

```json
{
    "centre": 1,
    "test": 1,
    "price": "500.00"
}
```

---

# Bookings

### List User Bookings

```http
GET /api/bookings/
```

The API returns bookings belonging to the authenticated user.

### Create Booking

```http
POST /api/bookings/
```

Example:

```json
{
    "centre_test": 1,
    "appointment_datetime": "2026-09-28T10:30:00Z"
}
```

The authenticated user is automatically assigned to the booking.

The booking amount is calculated from the selected centre-test price.

A newly created booking starts with `PENDING`.

---

# Payments

### Create Simulated Payment

```http
POST /api/payments/
```

Example successful payment:

```json
{
    "booking": 1,
    "simulate_success": true
}
```

Example failed payment:

```json
{
    "booking": 1,
    "simulate_success": false
}
```

Successful payment:

```text
Payment = SUCCESS
Booking = CONFIRMED
```

Failed payment:

```text
Payment = FAILED
Booking = FAILED
```

Payment creation and booking status updates are performed inside a database transaction.

---

# Payment Webhook

### Webhook Endpoint

```http
POST /api/payments/webhook/
```

Example:

```json
{
    "event_id": "payment-event-001",
    "booking": 1,
    "status": "SUCCESS"
}
```

The webhook uses `event_id` as an idempotency key.

If the same webhook event is received again, the existing payment is returned instead of creating another payment record.

---

# Booking and Payment Flow

```text
User Signup
     │
     ▼
JWT Login
     │
     ▼
View Diagnostic Centres / Tests
     │
     ▼
Create Booking
     │
     ▼
Booking = PENDING
     │
     ▼
Simulated Payment
     │
     ├───────────────┐
     │               │
   SUCCESS         FAILED
     │               │
     ▼               ▼
CONFIRMED          FAILED
```

---

# Validation and Authorization

The backend handles:

- Invalid request validation
- JWT authentication
- User booking isolation
- Unauthorized payment attempts
- Already processed bookings
- Duplicate webhook events
- Invalid booking references

---

# Local Setup

## Prerequisites

- Python 3.12+
- PostgreSQL
- Git

Make sure PostgreSQL is running.

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd eve-healthcare-backend
```

## 2. Create Virtual Environment

Windows Git Bash:

```bash
python -m venv env
source env/scripts/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create PostgreSQL Database

Create a database named:

```text
eve_healthcare
```

Example:

```sql
CREATE DATABASE eve_healthcare;
```

## 5. Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Update `.env` with your local PostgreSQL credentials and Django secret key.

Example:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=eve_healthcare
DB_USER=postgres
DB_PASSWORD=your-postgresql-password
DB_HOST=localhost
DB_PORT=5432
```

Do not commit `.env` to Git.

## 6. Apply Migrations

```bash
python manage.py migrate
```

## 7. Run Tests

```bash
python manage.py test
```

Expected result:

```text
Found 10 test(s).

..........
----------------------------------------------------------------------
Ran 10 tests

OK
```

## 8. Start Development Server

```bash
python manage.py runserver
```

API:

```text
http://127.0.0.1:8000/
```

---

# Testing

Automated tests cover:

### Accounts

- User signup
- JWT login

### Bookings

- Booking creation
- User booking isolation

### Payments

- Successful payment
- Failed payment
- Unauthorized payment attempt
- Already processed booking
- Webhook idempotency
- Unauthorized webhook access

Run all tests:

```bash
python manage.py test
```

---

# Environment and Security

Sensitive configuration is loaded through environment variables.

`.env` is excluded from Git.

`.env.example` contains only placeholder values.

The repository does not contain the local database password or Django secret key.

---

# Design Decisions

## Why PostgreSQL?

PostgreSQL provides a relational database suitable for the booking and payment relationships and is the preferred database for the assignment.

## Why CentreTest?

The same diagnostic test may have different prices at different centres.

Therefore, the price belongs to the centre-test relationship rather than directly to the test.

## Why Store Booking Amount?

The booking stores its own amount so that historical bookings retain their original price even if the centre-test price changes later.

## Why Unique Event ID?

Payment providers may deliver the same webhook more than once.

A unique `event_id` prevents duplicate payment records.

## Why Database Transactions?

Payment creation and booking status updates are related operations and are performed inside a database transaction.

---

# Important Assumptions

- Payments are simulated; no real payment gateway is integrated.
- PostgreSQL is used as the application database.
- JWT authentication is used for protected API endpoints.
- The webhook endpoint uses JWT authentication for this assignment.
- A production payment integration would normally use provider webhook signature verification.
- Booking amount is stored separately to preserve the historical booking amount.
- A payment can only be processed for the authenticated user's pending booking.
- A booking cannot be processed again after payment has been completed.
- Webhook `event_id` values are unique.
- The project is designed to run locally from the GitHub repository.

---

# Future Improvements

- Real payment gateway integration
- Payment-provider webhook signature verification
- Swagger/OpenAPI documentation
- Pagination
- Rate limiting
- Structured logging
- Background processing
- Docker-based deployment
- More extensive integration tests
- Retry handling for external payment-provider communication
- Booking cancellation workflow

---

# Assignment Submission

This repository contains:

- Source code
- Database migrations
- Automated tests
- `requirements.txt`
- `.env.example`
- `.gitignore`
- Project documentation

The project is intended to be run locally using PostgreSQL and Django.

---

## Author

**Vishal Kumar Chaurasia**

B.Tech - Computer Science & Engineering

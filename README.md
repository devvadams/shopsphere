# ShopSphere — E-Commerce REST API

**ShopSphere** is a backend e-commerce project built with Django REST Framework and PostgreSQL. It provides the core API functionality needed for an online shopping platform, including product browsing, customer authentication, shopping carts, and order processing.

The project is being developed with a focus on clean API design, secure data access, reliable order processing, and a foundation that can later support a React frontend.

> **Project status:** Backend development is underway. The core API features and automated tests have been implemented. A React frontend and cloud deployment are planned next steps.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Order Processing](#order-processing)
- [Testing](#testing)
- [Frontend Roadmap](#frontend-roadmap)
- [Deployment Roadmap](#deployment-roadmap)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

## Overview

ShopSphere is designed to provide the server-side foundation of an online store.

In a typical e-commerce application, the frontend presents products to customers and provides the interface for shopping. The backend manages the business logic, validates requests, stores information, enforces access permissions, and processes orders.

ShopSphere currently focuses on that backend responsibility.

The API allows clients to interact with products, register and authenticate users, manage shopping carts, and place orders. It uses PostgreSQL for persistent data storage and Django REST Framework to expose functionality through HTTP endpoints.

The planned React frontend will consume these endpoints to provide a complete shopping experience.

## Features

### 1. Product Catalog

The product API provides endpoints for retrieving product and category information.

Implemented capabilities include:

- Browsing product listings.
- Retrieving individual products using their slugs.
- Accessing product categories.
- Filtering and paginating API results where supported by the configured API framework.

### 2. User Authentication

ShopSphere uses JSON Web Tokens (JWT) for API authentication.

Authentication functionality includes:

- User registration.
- Obtaining access and refresh tokens.
- Refreshing access tokens.
- Retrieving the authenticated user's profile.
- Restricting protected resources to authorized users.

### 3. Shopping Cart

Authenticated customers can manage their shopping carts through the API.

Cart functionality includes:

- Retrieving the customer's cart.
- Adding products to the cart.
- Updating item quantities.
- Removing cart items.
- Validating requested quantities against available stock.
- Preventing users from modifying another user's cart.

### 4. Order Management

ShopSphere includes checkout and order-history functionality.

Implemented capabilities include:

- Creating orders through checkout.
- Validating cart contents and product availability.
- Preventing checkout when stock is insufficient.
- Deducting inventory after a successful checkout.
- Recording product names and prices at the time of purchase.
- Clearing the cart after successful checkout.
- Retrieving order history.
- Restricting order access to the customer who owns the order.

### 5. API Documentation

The project uses `drf-spectacular` to generate API documentation.

The Swagger UI provides an interactive interface for exploring endpoints and trying API requests.

### 6. Automated Testing

Automated tests cover important product, cart, and order behaviours, including access control and checkout validation.

The current test suite contains 20 passing tests.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Primary programming language |
| Django | Backend web framework |
| Django REST Framework | REST API development |
| PostgreSQL | Relational database |
| Psycopg 3 | PostgreSQL database adapter |
| Simple JWT | Token-based authentication |
| django-filter | API filtering support |
| drf-spectacular | OpenAPI schema and Swagger documentation |
| django-cors-headers | Cross-origin request configuration |
| WhiteNoise | Static file serving |
| Gunicorn | Production WSGI application server |
| pytest and pytest-django | Automated testing |
| Git and GitHub | Version control and source code hosting |

## Architecture

ShopSphere follows a modular Django architecture.

Each application is responsible for a particular area of the e-commerce domain:

- **Products:** Product catalog and category functionality.
- **Accounts:** User registration, authentication, and profile functionality.
- **Cart:** Shopping cart operations and cart-item validation.
- **Orders:** Checkout, inventory updates, order creation, and order history.
- **Config:** Project settings, URL routing, and WSGI/ASGI entry points.

PostgreSQL stores the application's persistent data. Django models represent database entities, serializers validate and transform API data, and views handle incoming requests.

The React frontend will eventually communicate with the backend through HTTP requests, using JSON for most API interactions and JWT authentication for protected operations.

## Project Structure

```text
shopsphere/
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── cart/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── orders/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── products/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .gitignore
├── manage.py
└── requirements.txt
```

The `.env` file and Python virtual environment are intentionally excluded from version control.

## Requirements

Before running ShopSphere locally, install or prepare the following:

- Python compatible with the installed Django version.
- PostgreSQL.
- Git.
- A terminal such as PowerShell, Command Prompt, or Bash.
- An API client such as Swagger UI or Postman for testing endpoints.

The commands below use Windows PowerShell.

## Getting Started

### 1. Clone the repository

```powershell
git clone https://github.com/devvadams/shopsphere.git
cd shopsphere
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, adjust the execution policy for the current terminal session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment again.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

Start your local PostgreSQL server and create a database and database user for ShopSphere.

For example, using the PostgreSQL command-line tool, an administrator can run:

```sql
CREATE USER shopsphere_user WITH PASSWORD 'choose-a-strong-local-password';
CREATE DATABASE shopsphere_db OWNER shopsphere_user;
```

Use your own strong password locally. Do not commit database passwords to GitHub.

If the database and user already exist, you can use those existing credentials instead.

### 5. Configure environment variables

Create a `.env` file in the project root, alongside `manage.py`.

Add the following configuration and replace the example values with your local settings:

```dotenv
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=shopsphere_db
DB_USER=shopsphere_user
DB_PASSWORD=replace-with-your-local-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

The settings module reads these variables from the environment.

**Never upload your real `.env` file to GitHub.** Keep it excluded through `.gitignore`.

### 6. Apply database migrations

```powershell
python manage.py migrate
```

### 7. Create an administrator account (optional)

To access Django's administrative interface:

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

### 8. Start the development server

```powershell
python manage.py runserver
```

The API will normally be available at:

```text
http://127.0.0.1:8000/
```

## API Documentation

Once the development server is running, open:

**Swagger UI:** `http://127.0.0.1:8000/api/docs/`

Use Swagger to inspect available endpoints, review request and response schemas, and test API operations.

For endpoints requiring authentication, obtain a JWT access token and use the authorization control in Swagger when available.

## API Endpoints

The following table summarises the current API route structure.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/categories/` | List product categories |
| GET | `/api/products/` | List products |
| GET | `/api/products/<slug>/` | Retrieve a product by slug |
| POST | `/api/auth/register/` | Register a user |
| POST | `/api/auth/token/` | Obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh an access token |
| GET | `/api/auth/me/` | Retrieve the authenticated user's profile |
| GET | `/api/cart/` | Retrieve the current user's cart |
| POST | `/api/cart/items/` | Add a product to the cart |
| PATCH | `/api/cart/items/<id>/` | Update a cart item's quantity |
| DELETE | `/api/cart/items/<id>/` | Remove a cart item |
| POST | `/api/orders/checkout/` | Create an order from the cart |
| GET | `/api/orders/` | Retrieve the current user's orders |
| GET | `/api/orders/<id>/` | Retrieve an individual order |

The API documentation is the authoritative source for request fields, validation rules, response formats, and any additional supported methods.

## Authentication

ShopSphere uses JSON Web Tokens.

A typical authentication workflow is:

1. Register an account through `/api/auth/register/`.
2. Submit login credentials to `/api/auth/token/`.
3. Receive an access token and refresh token.
4. Include the access token when calling protected endpoints.
5. Request a new access token through `/api/auth/token/refresh/` when necessary.

For protected API requests, the standard header format is:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The configured access-token lifetime is 30 minutes, while the refresh-token lifetime is one day.

Do not share tokens publicly or commit them to version control.

## Order Processing

Checkout is one of the most important business operations in ShopSphere.

The checkout process is designed to:

1. Retrieve the authenticated customer's cart.
2. Validate that the cart contains items.
3. Check product availability and requested quantities.
4. Prevent checkout if stock is insufficient.
5. Create order records using the product information and prices at purchase time.
6. Deduct the purchased quantities from inventory.
7. Clear the cart after successful checkout.

The checkout operation uses a database transaction so that related database changes can be rolled back if the operation fails.

Product and order data are protected by ownership and permission checks where applicable.

This establishes a foundation for future features such as payment integration, order-status tracking, delivery management, and customer notifications. Those additional features should not be considered implemented until they are developed and tested.

## Testing

ShopSphere includes automated tests for core backend functionality.

To run the complete test suite:

```powershell
python manage.py test
```

To run Django's system checks:

```powershell
python manage.py check
```

The current test suite has 20 passing tests covering product, cart, and order functionality, including important validation and authorization scenarios.

Run the tests again after making changes to the application.

## Frontend Roadmap

The next major development stage is a React frontend that consumes the ShopSphere API.

The intended frontend will provide a user-friendly shopping experience while keeping business logic and persistent data management in the Django backend.

Planned frontend capabilities include:

- A home page with featured products and categories.
- Product listings and product-detail pages.
- Product search and filtering.
- User registration and login.
- JWT-aware authentication handling.
- Shopping cart management.
- Checkout and order confirmation.
- Customer order history.
- Responsive layouts for desktop and mobile devices.

The frontend will be developed as a separate application and connected to the backend through its REST API.

Potential frontend technologies include React, Vite, JavaScript or TypeScript, and a suitable styling solution.

These are roadmap items, not claims that the frontend already exists.

## Deployment Roadmap

The planned deployment architecture separates the frontend, backend, and database.

- **Backend:** Django REST API hosted on Render.
- **Database:** PostgreSQL hosted on Render.
- **Frontend:** React application hosted separately.
- **Source control:** GitHub.

Before production deployment, the project must be configured to use production environment variables and a production database connection.

The production configuration should also include appropriate allowed hosts, frontend CORS origins, secure settings, and a deployment process that applies database migrations safely.

The local `.env` file must never be used as a substitute for configuring production environment variables in the hosting provider.

## Security Notes

ShopSphere is under active development. Before using it for real customers or production transactions, review and strengthen the following areas as appropriate:

- Keep secret keys, database passwords, and tokens out of source control.
- Use HTTPS in production.
- Configure allowed hosts and CORS origins explicitly.
- Review authentication, authorization, and object-level permissions.
- Validate all incoming data on the backend.
- Add rate limiting and abuse protection where appropriate.
- Review inventory concurrency and transaction behaviour under simultaneous checkout requests.
- Integrate a payment provider securely before accepting real payments.
- Configure backups, monitoring, logging, and error reporting.
- Test production configuration before exposing the API publicly.

A successful development test suite is a useful milestone, but it does not by itself guarantee production readiness.

## Contributing

Contributions, suggestions, and constructive feedback are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the relevant tests.
5. Submit a pull request describing the changes.

For substantial changes, open an issue or discuss the proposed feature before implementation.

## License

No license has been specified yet.

Until a license is added to the repository, do not assume that the project is available for unrestricted reuse, redistribution, or modification.
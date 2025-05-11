# Subscription-Billing-System


Overview
The Subscription Billing System allows users to register, log in, choose a subscription plan, and manage their billing cycle. It includes an automated process to activate subscriptions after 7 days, provided the invoice is paid. The system uses Django for the backend, Celery for task management, and SQLite for data storage.

This project comes with a frontend UI that includes a landing page for registration, a login page, and a home page displaying available subscription plans. It also features a task scheduler to manage subscription activations.


Features:
# User Registration and Login
* Users can register and log in to the platform.

# Subscription Plans
* Users can choose from 3 different subscription plans.

# Subscription Activation
* Subscriptions are activated after 7 days, provided the invoice is paid.

# Celery Background Tasks
* Periodic tasks run every minute, checking for subscription activations based on invoice status.

Project Structure:

subscription_billing_system/
│
├── manage.py                     # Django management script
├── subscription_billing_system/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py                 # Celery configuration
│   ├── settings.py               # Project settings
│   ├── urls.py                   # URL routing
│   ├── wsgi.py
│
├── billing/                       # Billing-related app
│   ├── __init__.py
│   ├── migrations
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Subscription and billing models
│   ├── tasks.py                  # Celery tasks for subscription activations
│   ├── tests.py                   
│   ├── urls.py
│   ├── views.py
│
├── users/                         # User-related app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # User registration and login models
│   ├── serializers.py            # User serializers for API
│   ├── urls.py
│   ├── views.py
│
├── templates/                     # Folder containing HTML templates
│   └── users/
│       ├── home.html
│       ├── login.html
│       └── register.html
│
├── db.sqlite3                     # SQLite database
├── celerybeat.pid                 # Celery beat schedule
├── req.txt                        # Project dependencies
└── README.md                      # Project documentation



### Installation
* Prerequisites
* * Ensure the following are installed:
* * * Python 3.8 or higher
* * * Django 3.x or higher
* * * Celery


### Clone the Repository:

# Clone the repo to your local machine:
* * git clone <repo_url> subscription_billing_system
* * cd subscription_billing_system

# Create and activate a virtual environment:
* * python3 -m venv myenv
* * source myenv/bin/activate  # macOS/Linux
* * myenv\Scripts\activate  

# Install the required dependencies from req.txt:
* * pip install -r req.txt

# Make migrations and apply them to set up the database:
* * python manage.py makemigrations
* * python manage.py migrate


# Run the Django development server:
* * python manage.py runserver
The API will be available at http://127.0.0.1:8000/

## Running Celery:
* In one terminal, start the Celery beat scheduler:
* * celery -A subscription_billing_system beat --loglevel=info

* In another terminal, start the Celery worker:
* * celery -A subscription_billing_system worker --loglevel=info



## Error Handling and Logging
* * I have implemented improved error handling with detailed logging to track issues. In case of a failure for a single user, it will not affect the operation of other users, ensuring system stability.

## Celery Tasks
* * generate_invoices_for_subscriptions
This task generates invoices for subscriptions that are "inactive" and have a requested date matching the current day. It ensures that no duplicate invoices are created by checking for existing pending invoices. If no invoice exists, a new one is created. The due date for the invoice is set to 3 days before the subscription's start date.

Frequency: Runs every minute (minute='*', hour='*').

Logic:

Filters subscriptions with the status "inactive" and a requested date of today.

Checks if a pending invoice already exists for each subscription.

If no pending invoice is found, a new invoice is generated with:

Issue Date: 7 days before the subscription start date.

Due Date: 3 days before the subscription start date.

Status: "pending".

Logging: Logs information if an invoice already exists for a subscription or when new invoices are created.


* * mark_overdue_invoices
This task identifies overdue invoices (where the due date is in the past and the status is "pending") and updates their status to "overdue." This helps in keeping track of unpaid invoices.

Frequency: Runs every minute (minute='*', hour='*').(Note - for testing purpose)

Logging: Logs the number of overdue invoices found and successfully updated.


* * send_invoice_reminder
This task sends reminders for unpaid invoices, notifying users about invoices that are due or overdue. If an error occurs while processing an individual user's invoice, it will not affect the processing of other invoices.

Frequency: Runs every minute (minute='*', hour='*').(Note - for testing purpose)

Logging: Logs errors for any failed reminder attempts and successfully sent reminders for each user.


* * cancel_overdue_subscriptions
This task checks for subscriptions whose invoice status is "overdue" and whose subscription start date is today. If such invoices are found, the associated subscriptions are automatically canceled. This ensures that overdue subscriptions are effectively managed and inactive users are no longer billed.

Frequency: Runs periodically based on a specified schedule.

Logic:

Filters invoices with the status "overdue" and a due date before the current date.

Checks if the related subscription has a start date of today.

If both conditions are met, the subscription is marked as "cancelled" to stop further billing or service.

Logging: Logs the cancellation of subscriptions and updates the status of overdue invoices.



* * mark_subscriptions_as_expired
This task runs periodically to check for subscriptions that have reached their end date. If a subscription’s end_date is the previous day (indicating the plan should be valid until the last day), and the subscription is still marked as "active," it will be marked as "expired." This ensures that subscriptions are automatically expired after their valid period has ended.

Frequency: Runs periodically based on a specified schedule.

Logic:

Filters subscriptions with the status "active" and an end_date equal to the previous day (ensuring the user’s plan was valid through the last day).

For each subscription that meets the criteria, it updates the status to "expired."

Logging: Logs when a subscription is marked as expired or when subscriptions are processed for expiration.

This task helps manage subscription lifecycles by automatically expiring subscriptions that have completed their term, reducing manual tracking overhead.
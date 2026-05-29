# Bus CMS — Django + PostgreSQL Setup Guide

## Django App → Database Table Mapping

| App              | Tables                                                                                 |
|------------------|----------------------------------------------------------------------------------------|
| `accounts`       | roles, permissions, role_permissions, user_accounts, user_roles, audit_logs           |
| `branches`       | branches                                                                               |
| `routes`         | provinces, stations, routes, route_stops                                               |
| `vehicles`       | vehicle_categories, vehicles, seat_maps, seats, vehicle_maintenance                   |
| `hr`             | departments, employees, shift_types, attendances, payroll                              |
| `trips`          | trip_schedules, trips, trip_staff, trip_prices, dispatch_orders                        |
| `tickets`        | customers, ticket_bookings, tickets, ticket_refunds, ticket_exchanges, group_contracts |
| `payments`       | payment_methods, payments, cashier_sessions, invoices                                  |
| `consignments`   | cargo_price_tables, consignments, consignment_manifests, manifest_items, cod_reconciliations |
| `promotions`     | promotions, promotion_usages, after_sales                                              |
| `notifications`  | notification_templates, notifications                                                  |
| `financials`     | expense_categories, expenses, fuel_allocations                                         |
| `assets`         | asset_categories, assets, storage_units                                                |

---

## 1. Project Setup

```bash
# Create project
django-admin startproject config .

# Create all apps
python manage.py startapp accounts apps/accounts
python manage.py startapp branches apps/branches
python manage.py startapp routes   apps/routes
python manage.py startapp vehicles apps/vehicles
python manage.py startapp hr       apps/hr
python manage.py startapp trips    apps/trips
python manage.py startapp tickets  apps/tickets
python manage.py startapp payments apps/payments
python manage.py startapp consignments apps/consignments
python manage.py startapp promotions   apps/promotions
python manage.py startapp notifications apps/notifications
python manage.py startapp financials    apps/financials
python manage.py startapp assets        apps/assets
```

---

## 2. INSTALLED_APPS (config/settings.py)

```python
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    # Project apps — order matters for FK dependencies
    "apps.accounts",
    "apps.branches",
    "apps.routes",
    "apps.vehicles",
    "apps.hr",
    "apps.trips",
    "apps.tickets",
    "apps.payments",
    "apps.consignments",
    "apps.promotions",
    "apps.notifications",
    "apps.financials",
    "apps.assets",
]
```

---

## 3. Database Config (config/settings.py)

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "bus_cms"),
        "USER": os.environ.get("DB_USER", "bus_cms_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c default_transaction_isolation=read committed",
        },
    }
}
```

---

## 4. Migration Files Deployment Order

Copy each migration file into the correct app's `migrations/` folder and rename it:

```
accounts_0001_initial.py    → apps/accounts/migrations/0001_initial.py
branches_0001_initial.py    → apps/branches/migrations/0001_initial.py
routes_0001_initial.py      → apps/routes/migrations/0001_initial.py
vehicles_0001_initial.py    → apps/vehicles/migrations/0001_initial.py
hr_0001_initial.py          → apps/hr/migrations/0001_initial.py
trips_0001_initial.py       → apps/trips/migrations/0001_initial.py
tickets_0001_initial.py     → apps/tickets/migrations/0001_initial.py
payments_0001_initial.py    → apps/payments/migrations/0001_initial.py
consignments_0001_initial.py → apps/consignments/migrations/0001_initial.py
promotions_0001_initial.py  → apps/promotions/migrations/0001_initial.py
notifications_0001_initial.py → apps/notifications/migrations/0001_initial.py
financials_0001_initial.py  → apps/financials/migrations/0001_initial.py
assets_0001_initial.py      → apps/assets/migrations/0001_initial.py
```

Each `migrations/` folder needs an `__init__.py` file.

---

## 5. Apply Migrations

```bash
# Option A: Use Django migrations (recommended for ongoing development)
python manage.py migrate

# Option B: Apply raw SQL directly to PostgreSQL (initial setup only)
psql -U bus_cms_user -d bus_cms -f sql/001_schema.sql
```

---

## 6. Cross-App FK Dependency Notes

Two circular/deferred FKs are resolved in later migrations:

| Field                         | Defined in         | Resolved in          |
|-------------------------------|--------------------|----------------------|
| `user_accounts.branch_id`     | accounts migration | branches migration   |
| `payments.consignment_id`     | payments migration | consignments migration |

---

## 7. Recommended pip packages

```
django>=4.2
psycopg2-binary>=2.9
djangorestframework>=3.15
django-filter>=23.0
celery>=5.3          # async notifications, background tasks
redis>=5.0           # celery broker + cache
django-storages      # S3/GCS for file uploads (avatars, attachments)
```
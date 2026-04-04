# Smart Warehouse & Production Control System

A full-featured web platform for warehouse inventory management and production process monitoring built with **Django 5**, **Bootstrap 5**, and **Chart.js**.

---

## Features

- **Role-based access control** — Admin, Warehouse Manager, Production Manager, Worker
- **Product & inventory management** — stock tracking, categories, warehouse locations
- **Stock transactions** — IN / OUT / TRANSFER / ADJUSTMENT / PRODUCTION
- **Raw materials & Bill of Materials (BOM)** — per-product material recipes
- **Production orders** — 5-stage workflow with automatic material deduction
- **Dashboard** — KPI cards and live Chart.js charts (stock movement, production status, top materials)
- **Notifications** — low stock alerts, insufficient materials, production completion
- **Reports & exports** — Inventory and Production reports in CSV and Excel

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.11+, Django 5            |
| Database   | SQLite (dev) / PostgreSQL (prod)  |
| Frontend   | Django Templates, Bootstrap 5     |
| Charts     | Chart.js 4                        |
| Icons      | Bootstrap Icons                   |
| Excel      | openpyxl                          |

---

## Project Structure

```
smart_warehouse/          ← Django project config (settings, urls)
accounts/                 ← Authentication, roles, user management
inventory/                ← Products, raw materials, BOM, transactions, locations
production/               ← Production orders and 5-stage workflow
dashboard/                ← KPI dashboard, notifications, context processors
reports/                  ← CSV/Excel report exports
templates/                ← All HTML templates
static/
  css/custom.css          ← Custom styles
  js/main.js              ← Sidebar toggle, auto-dismiss alerts, helpers
fixtures/
  initial_data.json       ← Sample categories, locations, products, BOM
setup.py                  ← One-command setup script
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip
- (Optional) PostgreSQL if not using SQLite

---

### Step 1 — Clone or download the project

```bash
git clone <repo-url>
cd Husniddin
```

---

### Step 2 — Create and activate a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Configure environment variables

```bash
# Copy the example env file
cp .env.example .env
```

Open `.env` and adjust values if needed.
For local development with SQLite the defaults work out of the box.

> **PostgreSQL users:** uncomment the `DB_*` lines in `.env` and update `smart_warehouse/settings.py` to read them.

---

### Step 5 — Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 6 — Load sample data and create default users

```bash
python setup.py
```

This single command:
1. Applies any pending migrations
2. Loads `fixtures/initial_data.json` (sample categories, locations, products, raw materials, BOM)
3. Creates four default user accounts

---

### Step 7 — Start the development server

```bash
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**

---

## Default Accounts

| Username   | Password       | Role                |
|------------|----------------|---------------------|
| `admin`    | `admin123`     | Admin               |
| `wmanager` | `warehouse123` | Warehouse Manager   |
| `pmanager` | `prod123`      | Production Manager  |
| `worker1`  | `worker123`    | Worker              |

> Change these passwords before deploying to production.

---

## Usage Guide

### Warehouse Workflow

1. **Add locations** → Inventory → Locations
2. **Add categories** → Inventory → Categories (Admin sidebar)
3. **Add products** → Inventory → Products → Add Product
4. **Add raw materials** → Inventory → Raw Materials → Add Raw Material
5. **Define BOM** → Inventory → Bill of Materials → Add BOM Entry (specify how much raw material each product needs)
6. **Record stock movements** → Inventory → Stock Transactions → New Transaction

### Production Workflow

1. **Create production order** → Production → New Order (select product + quantity)
2. **Check material availability** — shown on order detail page (green ✓ / red ✗)
3. **Start production** → click **Start Production**
   - System automatically deducts raw materials from inventory based on BOM
   - First stage (Preparation) activates automatically
4. **Update stages** — workers click **Update** on each stage and set status to `In Progress` → `Completed`
   - Next stage activates automatically when current one is completed
5. **Order completes** when all 5 stages finish — finished goods are added to product stock

### Production Stages (in order)

| # | Stage         | Description                        |
|---|---------------|------------------------------------|
| 1 | Preparation   | Setup, material gathering          |
| 2 | Manufacturing | Core production process            |
| 3 | Quality Check | Inspection and testing             |
| 4 | Packaging     | Packing finished goods             |
| 5 | Finished      | Ready for dispatch / stock         |

### Reports & Exports

- Go to **Reports** in the sidebar
- Choose **Inventory Report** or **Production Report**
- Filter by time period (7 / 30 / 90 / 365 days)
- Export to **CSV** or **color-coded Excel**

---

## Switching to PostgreSQL

1. Install the PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Create a database:
   ```sql
   CREATE DATABASE smart_warehouse;
   ```

3. Update `.env`:
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=smart_warehouse
   DB_USER=postgres
   DB_PASSWORD=yourpassword
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. Uncomment the PostgreSQL `DATABASES` block in `smart_warehouse/settings.py` and comment out the SQLite block.

5. Re-run migrations:
   ```bash
   python manage.py migrate
   python setup.py
   ```

---

## Creating a Superuser Manually

```bash
python manage.py createsuperuser
```

Access the Django admin panel at **http://127.0.0.1:8000/admin/**

---

## Collecting Static Files (Production)

```bash
python manage.py collectstatic
```

---

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Load fixtures manually
python manage.py loaddata fixtures/initial_data.json

# Collect static files
python manage.py collectstatic
```

---

## Security Notes for Production

- Set `DEBUG=False` in `.env`
- Set a strong random `SECRET_KEY`
- Set `ALLOWED_HOSTS` to your actual domain
- Use PostgreSQL instead of SQLite
- Serve static/media files via Nginx or a CDN
- Use HTTPS (SSL/TLS certificate)
- Change all default user passwords

---

## License

MIT License — free to use and modify.

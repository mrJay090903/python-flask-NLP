# 🎓 Flask XAMPP Setup Guide

Complete guide for setting up the Flask application with XAMPP (MySQL) and implementing authentication, role-based access control, and advanced features.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [XAMPP Installation & Setup](#xampp-installation--setup)
3. [Database Configuration](#database-configuration)
4. [Application Setup](#application-setup)
5. [Running the Application](#running-the-application)
6. [Demo Credentials](#demo-credentials)
7. [Features Overview](#features-overview)
8. [Troubleshooting](#troubleshooting)
9. [API Documentation](#api-documentation)

---

## Prerequisites

- **Python 3.8+** installed on your system
- **XAMPP** with Apache and MySQL enabled
- **pip** (Python package manager)
- **Git** (optional, for version control)

### Install XAMPP

1. Download XAMPP from https://www.apachefriends.org/
2. Install XAMPP in your preferred directory
3. Start XAMPP Control Panel and enable **MySQL** module

---

## XAMPP Installation & Setup

### Step 1: Start XAMPP Services

1. Open **XAMPP Control Panel**
2. Click **Start** next to **MySQL** module
3. Verify MySQL is running (should show "Running" in green)

### Step 2: Access MySQL Command Line

```bash
# Navigate to XAMPP installation directory
cd /path/to/xampp/mysql/bin

# Or use the XAMPP shell in the Control Panel
# Click "Shell" button to open terminal
```

### Step 3: Login to MySQL

```bash
mysql -u root -p
# Press Enter when prompted for password (default is empty)
```

---

## Database Configuration

### Step 1: Create Database

```sql
CREATE DATABASE py_data_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Create Database User (Optional but Recommended)

```sql
CREATE USER 'flask_user'@'localhost' IDENTIFIED BY 'flask_password123';
GRANT ALL PRIVILEGES ON py_data_app.* TO 'flask_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Run Seed Script

```bash
# Method 1: Using MySQL command line
mysql -u root -p py_data_app < seed_full.sql

# Method 2: Using XAMPP UI
# 1. Open phpMyAdmin: http://localhost/phpmyadmin
# 2. Select 'py_data_app' database
# 3. Click "Import" tab
# 4. Select seed_full.sql and click "Go"
```

### Step 4: Verify Database Setup

```bash
mysql -u root -p py_data_app -e "SHOW TABLES;"
```

Expected output:
```
+------------------------+
| Tables_in_py_data_app  |
+------------------------+
| nav_items              |
| records                |
| roles                  |
| users                  |
+------------------------+
```

---

## Application Setup

### Step 1: Clone/Download Application Files

```bash
cd /path/to/workspace
git clone <your-repo-url>
# or manually download all files
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create .env Configuration File

Create a `.env` file in the application root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=py_data_app

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
```

Or use the included template:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Verify Dependencies

Check `requirements.txt` contains:

```
Flask==3.1.2
Flask-SQLAlchemy==3.0.3
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
email-validator==2.1.0
PyMySQL==1.0.3
pandas==2.2.2
plotly==5.15.0
matplotlib==3.8.1
Werkzeug==3.0.1
python-dotenv==1.0.0
```

---

## Running the Application

### Step 1: Initialize Database (First Run Only)

```bash
# Start Python shell
python

# Run these commands:
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized!")
    
# Exit with: exit()
```

### Step 2: Start Flask Development Server

```bash
# Make sure virtual environment is activated
# Windows:
set FLASK_APP=app.py
set FLASK_ENV=development
python app.py

# macOS/Linux:
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py
```

### Step 3: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

---

## Demo Credentials

### Default Admin Account

After running `seed_full.sql`, use these credentials to log in:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |
| **Role** | Admin |

### Additional Demo Accounts (from seed)

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | admin123 | Admin | Full system access |
| president | pres123 | President | Record management, reports |
| cashier | cash123 | Cashier | Record entry, viewing |
| viewer | view123 | Viewer | Read-only access |

### Create New Accounts

1. Navigate to `http://localhost:5000/register`
2. Fill in the registration form
3. New users default to **Viewer** role
4. Admin can change roles in Admin Panel

---

## Features Overview

### 🔐 Authentication System

- **Login/Logout**: Secure session management with Flask-Login
- **Registration**: New user account creation with email validation
- **Password Security**: Werkzeug password hashing with salt

**Routes:**
- `GET /login` - Login form
- `POST /login` - Process login
- `GET /logout` - Logout user
- `GET /register` - Registration form
- `POST /register` - Create new account

### 👥 Role-Based Access Control (RBAC)

Four predefined roles with specific permissions:

| Role | Permissions |
|------|------------|
| **Admin** | User management, navigation config, full system access |
| **President** | Record management, reports, analytics |
| **Cashier** | Create/edit records, CSV upload |
| **Viewer** | Read-only access to records and reports |

### 📊 Records Management

- **List Records**: Paginated table with category filtering
- **Create Record**: Form-based entry with date/time picker
- **Edit Record**: Modify existing records (creator only)
- **Delete Record**: Remove records (Admin/Creator only)
- **CSV Upload**: Bulk import records from CSV file

**Routes:**
- `GET /records` - List all records
- `GET /records/new` - Create record form
- `POST /records/new` - Save new record
- `GET /records/<id>/edit` - Edit form
- `POST /records/<id>/edit` - Update record
- `POST /records/<id>/delete` - Delete record
- `POST /records/upload` - Upload CSV

### 👤 User Management (Admin Only)

- **List Users**: View all registered users with roles
- **Create User**: Add new user account
- **Edit User**: Modify user details and role
- **Delete User**: Remove user account

**Routes:**
- `GET /admin/users` - User list (paginated)
- `GET /admin/users/new` - Create user form
- `POST /admin/users/new` - Save new user
- `GET /admin/users/<id>/edit` - Edit user form
- `POST /admin/users/<id>/edit` - Update user
- `POST /admin/users/<id>/delete` - Delete user

### 🧭 Navigation Management (Admin Only)

- **Manage Navigation Items**: Configure dynamic navigation bar
- **Role-Based Visibility**: Show/hide menu items based on user role
- **Position Ordering**: Control menu item ordering

**Routes:**
- `GET /admin/nav` - Navigation list
- `GET /admin/nav/new` - Create nav item form
- `POST /admin/nav/new` - Save nav item
- `GET /admin/nav/<id>/edit` - Edit nav form
- `POST /admin/nav/<id>/edit` - Update nav item
- `POST /admin/nav/<id>/delete` - Delete nav item

### 📈 Analytics & Charts

- **Interactive Charts**: Plotly.js-based visualizations
- **Timeseries Analysis**: Aggregate data by day/week/month
- **Moving Averages**: Calculate trends
- **Export Data**: Download as PDF/PNG

**Routes:**
- `GET /charts` - Interactive dashboard
- `GET /api/records` - JSON API for records
- `GET /api/aggregate` - Aggregated data endpoint

### 📝 Data Analysis

Built-in analysis functions for:
- Timeseries aggregation
- Moving averages
- Statistical summaries
- Category breakdowns

---

## Troubleshooting

### Error: "Can't connect to MySQL server on 127.0.0.1:3306"

**Solution:**
1. Verify XAMPP MySQL module is running
2. Check MySQL credentials in `.env` file
3. Ensure database `py_data_app` exists
4. Run: `mysql -u root -p -e "SHOW DATABASES;"`

### Error: "Access Denied for user 'root'@'localhost'"

**Solution:**
1. Verify MySQL root password (usually empty by default)
2. Test connection: `mysql -u root -p`
3. Update `.env` with correct credentials
4. Check `.env` file is in the application root directory

### Error: "No module named 'flask'"

**Solution:**
1. Verify virtual environment is activated
2. Run: `pip install -r requirements.txt`
3. Check Python path: `which python` (macOS/Linux) or `where python` (Windows)

### Error: "404 Not Found" on charts page

**Solution:**
1. Ensure records exist in database
2. Check database connection
3. Run seed script: `mysql -u root py_data_app < seed_full.sql`
4. Verify templates are in `templates/` directory

### Application Won't Start

**Steps to debug:**
1. Check Python version: `python --version` (should be 3.8+)
2. Verify all imports: `python -c "from app import app"`
3. Check `.env` file configuration
4. Look at console error messages
5. Enable debug mode in `.env`: `FLASK_ENV=development`

---

## API Documentation

### Records Endpoint

```bash
# Get all records (paginated)
curl "http://localhost:5000/api/records?page=1&per_page=50"

# Filter by category
curl "http://localhost:5000/api/records?category=Sales&page=1"

# Response:
{
  "records": [
    {
      "id": 1,
      "category": "Sales",
      "subcategory": "Online",
      "value": 1500.50,
      "recorded_at": "2024-01-15 10:30:00",
      "created_by": "admin"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50,
  "pages": 2
}
```

### Aggregates Endpoint

```bash
# Aggregate by category
curl "http://localhost:5000/api/aggregate?group_by=category"

# Aggregate by subcategory
curl "http://localhost:5000/api/aggregate?group_by=subcategory"

# Response:
{
  "category1": 5000.50,
  "category2": 3200.25,
  ...
}
```

---

## Project Structure

```
project-root/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── models.py                   # Database models
├── forms.py                    # WTForms definitions
├── auth.py                     # Authentication blueprint
├── admin.py                    # Admin panel blueprint
├── records.py                  # Records blueprint
├── db_utils.py                 # Database utilities
├── analysis.py                 # Data analysis functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── seed_full.sql               # Database seed script
└── templates/
    ├── base.html               # Base template
    ├── index.html              # Home page
    ├── charts.html             # Analytics dashboard
    ├── login.html              # Login form
    ├── register.html           # Registration form
    ├── admin/
    │   ├── users.html          # User management
    │   ├── user_form.html      # User form
    │   ├── nav.html            # Navigation management
    │   └── nav_form.html       # Navigation form
    └── records/
        ├── list.html           # Records list
        └── form.html           # Record form
```

---

## Next Steps

1. **Customize Styling**: Edit `static/css/style.css` for your branding
2. **Add More Roles**: Modify `seed_full.sql` to add additional roles
3. **Extend Features**: Create new blueprints following the modular architecture
4. **Deploy to Production**: 
   - Change `FLASK_ENV=production`
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Enable HTTPS
   - Use environment secrets manager

---

## Support & Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/
- **Flask-Login**: https://flask-login.palletsprojects.com/
- **XAMPP Documentation**: https://www.apachefriends.org/faq.html
- **MySQL Reference**: https://dev.mysql.com/doc/

---

## License

This project is provided as-is for educational and commercial use.

---

**Last Updated**: January 2025
**Version**: 1.0

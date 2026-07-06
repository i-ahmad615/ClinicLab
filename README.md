# ClinicLab MVP

A simple Laboratory & Clinic Management System for a single clinic running on one Windows PC. Built with Flask, SQLite, and Bootstrap 5.

## Features

- Role-based authentication (Administrator, Receptionist, Doctor, Lab Technician)
- Dashboard with key counts and quick actions
- Patient management (register, search, edit, deactivate, history)
- Visit management (create, list, history)
- Doctor management (CRUD)
- Placeholder modules for future expansion

## Requirements

- Python 3.12
- Windows 10/11

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Initialize the database and create the default admin:

```powershell
flask --app app.py init-db
```

4. Run the application:

```powershell
python app.py
```

## Default Admin Login

- Username: `admin`
- Password: `admin123`

## Access From Another Device on Same LAN

1. Find the local IP address of the PC running Flask:

```powershell
ipconfig
```

Look for the IPv4 Address (example: `192.168.1.100`).

2. From a phone or another PC on the same Wi-Fi/LAN, open:

```
http://192.168.1.100:5000
```

## Notes

- The database file is stored at `instance/clinic.db`.
- Only Dashboard, Patients, Visits, and Doctors are active in this MVP.
- Other modules show a message: "This module will be available in a future version."

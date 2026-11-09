# MediFlow – Smart Multispeciality Hospital Management System
### *NEXORITHM Startup Project*
> **Tagline:** *"One Platform. Every Step of Patient Care."*

---

## 🏥 Overview
MediFlow is an all-in-one web-based hospital management platform that connects **Patients, Doctors, Receptionists, Pharmacists, and Hospital Administrators** in a single integrated workflow.

---

## 🚀 How to Run MediFlow

### 1. Open Terminal in Project Directory
```powershell
cd "c:\Users\Neha\Desktop\Smart Hospital Management"
```

### 2. Start the Development Server
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

### 3. Open in Browser
Visit: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔑 Pre-Configured Demo Accounts

MediFlow comes with a **1-Click Quick Demo Login Switcher** directly on the sign-in page:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Hospital Admin** | `admin` | `admin123` | Executive KPI dashboard, all modules & reports |
| **Doctor (Cardiology)** | `dr_jenkins` | `doctor123` | Active cabin, patient queue, e-Rx & lab requisition |
| **Doctor (General Med)** | `dr_sharma` | `doctor123` | Primary care consultation desk |
| **Receptionist** | `reception` | `reception123` | Walk-in registration & token vending |
| **Pharmacist** | `pharmacist` | `pharmacy123` | Dispense medications & track stock batches |
| **Lab Technician** | `labtech` | `lab123` | Process laboratory diagnostics |

---

## 🌟 Hero Features Built & Verified

1. **Live OPD Queue TV Display (`/queue/display/`)**
   * Designed for lobby TV screens. Shows **"NOW CONSULTING"** and **"NEXT IN LINE"** with auto-refreshing real-time updates.
2. **Smart Token & Vending System (`/opd/book/`)**
   * Automatic generation of department-specific tokens (e.g. `CARD-001`, `GEN-002`) and Universal Health IDs (`MF-2026-0001`).
3. **Doctor Consultation Desk (`/doctor/desk/<id>/`)**
   * Records vitals, provisional diagnosis, e-Prescriptions with **live pharmacy stock indicators**, and lab test orders.
4. **PharmaFlow Pharmacy Counter (`/pharmacy/`)**
   * Instant electronic prescription fulfillment with automated inventory deduction.
5. **Consolidated Billing Desk (`/billing/`)**
   * Unites Doctor Consultation Fee + Pharmacy Drugs + Lab Investigation charges into a single medical receipt with Cash/UPI settlement.

---

## 🛠️ Project Structure
```text
Smart Hospital Management/
├── apps/
│   ├── users/        # Custom User model & 6 RBAC roles
│   ├── opd/          # Departments, Doctors, Patients & Token Queue
│   ├── clinical/     # Consultations, Vitals, e-Prescriptions & Lab Orders
│   ├── pharmacy/     # Medicine Inventory, Batch/Expiry, Dispensing
│   └── billing/      # Unified Invoicing & Cashier Desk
├── config/           # Django project settings & URLs
├── templates/        # Responsive Tailwind CSS templates
├── venv/             # Python Virtual Environment
├── db.sqlite3        # Initialized database with demo data
└── manage.py
```

---

## 🔄 How to Re-Seed Demo Data Anytime
```powershell
.\venv\Scripts\python.exe manage.py seed_data
```

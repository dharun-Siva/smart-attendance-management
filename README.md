# Smart Attendance Management

A role-based attendance management system with Admin, Faculty, and Student workspaces.

## Quick Start

### Prerequisites

Install the following before starting:

- Python 3.11 or newer
- Node.js 18 or newer and npm
- PostgreSQL 14 or newer

### 1. Create the PostgreSQL database

Create a PostgreSQL database named `smart_attendance`:

```sql
CREATE DATABASE smart_attendance;
```

Make sure your PostgreSQL server is running and that you know the database username and password.

### 2. Set up the backend

From the repository root:

#### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

#### macOS/Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and configure the database connection and JWT secret:

```env
DATABASE_URL=postgresql+psycopg2://<postgres_user>:<postgres_password>@localhost:5432/smart_attendance
JWT_SECRET_KEY=<long-random-secret>
```

Use a strong, private `JWT_SECRET_KEY`. Never commit `.env` or reuse the development secret in production.

### 3. Run database migrations

With the backend virtual environment activated and your current directory set to `backend`:

```bash
alembic upgrade head
```

### 4. Create the development Admin account

The project includes a development-only, local CLI seed script. It creates or safely reconciles the initial Admin account and is not a public API endpoint.

From the `backend` directory, with the virtual environment activated:

```bash
python -m scripts.seed_admin
```

This creates or reconciles the following **DEVELOPMENT credentials only**:

```text
Username: admin
Password: Admin@123
Email: admin@smartattendance.local
Role: ADMIN
```

Change or remove these credentials before any production use. Do not run the development seed against a production database.

### 5. Start the backend

From the `backend` directory:

```bash
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

The API runs at `http://localhost:8000`.

### 6. Set up and start the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
```

Create `frontend/.env` if needed and configure the API base URL:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Start the frontend:

```bash
npm run dev -- --host localhost
```

Open the login page at:

http://localhost:5173/login

## Demo Workflow

Use the development Admin account to sign in and create the demo data through the Admin UI:

1. Admin creates a Department.
2. Admin creates a Class and Section.
3. Admin creates a Faculty account and a Student account.
4. Admin enrolls the Student in the Section.
5. Admin assigns the Faculty member to the Subject and Section.
6. Faculty signs in and creates an attendance session.
7. Faculty marks and submits attendance.
8. Student signs in and views attendance percentage, subject attendance, and history.
9. Faculty requests a correction for a submitted attendance record.
10. Admin reviews and approves or rejects the correction.

## Demo Credentials

The development seed provides the initial Admin account:

```text
Username: admin
Password: Admin@123
Email: admin@smartattendance.local
Role: ADMIN
```

These are **DEVELOPMENT credentials only**. Change the password and remove or disable the seeded account before production use.

Faculty and Student demo accounts are created through the Admin UI during the demo workflow. Their credentials are the values entered when those accounts are created.

## Useful Commands

Backend tests:

```bash
cd backend
python -m pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

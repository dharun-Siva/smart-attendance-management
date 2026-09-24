# Smart Attendance Management API

Backend foundation for the Smart Attendance Management System.

## Local setup

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and update `DATABASE_URL`.
4. Run the API with `uvicorn app.main:app --reload`.

Health check: `GET http://localhost:8000/api/v1/health`

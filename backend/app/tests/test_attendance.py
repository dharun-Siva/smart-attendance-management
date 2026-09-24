from datetime import date


def login_headers(client, username):
    token = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "CorrectPassword123!"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_attendance(client, users):
    admin_headers = login_headers(client, "admin")
    department = client.post(
        "/api/v1/departments",
        json={"name": "Attendance Engineering", "code": "ATT"},
        headers=admin_headers,
    ).json()
    class_item = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "Attendance Class", "code": "ATT1"},
        headers=admin_headers,
    ).json()
    section = client.post(
        "/api/v1/sections",
        json={"class_id": class_item["id"], "name": "A"},
        headers=admin_headers,
    ).json()
    second_class = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "Attendance Class 2", "code": "ATT2"},
        headers=admin_headers,
    ).json()
    second_section = client.post(
        "/api/v1/sections",
        json={"class_id": second_class["id"], "name": "B"},
        headers=admin_headers,
    ).json()
    subject = client.post(
        "/api/v1/subjects",
        json={"department_id": department["id"], "name": "Attendance Subject", "code": "ATTS"},
        headers=admin_headers,
    ).json()
    faculty_one = client.post(
        "/api/v1/faculty",
        json={
            "username": "attendance-faculty-one",
            "email": "attendance-one@example.com",
            "password": "CorrectPassword123!",
            "department_id": department["id"],
            "employee_number": "ATT-EMP-1",
            "first_name": "Faculty",
            "last_name": "One",
        },
        headers=admin_headers,
    ).json()
    faculty_two = client.post(
        "/api/v1/faculty",
        json={
            "username": "attendance-faculty-two",
            "email": "attendance-two@example.com",
            "password": "CorrectPassword123!",
            "department_id": department["id"],
            "employee_number": "ATT-EMP-2",
            "first_name": "Faculty",
            "last_name": "Two",
        },
        headers=admin_headers,
    ).json()
    student_one = client.post(
        "/api/v1/students",
        json={
            "username": "attendance-student-one",
            "email": "attendance-student-one@example.com",
            "password": "CorrectPassword123!",
            "department_id": department["id"],
            "student_number": "ATT-STU-1",
            "first_name": "Student",
            "last_name": "One",
        },
        headers=admin_headers,
    ).json()
    student_two = client.post(
        "/api/v1/students",
        json={
            "username": "attendance-student-two",
            "email": "attendance-student-two@example.com",
            "password": "CorrectPassword123!",
            "department_id": department["id"],
            "student_number": "ATT-STU-2",
            "first_name": "Student",
            "last_name": "Two",
        },
        headers=admin_headers,
    ).json()
    for student in (student_one, student_two):
        assert client.post(
            "/api/v1/enrollments",
            json={"student_id": student["id"], "section_id": section["id"]},
            headers=admin_headers,
        ).status_code == 201
    assignment_one = client.post(
        "/api/v1/assignments",
        json={"faculty_id": faculty_one["id"], "subject_id": subject["id"], "section_id": section["id"]},
        headers=admin_headers,
    ).json()
    assignment_two = client.post(
        "/api/v1/assignments",
        json={"faculty_id": faculty_two["id"], "subject_id": subject["id"], "section_id": second_section["id"]},
        headers=admin_headers,
    ).json()
    return {
        "admin": admin_headers,
        "faculty_one": login_headers(client, "attendance-faculty-one"),
        "faculty_two": login_headers(client, "attendance-faculty-two"),
        "student_one": login_headers(client, "attendance-student-one"),
        "student_two": login_headers(client, "attendance-student-two"),
        "assignment_one": assignment_one,
        "assignment_two": assignment_two,
        "section_id": section["id"],
        "subject_id": subject["id"],
        "student_one_id": student_one["id"],
        "student_two_id": student_two["id"],
    }


def create_session(client, headers, assignment_id, day="2026-09-24"):
    return client.post(
        "/api/v1/attendance/sessions",
        json={"faculty_assignment_id": assignment_id, "attendance_date": day, "topic": "Lecture"},
        headers=headers,
    )


def test_faculty_sees_only_active_owned_assignments_and_sessions(client, users):
    data = setup_attendance(client, users)
    assignment_response = client.get("/api/v1/attendance/assignments", headers=data["faculty_one"])
    assert assignment_response.status_code == 200
    assert [item["id"] for item in assignment_response.json()] == [data["assignment_one"]["id"]]

    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"])
    assert session.status_code == 201
    assert session.json()["status"] == "OPEN"
    assert client.get("/api/v1/attendance/sessions", headers=data["faculty_one"]).json()[0]["id"] == session.json()["id"]

    other_faculty_access = client.get(
        f"/api/v1/attendance/sessions/{session.json()['id']}",
        headers=data["faculty_two"],
    )
    assert other_faculty_access.status_code == 403


def test_duplicate_session_and_student_cannot_create_attendance(client, users):
    data = setup_attendance(client, users)
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"])
    assert session.status_code == 201
    duplicate = create_session(client, data["faculty_one"], data["assignment_one"]["id"])
    assert duplicate.status_code == 409
    student_attempt = create_session(client, data["student_one"], data["assignment_one"]["id"], "2026-09-25")
    assert student_attempt.status_code == 403


def test_records_require_enrollment_and_reject_duplicate_payload(client, users):
    data = setup_attendance(client, users)
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"]).json()
    duplicate_payload = {"records": [
        {"student_id": data["student_one_id"], "status": "PRESENT"},
        {"student_id": data["student_one_id"], "status": "ABSENT"},
    ]}
    assert client.put(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        json=duplicate_payload,
        headers=data["faculty_one"],
    ).status_code == 409
    invalid_student = client.put(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        json={"records": [{"student_id": 99999, "status": "PRESENT"}]},
        headers=data["faculty_one"],
    )
    assert invalid_student.status_code == 400
    invalid_status = client.put(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        json={"records": [{"student_id": data["student_one_id"], "status": "UNKNOWN"}]},
        headers=data["faculty_one"],
    )
    assert invalid_status.status_code == 422


def test_submit_requires_all_active_enrolled_students(client, users):
    data = setup_attendance(client, users)
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"]).json()
    records_url = f"/api/v1/attendance/sessions/{session['id']}/records"
    submit_url = f"/api/v1/attendance/sessions/{session['id']}/submit"
    client.put(
        records_url,
        json={"records": [{"student_id": data["student_one_id"], "status": "PRESENT"}]},
        headers=data["faculty_one"],
    )
    missing = client.post(submit_url, headers=data["faculty_one"])
    assert missing.status_code == 400
    client.put(
        records_url,
        json={"records": [{"student_id": data["student_two_id"], "status": "ABSENT"}]},
        headers=data["faculty_one"],
    )
    submitted = client.post(submit_url, headers=data["faculty_one"])
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "SUBMITTED"
    assert submitted.json()["submitted_at"] is not None


def test_submitted_and_locked_sessions_cannot_be_edited(client, users):
    data = setup_attendance(client, users)
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"]).json()
    records_url = f"/api/v1/attendance/sessions/{session['id']}/records"
    for student_id in (data["student_one_id"], data["student_two_id"]):
        response = client.put(
            records_url,
            json={"records": [{"student_id": student_id, "status": "PRESENT"}]},
            headers=data["faculty_one"],
        )
        assert response.status_code == 200
    assert client.post(f"/api/v1/attendance/sessions/{session['id']}/submit", headers=data["faculty_one"]).status_code == 200
    submitted_edit = client.put(
        records_url,
        json={"records": [{"student_id": data["student_one_id"], "status": "LATE"}]},
        headers=data["faculty_one"],
    )
    assert submitted_edit.status_code == 400
    faculty_lock = client.post(f"/api/v1/attendance/sessions/{session['id']}/lock", headers=data["faculty_one"])
    assert faculty_lock.status_code == 403
    admin_lock = client.post(f"/api/v1/attendance/sessions/{session['id']}/lock", headers=data["admin"])
    assert admin_lock.status_code == 200
    locked_edit = client.put(
        records_url,
        json={"records": [{"student_id": data["student_one_id"], "status": "LATE"}]},
        headers=data["faculty_one"],
    )
    assert locked_edit.status_code == 400


def test_student_history_and_percentage_and_faculty_summary(client, users):
    data = setup_attendance(client, users)
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"]).json()
    records_url = f"/api/v1/attendance/sessions/{session['id']}/records"
    response = client.put(
        records_url,
        json={"records": [
            {"student_id": data["student_one_id"], "status": "PRESENT", "remarks": "On time"},
            {"student_id": data["student_two_id"], "status": "EXCUSED"},
        ]},
        headers=data["faculty_one"],
    )
    assert response.status_code == 200
    assert response.json()[0]["student_number"] == "ATT-STU-1"
    assert response.json()[0]["student_name"] == "Student One"
    assert client.post(f"/api/v1/attendance/sessions/{session['id']}/submit", headers=data["faculty_one"]).status_code == 200

    history = client.get("/api/v1/attendance/students/me/history", headers=data["student_one"])
    assert history.status_code == 200
    assert len(history.json()) == 1
    percentage = client.get("/api/v1/attendance/students/me/percentage", headers=data["student_one"])
    assert percentage.status_code == 200
    assert percentage.json() == {"attended_sessions": 1, "qualifying_sessions": 1, "attendance_percentage": 100.0}
    faculty_summary = client.get(
        f"/api/v1/attendance/students/{data['student_one_id']}/percentage",
        headers=data["faculty_one"],
    )
    assert faculty_summary.status_code == 200
    assert faculty_summary.json()["attendance_percentage"] == 100.0
    other_section_access = client.get(
        f"/api/v1/attendance/students/{data['student_one_id']}/percentage",
        headers=data["faculty_two"],
    )
    assert other_section_access.status_code == 403


def test_percentage_counts_present_and_late_excludes_excused(client, users):
    data = setup_attendance(client, users)
    statuses = [("PRESENT", "2026-09-24"), ("LATE", "2026-09-25"), ("ABSENT", "2026-09-26"), ("EXCUSED", "2026-09-27")]
    for status_value, day in statuses:
        session = create_session(client, data["faculty_one"], data["assignment_one"]["id"], day).json()
        records = [
            {"student_id": data["student_one_id"], "status": status_value},
            {"student_id": data["student_two_id"], "status": "PRESENT"},
        ]
        assert client.put(
            f"/api/v1/attendance/sessions/{session['id']}/records",
            json={"records": records},
            headers=data["faculty_one"],
        ).status_code == 200
        assert client.post(f"/api/v1/attendance/sessions/{session['id']}/submit", headers=data["faculty_one"]).status_code == 200
    percentage = client.get("/api/v1/attendance/students/me/percentage", headers=data["student_one"])
    assert percentage.json() == {"attended_sessions": 2, "qualifying_sessions": 3, "attendance_percentage": 66.67}

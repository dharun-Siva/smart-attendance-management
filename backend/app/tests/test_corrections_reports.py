from app.tests.test_attendance import create_session, setup_attendance


PASSWORD = "CorrectPassword123!"


def submitted_session(client, data, day="2026-09-24", first_status="PRESENT", second_status="PRESENT"):
    session = create_session(client, data["faculty_one"], data["assignment_one"]["id"], day).json()
    records = client.put(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        json={"records": [
            {"student_id": data["student_one_id"], "status": first_status},
            {"student_id": data["student_two_id"], "status": second_status},
        ]},
        headers=data["faculty_one"],
    )
    assert records.status_code == 200
    submitted = client.post(
        f"/api/v1/attendance/sessions/{session['id']}/submit",
        headers=data["faculty_one"],
    )
    assert submitted.status_code == 200
    return session, records.json()


def test_correction_request_rules_and_admin_approval(client, users):
    data = setup_attendance(client, users)
    session, records = submitted_session(client, data)
    record_id = records[0]["id"]
    request_url = f"/api/v1/attendance/records/{record_id}/corrections"
    payload = {"new_status": "ABSENT", "reason": "Attendance was recorded incorrectly"}

    created = client.post(request_url, json=payload, headers=data["faculty_one"])
    assert created.status_code == 201
    correction = created.json()
    assert correction["old_status"] == "PRESENT"
    assert correction["status"] == "PENDING"
    assert "password_hash" not in correction
    assert client.post(request_url, json=payload, headers=data["faculty_one"]).status_code == 409
    assert client.post(request_url, json=payload, headers=data["student_one"]).status_code == 403
    assert client.post(request_url, json=payload, headers=data["faculty_two"]).status_code == 403
    assert client.post(request_url, json={"new_status": "ABSENT"}, headers=data["faculty_one"]).status_code == 422

    assert client.post(
        f"/api/v1/corrections/{correction['id']}/approve",
        headers=data["faculty_one"],
    ).status_code == 403
    approved = client.post(
        f"/api/v1/corrections/{correction['id']}/approve",
        json={"review_comment": "Approved"},
        headers=data["admin"],
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"
    records_after = client.get(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        headers=data["admin"],
    )
    assert records_after.json()[0]["status"] == "ABSENT"
    assert client.post(
        f"/api/v1/corrections/{correction['id']}/reject",
        headers=data["admin"],
    ).status_code == 409


def test_rejected_correction_does_not_change_attendance(client, users):
    data = setup_attendance(client, users)
    session, records = submitted_session(client, data, first_status="LATE")
    correction = client.post(
        f"/api/v1/attendance/records/{records[0]['id']}/corrections",
        json={"new_status": "ABSENT", "reason": "Review requested"},
        headers=data["faculty_one"],
    ).json()
    rejected = client.post(
        f"/api/v1/corrections/{correction['id']}/reject",
        json={"review_comment": "Evidence was insufficient"},
        headers=data["admin"],
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "REJECTED"
    records_after = client.get(
        f"/api/v1/attendance/sessions/{session['id']}/records",
        headers=data["admin"],
    )
    assert records_after.json()[0]["status"] == "LATE"


def test_correction_list_is_scoped_to_admin_or_requesting_faculty(client, users):
    data = setup_attendance(client, users)
    _, records = submitted_session(client, data)
    created = client.post(
        f"/api/v1/attendance/records/{records[0]['id']}/corrections",
        json={"new_status": "ABSENT", "reason": "Correction needed"},
        headers=data["faculty_one"],
    )
    assert created.status_code == 201
    assert len(client.get("/api/v1/corrections", headers=data["faculty_one"]).json()) == 1
    assert len(client.get("/api/v1/corrections", headers=data["admin"]).json()) == 1
    assert client.get("/api/v1/corrections", headers=data["student_one"]).status_code == 403


def test_reports_calculate_low_attendance_and_authorize_scopes(client, users):
    data = setup_attendance(client, users)
    statuses = [
        ("PRESENT", "PRESENT", "2026-09-24"),
        ("LATE", "PRESENT", "2026-09-25"),
        ("ABSENT", "PRESENT", "2026-09-26"),
        ("EXCUSED", "PRESENT", "2026-09-27"),
    ]
    for first_status, second_status, day in statuses:
        submitted_session(client, data, day, first_status, second_status)

    low_admin = client.get("/api/v1/reports/low-attendance", headers=data["admin"])
    assert low_admin.status_code == 200
    low_rows = low_admin.json()
    student_one_row = next(row for row in low_rows if row["student_id"] == data["student_one_id"])
    assert student_one_row["attended_sessions"] == 2
    assert student_one_row["qualifying_sessions"] == 3
    assert student_one_row["attendance_percentage"] == 66.67
    assert data["student_two_id"] not in {row["student_id"] for row in low_rows}

    faculty_low = client.get("/api/v1/reports/low-attendance", headers=data["faculty_one"])
    assert faculty_low.status_code == 200
    student_report = client.get(
        f"/api/v1/reports/students/{data['student_one_id']}/attendance",
        headers=data["student_one"],
    )
    assert student_report.status_code == 200
    assert student_report.json()[0]["attendance_percentage"] == 66.67
    assert client.get(
        f"/api/v1/reports/students/{data['student_two_id']}/attendance",
        headers=data["student_one"],
    ).status_code == 403
    assert client.get(
        "/api/v1/reports/sections/99999/attendance",
        headers=data["faculty_two"],
    ).status_code == 403
    assert client.get(
        "/api/v1/reports/sections/99999/attendance",
        headers=data["student_one"],
    ).status_code == 403

    section_report = client.get(
        f"/api/v1/reports/sections/{data['section_id']}/attendance",
        headers=data["admin"],
    )
    assert section_report.status_code == 200
    subject_report = client.get(
        f"/api/v1/reports/subjects/{data['subject_id']}/attendance",
        headers=data["admin"],
    )
    assert subject_report.status_code == 200

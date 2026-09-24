from app.models.enums import UserRole


PASSWORD = "CorrectPassword123!"


def admin_headers(client):
    token = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": PASSWORD},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_crud_academic_records(client, users):
    headers = admin_headers(client)

    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Computer Science", "code": "CS"},
        headers=headers,
    )
    assert department_response.status_code == 201
    department = department_response.json()

    class_response = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "BSc CS", "code": "BSCS"},
        headers=headers,
    )
    assert class_response.status_code == 201
    class_item = class_response.json()

    section_response = client.post(
        "/api/v1/sections",
        json={"class_id": class_item["id"], "name": "A"},
        headers=headers,
    )
    assert section_response.status_code == 201

    subject_response = client.post(
        "/api/v1/subjects",
        json={"department_id": department["id"], "name": "Databases", "code": "DB101"},
        headers=headers,
    )
    assert subject_response.status_code == 201

    update_response = client.patch(
        f"/api/v1/departments/{department['id']}",
        json={"name": "Computer Science and Engineering"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Computer Science and Engineering"
    assert client.get(f"/api/v1/departments/{department['id']}", headers=headers).status_code == 200
    assert client.get("/api/v1/classes", headers=headers).status_code == 200
    assert client.get("/api/v1/sections", headers=headers).status_code == 200
    assert client.get("/api/v1/subjects", headers=headers).status_code == 200


def test_admin_can_create_accounts_enrollment_and_assignment(client, users):
    headers = admin_headers(client)
    department = client.post(
        "/api/v1/departments",
        json={"name": "Engineering", "code": "ENG"},
        headers=headers,
    ).json()
    class_item = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "ECE", "code": "ECE1"},
        headers=headers,
    ).json()
    section = client.post(
        "/api/v1/sections",
        json={"class_id": class_item["id"], "name": "A"},
        headers=headers,
    ).json()
    subject = client.post(
        "/api/v1/subjects",
        json={"department_id": department["id"], "name": "Circuits", "code": "CIR1"},
        headers=headers,
    ).json()
    faculty = client.post(
        "/api/v1/faculty",
        json={
            "username": "newfaculty",
            "email": "newfaculty@example.com",
            "password": PASSWORD,
            "department_id": department["id"],
            "employee_number": "EMP-1",
            "first_name": "New",
            "last_name": "Faculty",
        },
        headers=headers,
    )
    assert faculty.status_code == 201
    assert "password_hash" not in faculty.json()

    student = client.post(
        "/api/v1/students",
        json={
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password": PASSWORD,
            "department_id": department["id"],
            "student_number": "STU-1",
            "first_name": "New",
            "last_name": "Student",
        },
        headers=headers,
    )
    assert student.status_code == 201
    assert "password_hash" not in student.json()

    enrollment = client.post(
        "/api/v1/enrollments",
        json={"student_id": student.json()["id"], "section_id": section["id"]},
        headers=headers,
    )
    assert enrollment.status_code == 201

    assignment = client.post(
        "/api/v1/assignments",
        json={
            "faculty_id": faculty.json()["id"],
            "subject_id": subject["id"],
            "section_id": section["id"],
        },
        headers=headers,
    )
    assert assignment.status_code == 201
    assert client.get("/api/v1/faculty", headers=headers).status_code == 200
    assert client.get("/api/v1/students", headers=headers).status_code == 200
    assert client.get("/api/v1/enrollments", headers=headers).status_code == 200
    assert client.get("/api/v1/assignments", headers=headers).status_code == 200


def test_faculty_and_student_cannot_access_admin_apis(client, users):
    for username in ("faculty", "student"):
        token = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": PASSWORD},
        ).json()["access_token"]
        response = client.get(
            "/api/v1/departments",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_duplicate_accounts_are_rejected(client, users):
    headers = admin_headers(client)
    department = client.post(
        "/api/v1/departments",
        json={"name": "Math", "code": "MATH"},
        headers=headers,
    ).json()
    payload = {
        "username": "duplicate-user",
        "email": "duplicate@example.com",
        "password": PASSWORD,
        "department_id": department["id"],
        "employee_number": "EMP-DUP",
        "first_name": "Duplicate",
        "last_name": "User",
    }
    assert client.post("/api/v1/faculty", json=payload, headers=headers).status_code == 201
    assert client.post("/api/v1/faculty", json=payload, headers=headers).status_code == 409

    student_payload = {
        "username": "duplicate-student",
        "email": "duplicate-student@example.com",
        "password": PASSWORD,
        "department_id": department["id"],
        "student_number": "STU-DUP",
        "first_name": "Duplicate",
        "last_name": "Student",
    }
    assert client.post("/api/v1/students", json=student_payload, headers=headers).status_code == 201
    duplicate_number = {**student_payload, "username": "another-student", "email": "another@example.com"}
    assert client.post("/api/v1/students", json=duplicate_number, headers=headers).status_code == 409


def test_invalid_references_are_rejected(client, users):
    headers = admin_headers(client)
    assert client.post(
        "/api/v1/classes",
        json={"department_id": 9999, "name": "Invalid", "code": "INVALID"},
        headers=headers,
    ).status_code == 404
    assert client.post(
        "/api/v1/sections",
        json={"class_id": 9999, "name": "A"},
        headers=headers,
    ).status_code == 404
    assert client.post(
        "/api/v1/subjects",
        json={"department_id": 9999, "name": "Invalid", "code": "INVALID"},
        headers=headers,
    ).status_code == 404


def test_duplicate_enrollment_and_assignment_are_rejected(client, users):
    headers = admin_headers(client)
    department = client.post(
        "/api/v1/departments",
        json={"name": "Physics", "code": "PHY"},
        headers=headers,
    ).json()
    class_item = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "Physics 1", "code": "PHY1"},
        headers=headers,
    ).json()
    section = client.post("/api/v1/sections", json={"class_id": class_item["id"], "name": "A"}, headers=headers).json()
    subject = client.post(
        "/api/v1/subjects",
        json={"department_id": department["id"], "name": "Mechanics", "code": "MECH"},
        headers=headers,
    ).json()
    faculty = client.post(
        "/api/v1/faculty",
        json={
            "username": "physics-faculty",
            "email": "physics@example.com",
            "password": PASSWORD,
            "department_id": department["id"],
            "employee_number": "EMP-PHY",
            "first_name": "Physics",
            "last_name": "Faculty",
        },
        headers=headers,
    ).json()
    student = client.post(
        "/api/v1/students",
        json={
            "username": "physics-student",
            "email": "physics-student@example.com",
            "password": PASSWORD,
            "department_id": department["id"],
            "student_number": "STU-PHY",
            "first_name": "Physics",
            "last_name": "Student",
        },
        headers=headers,
    ).json()
    enrollment_payload = {"student_id": student["id"], "section_id": section["id"]}
    assert client.post("/api/v1/enrollments", json=enrollment_payload, headers=headers).status_code == 201
    assert client.post("/api/v1/enrollments", json=enrollment_payload, headers=headers).status_code == 409
    assignment_payload = {"faculty_id": faculty["id"], "subject_id": subject["id"], "section_id": section["id"]}
    assert client.post("/api/v1/assignments", json=assignment_payload, headers=headers).status_code == 201
    assert client.post("/api/v1/assignments", json=assignment_payload, headers=headers).status_code == 409


def test_inactive_faculty_cannot_be_assigned(client, users):
    headers = admin_headers(client)
    department = client.post(
        "/api/v1/departments",
        json={"name": "Chemistry", "code": "CHEM"},
        headers=headers,
    ).json()
    faculty = client.post(
        "/api/v1/faculty",
        json={
            "username": "inactive-faculty",
            "email": "inactive-faculty@example.com",
            "password": PASSWORD,
            "department_id": department["id"],
            "employee_number": "EMP-CHEM",
            "first_name": "Inactive",
            "last_name": "Faculty",
        },
        headers=headers,
    ).json()
    client.patch(f"/api/v1/faculty/{faculty['id']}", json={"is_active": False}, headers=headers)
    class_item = client.post(
        "/api/v1/classes",
        json={"department_id": department["id"], "name": "Chemistry 1", "code": "CHEM1"},
        headers=headers,
    ).json()
    section = client.post("/api/v1/sections", json={"class_id": class_item["id"], "name": "A"}, headers=headers).json()
    subject = client.post(
        "/api/v1/subjects",
        json={"department_id": department["id"], "name": "Organic", "code": "ORG"},
        headers=headers,
    ).json()
    response = client.post(
        "/api/v1/assignments",
        json={"faculty_id": faculty["id"], "subject_id": subject["id"], "section_id": section["id"]},
        headers=headers,
    )
    assert response.status_code == 400

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_job_analyze_endpoint():
    payload = {
        "text": (
            "Backend Engineer\n\nRequired Skills\n- Python\n- FastAPI\n\n"
            "Responsibilities\n- Build APIs\n- Write tests\n"
        )
    }
    response = client.post("/job/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Python" in data["required_skills"]


def test_ats_score_endpoint():
    payload = {
        "resume": {
            "name": "Jane Doe",
            "skills": ["Python", "FastAPI"],
            "experience": ["Improved performance by 25%."],
            "education": ["B.S. CS"],
            "projects": [],
            "certifications": [],
            "raw_text": "Jane Doe Summary Skills Experience Education " + "word " * 150,
        },
        "job_description": {
            "role_title": "Backend Engineer",
            "required_skills": ["Python", "FastAPI"],
            "preferred_skills": [],
            "responsibilities": [],
            "raw_text": "jd text",
        },
    }
    response = client.post("/ats-score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["ats_score"] <= 100
    assert "keyword_match" in data["breakdown"]


def test_resume_match_endpoint():
    payload = {
        "resume": {"skills": ["Python"], "raw_text": "Python developer"},
        "job_description": {"required_skills": ["Python", "Go"], "preferred_skills": []},
    }
    response = client.post("/resume-match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Python" in data["matched_skills"]
    assert "Go" in data["missing_skills"]


def test_resume_upload_rejects_non_pdf():
    response = client.post(
        "/resume/upload",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 415

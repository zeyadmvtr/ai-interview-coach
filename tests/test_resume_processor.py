from app.services.resume_processor import ResumeProcessor

SAMPLE_RESUME = """Jane Doe
jane.doe@example.com
+1 (415) 555-0134

Summary
Backend engineer with 4 years of experience building distributed systems.

Skills
Python, FastAPI, PostgreSQL, Docker, AWS, Kubernetes

Experience
- Senior Backend Engineer at Acme Corp (2021-Present)
  Led migration of monolith to microservices, reducing latency by 30%.
- Backend Engineer at Globex (2019-2021)
  Built REST APIs serving 1M+ requests per day.

Education
- B.S. Computer Science, State University (2015-2019)

Projects
- Open source contribution to FastAPI ecosystem, 500+ GitHub stars.

Certifications
- AWS Certified Solutions Architect
"""


def test_parse_text_extracts_email_and_phone():
    resume = ResumeProcessor().parse_text(SAMPLE_RESUME)
    assert resume.email == "jane.doe@example.com"
    assert resume.phone is not None


def test_parse_text_extracts_name():
    resume = ResumeProcessor().parse_text(SAMPLE_RESUME)
    assert resume.name == "Jane Doe"


def test_parse_text_extracts_skills():
    resume = ResumeProcessor().parse_text(SAMPLE_RESUME)
    skill_keys = {s.lower() for s in resume.skills}
    assert "python" in skill_keys
    assert "fastapi" in skill_keys
    assert "docker" in skill_keys


def test_parse_text_extracts_experience_and_education():
    resume = ResumeProcessor().parse_text(SAMPLE_RESUME)
    assert len(resume.experience) == 2
    assert len(resume.education) == 1
    assert "Acme Corp" in resume.experience[0]


def test_parse_text_extracts_certifications_and_projects():
    resume = ResumeProcessor().parse_text(SAMPLE_RESUME)
    assert len(resume.certifications) == 1
    assert len(resume.projects) == 1

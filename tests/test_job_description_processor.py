from app.services.job_description_processor import JobDescriptionProcessor

SAMPLE_JD = """Senior Backend Engineer

About the Role
We are looking for a senior backend engineer to join our platform team.

Required Skills
- Python
- FastAPI
- PostgreSQL
- Docker

Preferred Skills
- Kubernetes
- AWS

Responsibilities
- Design and build scalable backend services
- Mentor junior engineers
- Participate in on-call rotation

5+ years of experience required.
"""


def test_parse_extracts_role_title():
    jd = JobDescriptionProcessor().parse(SAMPLE_JD)
    assert jd.role_title == "Senior Backend Engineer"


def test_parse_extracts_required_and_preferred_skills():
    jd = JobDescriptionProcessor().parse(SAMPLE_JD)
    assert "Python" in jd.required_skills
    assert "FastAPI" in jd.required_skills
    assert "Kubernetes" in jd.preferred_skills


def test_parse_extracts_responsibilities():
    jd = JobDescriptionProcessor().parse(SAMPLE_JD)
    assert len(jd.responsibilities) == 3


def test_parse_extracts_experience_requirement():
    jd = JobDescriptionProcessor().parse(SAMPLE_JD)
    assert jd.experience_requirements is not None
    assert "5" in jd.experience_requirements

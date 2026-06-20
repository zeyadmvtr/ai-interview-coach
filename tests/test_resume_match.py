from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData
from app.services.resume_match import ResumeMatchEngine

engine = ResumeMatchEngine()


def test_full_match_scores_100():
    resume = ResumeData(skills=["Python", "FastAPI"], raw_text="Python FastAPI experience")
    jd = JobDescriptionData(required_skills=["Python", "FastAPI"], preferred_skills=[])
    result = engine.match(resume, jd)
    assert result["match_score"] == 100
    assert result["missing_skills"] == []


def test_partial_match_lists_missing_skills():
    resume = ResumeData(skills=["Python"], raw_text="Python developer")
    jd = JobDescriptionData(required_skills=["Python", "Go"], preferred_skills=["Docker"])
    result = engine.match(resume, jd)
    assert "Go" in result["missing_skills"]
    assert "Docker" in result["missing_skills"]
    assert "Python" in result["matched_skills"]
    assert 0 < result["match_score"] < 100


def test_no_jd_skills_is_neutral():
    resume = ResumeData(skills=["Python"], raw_text="Python developer")
    jd = JobDescriptionData(required_skills=[], preferred_skills=[])
    result = engine.match(resume, jd)
    assert result["match_score"] == 50


def test_recommendations_mention_missing_required_skills():
    resume = ResumeData(skills=[], raw_text="")
    jd = JobDescriptionData(required_skills=["Rust"], preferred_skills=[])
    result = engine.match(resume, jd)
    assert any("Rust" in rec for rec in result["recommendations"])

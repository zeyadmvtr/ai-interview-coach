from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData
from app.services.ats_scoring import ATSScoringEngine

engine = ATSScoringEngine()


def make_resume(**overrides) -> ResumeData:
    defaults = dict(
        name="Jane Doe",
        email="jane@example.com",
        phone="555-0134",
        skills=["Python", "FastAPI", "Docker"],
        experience=["Built APIs that improved throughput by 30%."],
        education=["B.S. Computer Science"],
        projects=["Open source project with 500 stars."],
        certifications=["AWS Certified"],
        raw_text="Jane Doe\nSummary\nExperience\nSkills\nProjects\nEducation\n" + "word " * 200,
    )
    defaults.update(overrides)
    return ResumeData(**defaults)


def make_jd(**overrides) -> JobDescriptionData:
    defaults = dict(
        role_title="Backend Engineer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        experience_requirements="3+ years",
        responsibilities=["Build services"],
        raw_text="job description text",
    )
    defaults.update(overrides)
    return JobDescriptionData(**defaults)


def test_score_is_within_bounds():
    score, breakdown = engine.score(make_resume(), make_jd())
    assert 0 <= score <= 100
    assert set(breakdown.keys()) == {"keyword_match", "structure", "readability", "impact"}


def test_full_keyword_match_gets_full_points():
    score, breakdown = engine.score(make_resume(), make_jd())
    assert breakdown["keyword_match"]["score"] == 40


def test_missing_all_keywords_scores_zero_on_that_component():
    resume = make_resume(skills=["Java"], raw_text="Just some unrelated text " * 50)
    score, breakdown = engine.score(resume, make_jd())
    assert breakdown["keyword_match"]["score"] == 0


def test_empty_jd_skills_is_neutral_not_punitive():
    jd = make_jd(required_skills=[], preferred_skills=[])
    score, breakdown = engine.score(make_resume(), jd)
    assert breakdown["keyword_match"]["score"] == 40


def test_impact_score_rewards_quantified_achievements():
    resume = make_resume(experience=["Increased revenue by 20% and cut costs by $50,000."])
    score, breakdown = engine.score(resume, make_jd())
    assert breakdown["impact"]["score"] > 0

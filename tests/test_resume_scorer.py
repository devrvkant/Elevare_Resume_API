from app.resume_scorer import calculate_overall_score, score_resume_with_ai


def test_calculate_overall_score_uses_weighted_categories():
    score = calculate_overall_score(
        {
            "grammar": 80,
            "formatting": 70,
            "industry_standards": 75,
            "genuine_skills": 85,
            "company_standards": 65,
            "ats_readability": 90,
        }
    )

    assert score == 76


def test_score_resume_with_ai_requires_groq_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    result = score_resume_with_ai("Python developer with clean project experience.", ["Python"])

    assert result.overall_score == 0
    assert result.fallback_used is True
    assert result.scoring_method == "unavailable"

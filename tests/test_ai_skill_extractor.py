from app.ai_skill_extractor import extract_skills_hybrid


def test_extract_skills_hybrid_uses_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    result = extract_skills_hybrid("Python developer using ReactJS and Postgres.")

    assert result.extraction_method == "keyword_fallback"
    assert result.fallback_used is True
    assert result.skills == ["PostgreSQL", "Python", "React"]

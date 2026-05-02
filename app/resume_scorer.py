import json
import os
from dataclasses import dataclass

from groq import Groq, GroqError
from pydantic import BaseModel, Field, ValidationError

from app.ai_skill_extractor import _response_format_for_model


WEIGHTS = {
    "grammar": 0.15,
    "formatting": 0.15,
    "industry_standards": 0.20,
    "genuine_skills": 0.20,
    "company_standards": 0.20,
    "ats_readability": 0.10,
}


class ResumeCategoryScores(BaseModel):
    grammar: int = Field(ge=0, le=100)
    formatting: int = Field(ge=0, le=100)
    industry_standards: int = Field(ge=0, le=100)
    genuine_skills: int = Field(ge=0, le=100)
    company_standards: int = Field(ge=0, le=100)
    ats_readability: int = Field(ge=0, le=100)


class ResumeScoreResponse(BaseModel):
    category_scores: ResumeCategoryScores
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


@dataclass(frozen=True)
class ResumeScoreResult:
    overall_score: int
    category_scores: dict[str, int]
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    scoring_method: str
    fallback_used: bool
    error: str | None = None


SCORING_SYSTEM_PROMPT = """
You are an AI resume quality evaluator.

Evaluate the resume using these categories:
- grammar: spelling, grammar, sentence clarity, professional language.
- formatting: section structure, readability, consistency, clean layout, ATS-friendly formatting.
- industry_standards: alignment with common expectations for the candidate's target industry or role.
- genuine_skills: whether skills look relevant, supported by projects/experience, and not randomly listed.
- company_standards: professionalism, impact, measurable achievements, recruiter readiness.
- ats_readability: keyword clarity, simple parsing, relevant terms, and lack of confusing formatting.

Rules:
- Respond only with JSON.
- Use this exact shape:
  {
    "category_scores": {
      "grammar": 80,
      "formatting": 75,
      "industry_standards": 70,
      "genuine_skills": 78,
      "company_standards": 72,
      "ats_readability": 82
    },
    "summary": "Short explanation of resume quality.",
    "strengths": ["Specific strength"],
    "weaknesses": ["Specific weakness"],
    "suggestions": ["Specific improvement"]
  }
- Every score must be an integer from 0 to 100.
- Be fair and strict. Do not give very high scores unless the resume clearly supports them.
- Do not include names, phone numbers, email addresses, or private personal details.
- Do not invent experience that is not in the resume.
"""


def score_resume_with_ai(text: str, skills: list[str] | None = None) -> ResumeScoreResult:
    if not os.getenv("GROQ_API_KEY"):
        return _fallback_score("GROQ_API_KEY is not set.")

    try:
        ai_score = _score_resume_with_groq(text, skills or [])
    except (GroqError, ValidationError, json.JSONDecodeError) as exc:
        return _fallback_score(f"Groq resume scoring failed: {exc}")
    except Exception as exc:
        return _fallback_score(f"Resume scoring failed: {exc}")

    category_scores = ai_score.category_scores.model_dump()
    overall_score = calculate_overall_score(category_scores)

    return ResumeScoreResult(
        overall_score=overall_score,
        category_scores=category_scores,
        summary=ai_score.summary,
        strengths=ai_score.strengths,
        weaknesses=ai_score.weaknesses,
        suggestions=ai_score.suggestions,
        scoring_method="groq_resume_quality",
        fallback_used=False,
    )


def calculate_overall_score(category_scores: dict[str, int]) -> int:
    score = sum(category_scores[key] * weight for key, weight in WEIGHTS.items())
    return round(score)


def _score_resume_with_groq(text: str, skills: list[str]) -> ResumeScoreResponse:
    client = Groq()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SCORING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_scoring_prompt(text, skills),
            },
        ],
        response_format=_response_format_for_model(model),
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Groq returned an empty response.")

    return ResumeScoreResponse.model_validate(json.loads(content))


def _build_scoring_prompt(text: str, skills: list[str]) -> str:
    detected_skills = ", ".join(skills) if skills else "No extracted skills were provided."
    return f"""
Resume text:
{text[:12000]}

Already extracted skills:
{detected_skills}
"""


def _fallback_score(error: str) -> ResumeScoreResult:
    category_scores = {
        "grammar": 0,
        "formatting": 0,
        "industry_standards": 0,
        "genuine_skills": 0,
        "company_standards": 0,
        "ats_readability": 0,
    }

    return ResumeScoreResult(
        overall_score=0,
        category_scores=category_scores,
        summary="Resume quality scoring needs an active Groq API key.",
        strengths=[],
        weaknesses=["AI resume scoring is unavailable."],
        suggestions=["Add a Groq API key in the sidebar, then click Score Resume again."],
        scoring_method="unavailable",
        fallback_used=True,
        error=error,
    )


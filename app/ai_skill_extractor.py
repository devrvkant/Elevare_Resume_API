import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import Groq, GroqError
from pydantic import BaseModel, Field

from app.skill_extractor import extract_skills


load_dotenv()


class SkillExtraction(BaseModel):
    skills: list[str] = Field(
        description="Normalized technical, professional, and domain skills found in the resume."
    )


@dataclass(frozen=True)
class SkillExtractionResult:
    skills: list[str]
    extraction_method: str
    fallback_used: bool
    error: str | None = None


SYSTEM_PROMPT = """
You extract skills from resumes.

Rules:
- Respond only with JSON in this exact shape: {"skills": ["Python", "React"]}.
- Return only skills, tools, technologies, methods, platforms, and professional capabilities.
- Do not return names, phone numbers, emails, addresses, companies, schools, degrees, job titles, or full sentences.
- Normalize common variants, for example ReactJS to React, Postgres to PostgreSQL, JS to JavaScript.
- Keep skills short and readable.
- Remove duplicates.
- Do not invent skills that are not supported by the resume text.
"""

STRUCTURED_OUTPUT_MODELS = {
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
}


def extract_skills_hybrid(text: str) -> SkillExtractionResult:
    fallback_skills = extract_skills(text)

    if not os.getenv("GROQ_API_KEY"):
        return SkillExtractionResult(
            skills=fallback_skills,
            extraction_method="keyword_fallback",
            fallback_used=True,
            error="GROQ_API_KEY is not set.",
        )

    try:
        ai_skills = _extract_skills_with_groq(text)
    except GroqError as exc:
        return SkillExtractionResult(
            skills=fallback_skills,
            extraction_method="keyword_fallback",
            fallback_used=True,
            error=f"Groq request failed: {exc}",
        )
    except Exception as exc:
        return SkillExtractionResult(
            skills=fallback_skills,
            extraction_method="keyword_fallback",
            fallback_used=True,
            error=f"AI extraction failed: {exc}",
        )

    combined_skills = _merge_skills(ai_skills, fallback_skills)

    return SkillExtractionResult(
        skills=combined_skills,
        extraction_method="groq_hybrid",
        fallback_used=False,
    )


def _extract_skills_with_groq(text: str) -> list[str]:
    client = Groq()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    response_format = _response_format_for_model(model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract resume skills from this resume text:\n\n{text[:12000]}",
            },
        ],
        response_format=response_format,
    )

    content = response.choices[0].message.content
    if not content:
        return []

    parsed = SkillExtraction.model_validate(json.loads(content))
    return _clean_skills(parsed.skills)


def _response_format_for_model(model: str) -> dict[str, object]:
    if model in STRUCTURED_OUTPUT_MODELS:
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "resume_skill_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["skills"],
                    "additionalProperties": False,
                },
            },
        }

    return {"type": "json_object"}


def _merge_skills(primary_skills: list[str], fallback_skills: list[str]) -> list[str]:
    return sorted(
        {skill for skill in _clean_skills(primary_skills + fallback_skills)},
        key=str.casefold,
    )


def _clean_skills(skills: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized = " ".join(str(skill).strip().split())
        if not normalized:
            continue

        key = normalized.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(normalized)

    return cleaned

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.ai_skill_extractor import extract_skills_hybrid
from app.resume_parser import UnsupportedFileTypeError, extract_text_from_upload
from app.resume_scorer import score_resume_with_ai

app = FastAPI(title="Resume Skill Extractor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Resume API is running", "endpoints": ["/health", "/extract-skills", "/score-resume"]}


@app.get("/health")
def health():
    print("Health check called")
    return {"status": "ok"}


@app.post("/extract-skills")
async def extract_resume_skills(file: UploadFile = File(...)) -> dict[str, object]:
    try:
        text = await extract_text_from_upload(file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = extract_skills_hybrid(text)

    return {
        "filename": file.filename,
        "skills": result.skills,
        "skill_count": len(result.skills),
        "extraction_method": result.extraction_method,
        "fallback_used": result.fallback_used,
        "error": result.error,
    }


@app.post("/score-resume")
async def score_resume(file: UploadFile = File(...)) -> dict[str, object]:
    try:
        text = await extract_text_from_upload(file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    skill_result = extract_skills_hybrid(text)
    score_result = score_resume_with_ai(text, skill_result.skills)

    return {
        "filename": file.filename,
        "skills": skill_result.skills,
        "skill_count": len(skill_result.skills),
        "overall_score": score_result.overall_score,
        "category_scores": score_result.category_scores,
        "summary": score_result.summary,
        "strengths": score_result.strengths,
        "weaknesses": score_result.weaknesses,
        "suggestions": score_result.suggestions,
        "extraction_method": skill_result.extraction_method,
        "scoring_method": score_result.scoring_method,
        "fallback_used": skill_result.fallback_used or score_result.fallback_used,
        "error": score_result.error or skill_result.error,
    }

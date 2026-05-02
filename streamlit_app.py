import asyncio
import os

import streamlit as st
from dotenv import load_dotenv
from starlette.datastructures import UploadFile

from app.ai_skill_extractor import SkillExtractionResult, extract_skills_hybrid
from app.resume_parser import UnsupportedFileTypeError, extract_text_from_upload
from app.resume_scorer import ResumeScoreResult, score_resume_with_ai


load_dotenv()

st.set_page_config(page_title="Resume Skill Extractor", layout="centered")

st.title("Resume Skill Extractor")
st.write("Upload a PDF, DOCX, or TXT resume to extract skills, then score the resume quality.")

with st.sidebar:
    st.subheader("AI Settings")
    model = st.text_input("Model", value=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    if os.getenv("GROQ_API_KEY"):
        st.success("Groq API key loaded from .env")
    else:
        st.warning("Groq API key is missing. Add it to your .env file.")

if model:
    os.environ["GROQ_MODEL"] = model

uploaded_file = st.file_uploader("Resume file", type=["pdf", "docx", "txt"])


async def parse_uploaded_file() -> tuple[str, SkillExtractionResult]:
    upload = UploadFile(filename=uploaded_file.name, file=uploaded_file)
    text = await extract_text_from_upload(upload)
    return text, extract_skills_hybrid(text)


if uploaded_file:
    try:
        with st.spinner("Reading resume..."):
            resume_text, result = asyncio.run(parse_uploaded_file())

        st.subheader("Extracted Skills")
        if result.extraction_method == "groq_hybrid":
            st.success("Groq AI extraction is active")
        else:
            st.warning("Using keyword fallback. Add a Groq API key to your .env file for AI extraction.")

        if result.error:
            st.caption(result.error)

        if result.skills:
            st.success(f"Found {len(result.skills)} skills")
            st.write(", ".join(result.skills))
            st.json(
                {
                    "filename": uploaded_file.name,
                    "skills": result.skills,
                    "skill_count": len(result.skills),
                    "extraction_method": result.extraction_method,
                    "fallback_used": result.fallback_used,
                }
            )
        else:
            st.info("No skills found in this resume.")

        st.subheader("Resume Quality Score")
        st.write("Score the resume using grammar, formatting, industry standards, genuine skills, company standards, and ATS readability.")

        if st.button("Score Resume", type="primary"):
            with st.spinner("Scoring resume with Groq..."):
                score_result: ResumeScoreResult = score_resume_with_ai(resume_text, result.skills)

            if score_result.error:
                st.warning(score_result.error)

            st.metric("Overall Score", f"{score_result.overall_score}/100")

            st.markdown("**Category Scores**")
            st.json(score_result.category_scores)

            st.markdown("**Summary**")
            st.write(score_result.summary)

            if score_result.strengths:
                st.markdown("**Strengths**")
                for item in score_result.strengths:
                    st.write(f"- {item}")

            if score_result.weaknesses:
                st.markdown("**Weaknesses**")
                for item in score_result.weaknesses:
                    st.write(f"- {item}")

            if score_result.suggestions:
                st.markdown("**Suggestions**")
                for item in score_result.suggestions:
                    st.write(f"- {item}")

            st.markdown("**Score JSON Preview**")
            st.json(
                {
                    "filename": uploaded_file.name,
                    "overall_score": score_result.overall_score,
                    "category_scores": score_result.category_scores,
                    "summary": score_result.summary,
                    "strengths": score_result.strengths,
                    "weaknesses": score_result.weaknesses,
                    "suggestions": score_result.suggestions,
                    "scoring_method": score_result.scoring_method,
                    "fallback_used": score_result.fallback_used,
                }
            )

        with st.expander("Preview extracted text"):
            st.text_area("Resume text", resume_text, height=250)
    except UnsupportedFileTypeError as exc:
        st.error(str(exc))
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not process this file: {exc}")

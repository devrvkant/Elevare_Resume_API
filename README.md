# Resume Skill Extractor

A small Python API that accepts a resume upload and returns extracted skills as JSON.
It is built so a React frontend can call it directly with `multipart/form-data`.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To enable AI extraction, create a `.env` file:

```text
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Create this file at the project root:

```text
C:\Users\Divyam\Documents\New project\.env
```

Do not put your API key in React frontend code or commit it to Git. The `.env` file is ignored by Git.

Without an API key, the app still works using the keyword fallback.

The default Groq model uses JSON Object Mode. If you want strict schema output, use a Groq model that supports structured outputs, such as `openai/gpt-oss-20b` or `openai/gpt-oss-120b`.

## Run

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Upload API

`POST /extract-skills`

Form field:

- `file`: resume file, supported formats are `.pdf`, `.docx`, and `.txt`

Example response:

```json
{
  "filename": "resume.pdf",
  "skills": ["Python", "React", "SQL"],
  "skill_count": 3,
  "extraction_method": "groq_hybrid",
  "fallback_used": false,
  "error": null
}
```

## Score API

`POST /score-resume`

This endpoint extracts skills first, then scores resume quality using the Groq AI backend.

Scoring categories:

- Grammar
- Formatting
- Industry standards
- Genuine skills
- Company standards
- ATS readability

Example response:

```json
{
  "filename": "resume.pdf",
  "skills": ["Python", "React", "SQL"],
  "skill_count": 3,
  "overall_score": 78,
  "category_scores": {
    "grammar": 84,
    "formatting": 72,
    "industry_standards": 78,
    "genuine_skills": 80,
    "company_standards": 75,
    "ats_readability": 82
  },
  "summary": "The resume is strong technically but needs stronger measurable impact.",
  "strengths": ["Relevant technical skills"],
  "weaknesses": ["Few quantified achievements"],
  "suggestions": ["Add measurable outcomes to project bullet points"],
  "extraction_method": "groq_hybrid",
  "scoring_method": "groq_resume_quality",
  "fallback_used": false,
  "error": null
}
```

## Streamlit Tester

```powershell
streamlit run streamlit_app.py
```

## React Example

```js
async function extractSkills(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://127.0.0.1:8000/extract-skills", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Could not extract skills");
  }

  return response.json();
}
```

## Health Check

```text
GET /health
```

import re


SKILLS = [
    ".NET",
    "ABAP",
    "AWS",
    "Agile",
    "Airflow",
    "Android",
    "Angular",
    "Ansible",
    "Apache Kafka",
    "Azure",
    "Bash",
    "Bootstrap",
    "C",
    "C#",
    "C++",
    "CSS",
    "CI/CD",
    "Django",
    "Docker",
    "Excel",
    "Express.js",
    "FastAPI",
    "Figma",
    "Firebase",
    "Flask",
    "Git",
    "GitHub",
    "GitLab",
    "Go",
    "GraphQL",
    "HTML",
    "Java",
    "JavaScript",
    "Jenkins",
    "Jira",
    "Kotlin",
    "Kubernetes",
    "Linux",
    "Machine Learning",
    "MongoDB",
    "MySQL",
    "Next.js",
    "Node.js",
    "NumPy",
    "Oracle",
    "PHP",
    "Pandas",
    "PostgreSQL",
    "Power BI",
    "Python",
    "PyTorch",
    "R",
    "React",
    "React Native",
    "Redis",
    "Redux",
    "REST API",
    "Ruby",
    "Rust",
    "SAP",
    "Sass",
    "Scala",
    "Scikit-learn",
    "Selenium",
    "Spark",
    "Spring Boot",
    "SQL",
    "SQLite",
    "Tableau",
    "TensorFlow",
    "Terraform",
    "TypeScript",
    "Vue.js",
    "WordPress",
]

ALIASES = {
    "Amazon Web Services": "AWS",
    "C Sharp": "C#",
    "C Plus Plus": "C++",
    "Cascading Style Sheets": "CSS",
    "Continuous Integration": "CI/CD",
    "Continuous Deployment": "CI/CD",
    "Golang": "Go",
    "JS": "JavaScript",
    "K8s": "Kubernetes",
    "Keras": "TensorFlow",
    "MS Excel": "Excel",
    "Node": "Node.js",
    "Postgres": "PostgreSQL",
    "PowerBI": "Power BI",
    "REST": "REST API",
    "ReactJS": "React",
    "TS": "TypeScript",
}


def extract_skills(text: str) -> list[str]:
    normalized_text = _normalize(text)
    found: set[str] = set()

    for skill in SKILLS:
        if _contains_term(normalized_text, skill):
            found.add(skill)

    for alias, skill in ALIASES.items():
        if _contains_term(normalized_text, alias):
            found.add(skill)

    return sorted(found, key=str.casefold)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _contains_term(text: str, term: str) -> bool:
    escaped = re.escape(term)
    pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

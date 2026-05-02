from app.skill_extractor import extract_skills


def test_extract_skills_finds_direct_matches_and_aliases():
    text = "Built ReactJS dashboards with Python, Postgres, Docker, and AWS."

    assert extract_skills(text) == [
        "AWS",
        "Docker",
        "PostgreSQL",
        "Python",
        "React",
    ]


def test_extract_skills_avoids_partial_word_matches():
    text = "The candidate wrote about scattered scripts and grassroots events."

    assert extract_skills(text) == []


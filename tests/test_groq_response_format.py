from app.ai_skill_extractor import _response_format_for_model


def test_response_format_uses_json_object_for_llama_model():
    assert _response_format_for_model("llama-3.3-70b-versatile") == {
        "type": "json_object"
    }


def test_response_format_uses_schema_for_supported_model():
    response_format = _response_format_for_model("openai/gpt-oss-20b")

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True


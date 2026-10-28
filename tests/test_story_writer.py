import pytest
from unittest.mock import MagicMock
from services.ollama_client import OllamaClient
from services.story_writer import StoryWriter
from services.interview_questions import InterviewQuestionsGenerator
from services.remembrance_builder import RemembranceBuilder

def test_story_enhancement_success():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": True,
        "text": "Every August, Grandma Clara stood on the wooden porch...",
        "error": None
    }

    writer = StoryWriter(mock_ollama)
    result = writer.enhance_story(
        raw_notes="Grandma made lemonade on porch. Lemons and cane sugar.",
        title="Lemonade Days",
        approximate_date="Summer 1996",
        people="Grandma Clara",
        style="warm"
    )

    assert result["success"] is True
    assert "Grandma Clara" in result["story"]
    assert mock_ollama.generate.called

def test_story_enhancement_empty_input():
    mock_ollama = MagicMock(spec=OllamaClient)
    writer = StoryWriter(mock_ollama)
    result = writer.enhance_story(raw_notes="")
    assert result["success"] is False
    assert "empty" in result["error"].lower()
    assert not mock_ollama.generate.called

def test_missing_ollama_or_connection_failure():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": False,
        "text": "",
        "error": "Ollama is not running. Please start Ollama locally (`ollama serve`)."
    }

    writer = StoryWriter(mock_ollama)
    result = writer.enhance_story(
        raw_notes="Some memorable event.",
        title="Test"
    )

    assert result["success"] is False
    assert "ollama is not running" in result["error"].lower()

def test_malformed_or_empty_model_response():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": False,
        "text": "",
        "error": "Model returned an empty response."
    }

    writer = StoryWriter(mock_ollama)
    result = writer.enhance_story(raw_notes="Valid notes here.")
    assert result["success"] is False
    assert "empty response" in result["error"].lower()

def test_suggest_title():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": True,
        "text": "Golden Lemonade Afternoons",
        "error": None
    }

    writer = StoryWriter(mock_ollama)
    res = writer.suggest_title("Grandma lemonade on porch")
    assert res["success"] is True
    assert res["title"] == "Golden Lemonade Afternoons"

def test_interview_questions_generation():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": True,
        "text": "1. What did the porch smell like in August?\n2. Who took the first sip of lemonade?\n3. Was there a special yellow pitcher?\n4. What did Grandma Clara say while squeezing lemons?\n5. Why does this memory bring comfort today?",
        "error": None
    }

    generator = InterviewQuestionsGenerator(mock_ollama)
    res = generator.generate_questions(
        raw_notes="Grandma Clara made lemonade.",
        title="Lemonade Memories",
        people="Grandma Clara"
    )

    assert res["success"] is True
    assert len(res["questions"]) == 5
    assert "lemonade" in res["questions"][1].lower()

def test_remembrance_builder_success():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": True,
        "text": "# In Loving Memory of Martha Vance\nA life lived with generosity and laughter.",
        "error": None
    }

    builder = RemembranceBuilder(mock_ollama)
    res = builder.draft_tribute(
        name="Martha Vance",
        dates="1935 - 2022",
        stories="She loved gardening."
    )

    assert res["success"] is True
    assert "Martha Vance" in res["tribute"]

def test_remembrance_builder_offline_fallback():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "success": False,
        "text": "",
        "error": "Ollama connection timeout"
    }

    builder = RemembranceBuilder(mock_ollama)
    res = builder.draft_tribute(
        name="Martha Vance",
        dates="1935 - 2022",
        sayings="Always be kind."
    )

    # In fallback mode, it still creates a high quality deterministic template
    assert res["success"] is True
    assert res["is_fallback"] is True
    assert "Martha Vance" in res["tribute"]
    assert "Always be kind" in res["tribute"]

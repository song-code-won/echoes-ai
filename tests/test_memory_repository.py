import pytest
import tempfile
import os
import json
from services.memory_repository import MemoryRepository

@pytest.fixture
def temp_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    repo = MemoryRepository(db_path)
    yield repo
    if os.path.exists(db_path):
        os.remove(db_path)

def test_save_and_retrieve_memory(temp_repo):
    mem = {
        "title": "Summer Porch Lemonade",
        "raw_notes": "Grandma Clara squeezed fresh lemons with cane sugar.",
        "category": "Childhood",
        "approximate_date": "Summer 1996",
        "people": "Grandma Clara",
        "tags": "summer, lemonade, grandma"
    }
    mem_id = temp_repo.save_memory(mem)
    assert mem_id is not None
    assert mem_id > 0

    fetched = temp_repo.get_memory(mem_id)
    assert fetched is not None
    assert fetched["title"] == "Summer Porch Lemonade"
    assert "Grandma Clara" in fetched["people"]
    assert fetched["category"] == "Childhood"

def test_edit_memory(temp_repo):
    mem = {
        "title": "Original Title",
        "raw_notes": "Initial rough note.",
        "category": "Family Traditions"
    }
    mem_id = temp_repo.save_memory(mem)

    update_payload = {
        "id": mem_id,
        "title": "Updated Title",
        "raw_notes": "Revised and enriched note.",
        "enhanced_story": "A beautifully rewritten memory.",
        "category": "Celebrations & Milestones"
    }
    temp_repo.save_memory(update_payload)

    updated = temp_repo.get_memory(mem_id)
    assert updated["title"] == "Updated Title"
    assert updated["raw_notes"] == "Revised and enriched note."
    assert updated["enhanced_story"] == "A beautifully rewritten memory."
    assert updated["category"] == "Celebrations & Milestones"

def test_delete_memory(temp_repo):
    mem_id = temp_repo.save_memory({
        "title": "Temporary Note",
        "raw_notes": "To be deleted",
        "category": "Other"
    })
    assert temp_repo.get_memory(mem_id) is not None
    deleted = temp_repo.delete_memory(mem_id)
    assert deleted is True
    assert temp_repo.get_memory(mem_id) is None

def test_search_and_filtering(temp_repo):
    temp_repo.save_memory({
        "title": "Fishing at Pine Lake",
        "raw_notes": "Caught trout with Uncle Dan at dawn.",
        "category": "Travel & Adventures",
        "people": "Uncle Dan",
        "tags": "lake, trout"
    })
    temp_repo.save_memory({
        "title": "Baking Sourdough with Mom",
        "raw_notes": "Warm bread aroma filled the autumn kitchen.",
        "category": "Family Traditions",
        "people": "Mom",
        "tags": "baking, kitchen"
    })

    # Search by keyword
    lake_results = temp_repo.get_all_memories(search_query="trout")
    assert len(lake_results) == 1
    assert lake_results[0]["title"] == "Fishing at Pine Lake"

    # Filter by category
    traditions = temp_repo.get_all_memories(category="Family Traditions")
    assert len(traditions) == 1
    assert traditions[0]["title"] == "Baking Sourdough with Mom"

    # Filter by tag
    baking_tags = temp_repo.get_all_memories(tag="baking")
    assert len(baking_tags) == 1

def test_unique_categories_and_tags(temp_repo):
    temp_repo.save_memory({
        "title": "Memory A",
        "raw_notes": "Notes A",
        "category": "Childhood",
        "tags": "nostalgia, sunny"
    })
    temp_repo.save_memory({
        "title": "Memory B",
        "raw_notes": "Notes B",
        "category": "Travel & Adventures",
        "tags": "sunny, journey"
    })

    cats = temp_repo.get_unique_categories()
    assert "Childhood" in cats
    assert "Travel & Adventures" in cats

    tags = temp_repo.get_unique_tags()
    assert "nostalgia" in tags
    assert "sunny" in tags
    assert "journey" in tags

def test_remembrance_profiles_crud(temp_repo):
    prof_id = temp_repo.save_remembrance_profile({
        "honoree_name": "Eleanor Rigby",
        "dates": "1940 - 2020",
        "sayings": "Keep smiling through",
        "traditions": "Sunday roast",
        "compiled_tribute": "# In Memory of Eleanor"
    })
    assert prof_id > 0

    profiles = temp_repo.get_all_remembrance_profiles()
    assert len(profiles) == 1
    assert profiles[0]["honoree_name"] == "Eleanor Rigby"

    del_res = temp_repo.delete_remembrance_profile(prof_id)
    assert del_res is True
    assert len(temp_repo.get_all_remembrance_profiles()) == 0

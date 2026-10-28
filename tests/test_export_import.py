import pytest
import tempfile
import os
import json
from services.memory_repository import MemoryRepository
from services.export_service import ExportService

@pytest.fixture
def repo_and_exporter():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    repo = MemoryRepository(db_path)
    exporter = ExportService(repo)
    yield repo, exporter
    if os.path.exists(db_path):
        os.remove(db_path)

def test_export_memory_to_markdown_and_txt(repo_and_exporter):
    repo, exporter = repo_and_exporter
    mem_id = repo.save_memory({
        "title": "Autumn Harvest Festival",
        "raw_notes": "We picked crisp red apples at the local orchard.",
        "enhanced_story": "The crisp October breeze swept across the orchard as we gathered baskets of apples.",
        "category": "Celebrations & Milestones",
        "approximate_date": "October 2005",
        "people": "Mom, Dad, Sis",
        "tags": "apples, autumn"
    })

    md_output = exporter.export_memory_to_markdown(mem_id)
    assert "# Autumn Harvest Festival" in md_output
    assert "The crisp October breeze" in md_output
    assert "Mom, Dad, Sis" in md_output

    txt_output = exporter.export_memory_to_txt(mem_id)
    assert "AUTUMN HARVEST FESTIVAL" in txt_output
    assert "PRESERVED STORY:" in txt_output

def test_json_backup_export_and_import(repo_and_exporter):
    repo, exporter = repo_and_exporter
    repo.save_memory({
        "title": "First Bicycle Ride",
        "raw_notes": "Father let go of the seat on Maple Street.",
        "category": "Childhood"
    })
    repo.save_remembrance_profile({
        "honoree_name": "Arthur Pendelton",
        "dates": "1920 - 2005",
        "compiled_tribute": "A gentle grandfather."
    })

    json_backup = exporter.export_all_to_json()
    assert "First Bicycle Ride" in json_backup
    assert "Arthur Pendelton" in json_backup

    # Test importing back into a clean second database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf2:
        db2_path = tf2.name
    repo2 = MemoryRepository(db2_path)
    exporter2 = ExportService(repo2)

    ok, msg, count = exporter2.validate_and_import_json(json_backup)
    assert ok is True
    assert count == 1
    imported_mems = repo2.get_all_memories()
    assert len(imported_mems) == 1
    assert imported_mems[0]["title"] == "First Bicycle Ride"
    imported_profs = repo2.get_all_remembrance_profiles()
    assert len(imported_profs) == 1
    assert imported_profs[0]["honoree_name"] == "Arthur Pendelton"

    if os.path.exists(db2_path):
        os.remove(db2_path)

def test_invalid_json_import(repo_and_exporter):
    repo, exporter = repo_and_exporter
    ok, msg, count = exporter.validate_and_import_json("INVALID NOT JSON {{{")
    assert ok is False
    assert "Invalid JSON" in msg

    ok, msg, count = exporter.validate_and_import_json(json.dumps(["not a dict root"]))
    assert ok is False
    assert "dictionary object" in msg

    ok, msg, count = exporter.validate_and_import_json(json.dumps({"some_key": "some_value"}))
    assert ok is False
    assert "missing 'memories'" in msg

def test_no_silent_overwrite_duplicate_protection(repo_and_exporter):
    repo, exporter = repo_and_exporter
    repo.save_memory({
        "title": "Holiday Carols",
        "raw_notes": "Singing in the snow outside the chapel.",
        "category": "Celebrations & Milestones"
    })
    json_backup = exporter.export_all_to_json()

    # Import back with skip_duplicates=True
    ok, msg, count = exporter.validate_and_import_json(json_backup, skip_duplicates=True)
    assert ok is True
    assert count == 0  # Duplicate skipped

    all_mems = repo.get_all_memories()
    assert len(all_mems) == 1

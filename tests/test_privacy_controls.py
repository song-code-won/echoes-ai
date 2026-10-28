import pytest
import tempfile
import os
from services.memory_repository import MemoryRepository

@pytest.fixture
def repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    r = MemoryRepository(db_path)
    yield r
    if os.path.exists(db_path):
        os.remove(db_path)

def test_delete_all_requires_confirmation(repo):
    repo.save_memory({
        "title": "Secret Recipe",
        "raw_notes": "A pinch of nutmeg in the custard.",
        "category": "Family Traditions"
    })
    assert len(repo.get_all_memories()) == 1

    # Attempt deletion without explicit confirmation parameter
    res = repo.delete_all_memories(confirmation=False)
    assert res is False
    assert len(repo.get_all_memories()) == 1

    # Execute deletion with explicit confirmation
    res_confirmed = repo.delete_all_memories(confirmation=True)
    assert res_confirmed is True
    assert len(repo.get_all_memories()) == 0

def test_single_memory_deletion(repo):
    id1 = repo.save_memory({"title": "One", "raw_notes": "Note 1", "category": "General"})
    id2 = repo.save_memory({"title": "Two", "raw_notes": "Note 2", "category": "General"})

    assert len(repo.get_all_memories()) == 2
    repo.delete_memory(id1)

    remaining = repo.get_all_memories()
    assert len(remaining) == 1
    assert remaining[0]["id"] == id2

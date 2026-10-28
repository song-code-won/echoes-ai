import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from contextlib import contextmanager

class MemoryRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    raw_notes TEXT NOT NULL,
                    enhanced_story TEXT,
                    approximate_date TEXT,
                    people TEXT,
                    category TEXT NOT NULL,
                    tags TEXT,
                    style_used TEXT,
                    interview_qa TEXT,
                    is_remembrance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remembrance_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    honoree_name TEXT NOT NULL,
                    dates TEXT,
                    sayings TEXT,
                    traditions TEXT,
                    compiled_tribute TEXT,
                    linked_memory_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_memory(self, memory_data: Dict[str, Any]) -> int:
        now = datetime.utcnow().isoformat()
        tags = memory_data.get("tags", "")
        if isinstance(tags, list):
            tags = ", ".join(tags)
            
        interview_qa = memory_data.get("interview_qa", "")
        if isinstance(interview_qa, (list, dict)):
            interview_qa = json.dumps(interview_qa)

        with self._connection() as conn:
            cursor = conn.cursor()
            if "id" in memory_data and memory_data["id"]:
                cursor.execute("""
                    UPDATE memories
                    SET title = ?,
                        raw_notes = ?,
                        enhanced_story = ?,
                        approximate_date = ?,
                        people = ?,
                        category = ?,
                        tags = ?,
                        style_used = ?,
                        interview_qa = ?,
                        is_remembrance = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    memory_data.get("title", "Untitled Memory").strip(),
                    memory_data.get("raw_notes", "").strip(),
                    memory_data.get("enhanced_story", ""),
                    memory_data.get("approximate_date", ""),
                    memory_data.get("people", ""),
                    memory_data.get("category", "General"),
                    tags,
                    memory_data.get("style_used", ""),
                    interview_qa,
                    1 if memory_data.get("is_remembrance") else 0,
                    now,
                    memory_data["id"]
                ))
                conn.commit()
                return int(memory_data["id"])
            else:
                cursor.execute("""
                    INSERT INTO memories (
                        title, raw_notes, enhanced_story, approximate_date,
                        people, category, tags, style_used, interview_qa, is_remembrance,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_data.get("title", "Untitled Memory").strip(),
                    memory_data.get("raw_notes", "").strip(),
                    memory_data.get("enhanced_story", ""),
                    memory_data.get("approximate_date", ""),
                    memory_data.get("people", ""),
                    memory_data.get("category", "General"),
                    tags,
                    memory_data.get("style_used", ""),
                    interview_qa,
                    1 if memory_data.get("is_remembrance") else 0,
                    now,
                    now
                ))
                conn.commit()
                return cursor.lastrowid

    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_memories(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        tag: Optional[str] = None,
        remembrance_only: bool = False
    ) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM memories WHERE 1=1"
            params: List[Any] = []

            if category and category != "All":
                query += " AND category = ?"
                params.append(category)

            if search_query:
                query += " AND (title LIKE ? OR raw_notes LIKE ? OR enhanced_story LIKE ? OR people LIKE ?)"
                wildcard = f"%{search_query.strip()}%"
                params.extend([wildcard, wildcard, wildcard, wildcard])

            if tag:
                query += " AND tags LIKE ?"
                params.append(f"%{tag.strip()}%")

            if remembrance_only:
                query += " AND is_remembrance = 1"

            query += " ORDER BY updated_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_memory(self, memory_id: int) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def delete_all_memories(self, confirmation: bool = False) -> bool:
        if not confirmation:
            return False
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories")
            cursor.execute("DELETE FROM remembrance_profiles")
            conn.commit()
            return True

    def get_unique_categories(self) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM memories WHERE category IS NOT NULL AND category != ''")
            return [row["category"] for row in cursor.fetchall()]

    def get_unique_tags(self) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tags FROM memories WHERE tags IS NOT NULL AND tags != ''")
            tags_set = set()
            for row in cursor.fetchall():
                parts = [t.strip() for t in row["tags"].split(",") if t.strip()]
                tags_set.update(parts)
            return sorted(list(tags_set))

    # Remembrance Profile CRUD
    def save_remembrance_profile(self, profile_data: Dict[str, Any]) -> int:
        now = datetime.utcnow().isoformat()
        with self._connection() as conn:
            cursor = conn.cursor()
            if "id" in profile_data and profile_data["id"]:
                cursor.execute("""
                    UPDATE remembrance_profiles
                    SET honoree_name = ?,
                        dates = ?,
                        sayings = ?,
                        traditions = ?,
                        compiled_tribute = ?,
                        linked_memory_ids = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    profile_data.get("honoree_name", "").strip(),
                    profile_data.get("dates", "").strip(),
                    profile_data.get("sayings", "").strip(),
                    profile_data.get("traditions", "").strip(),
                    profile_data.get("compiled_tribute", "").strip(),
                    profile_data.get("linked_memory_ids", ""),
                    now,
                    profile_data["id"]
                ))
                conn.commit()
                return int(profile_data["id"])
            else:
                cursor.execute("""
                    INSERT INTO remembrance_profiles (
                        honoree_name, dates, sayings, traditions,
                        compiled_tribute, linked_memory_ids, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_data.get("honoree_name", "").strip(),
                    profile_data.get("dates", "").strip(),
                    profile_data.get("sayings", "").strip(),
                    profile_data.get("traditions", "").strip(),
                    profile_data.get("compiled_tribute", "").strip(),
                    profile_data.get("linked_memory_ids", ""),
                    now,
                    now
                ))
                conn.commit()
                return cursor.lastrowid

    def get_all_remembrance_profiles(self) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM remembrance_profiles ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_remembrance_profile(self, profile_id: int) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM remembrance_profiles WHERE id = ?", (profile_id,))
            conn.commit()
            return cursor.rowcount > 0

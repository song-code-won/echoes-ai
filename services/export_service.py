import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from services.memory_repository import MemoryRepository

class ExportService:
    def __init__(self, repository: MemoryRepository):
        self.repo = repository

    def export_memory_to_markdown(self, memory_id: int) -> str:
        mem = self.repo.get_memory(memory_id)
        if not mem:
            return ""

        date_str = mem.get("approximate_date") or "Undated"
        people = mem.get("people") or "Not recorded"
        tags = mem.get("tags") or "None"
        category = mem.get("category") or "General"
        style = mem.get("style_used") or "Standard"

        md = [
            f"# {mem.get('title', 'Untitled Memory')}",
            "",
            f"**Category:** {category} | **Date:** {date_str}",
            f"**People:** {people} | **Tags:** {tags}",
            f"**Story Style:** {style}",
            "",
            "---",
            "",
            "## Preserved Story",
            mem.get("enhanced_story") or "*No enhanced narrative saved yet.*",
            "",
            "---",
            "",
            "## Original Raw Notes",
            "> " + (mem.get("raw_notes") or "").replace("\n", "\n> "),
            ""
        ]

        # Interview questions if present
        qa_raw = mem.get("interview_qa")
        if qa_raw:
            try:
                qa_data = json.loads(qa_raw) if isinstance(qa_raw, str) else qa_raw
                if isinstance(qa_data, list) and qa_data:
                    md.extend(["", "## Reflection Questions & Answers"])
                    for item in qa_data:
                        if isinstance(item, dict):
                            md.append(f"- **Q: {item.get('q', '')}**")
                            if item.get("a"):
                                md.append(f"  *A: {item.get('a')}*")
                        elif isinstance(item, str):
                            md.append(f"- *{item}*")
            except Exception:
                pass

        md.extend([
            "",
            "---",
            f"*Preserved locally with Echoes AI on {datetime.utcnow().strftime('%Y-%m-%d')}*"
        ])
        return "\n".join(md)

    def export_memory_to_txt(self, memory_id: int) -> str:
        mem = self.repo.get_memory(memory_id)
        if not mem:
            return ""

        title = mem.get("title", "Untitled Memory")
        date_str = mem.get("approximate_date") or "Undated"
        category = mem.get("category") or "General"
        people = mem.get("people") or "Not recorded"

        txt = [
            f"============================================================",
            f"{title.upper()}",
            f"============================================================",
            f"Category : {category}",
            f"Date     : {date_str}",
            f"People   : {people}",
            f"------------------------------------------------------------",
            "PRESERVED STORY:",
            mem.get("enhanced_story") or "[No enhanced narrative saved]",
            f"------------------------------------------------------------",
            "ORIGINAL NOTES:",
            mem.get("raw_notes") or "[Empty]",
            f"============================================================",
            f"Preserved with Echoes AI (Local & Private)"
        ]
        return "\n".join(txt)

    def export_all_to_json(self) -> str:
        """
        Creates a structured, verifiable JSON backup of all memories and remembrance profiles.
        """
        memories = self.repo.get_all_memories()
        profiles = self.repo.get_all_remembrance_profiles()

        backup_payload = {
            "app": "Echoes AI",
            "version": "1.0.0",
            "exported_at": datetime.utcnow().isoformat(),
            "memories_count": len(memories),
            "remembrance_count": len(profiles),
            "memories": memories,
            "remembrance_profiles": profiles
        }
        return json.dumps(backup_payload, indent=2, ensure_ascii=False)

    def validate_and_import_json(
        self,
        json_content: str,
        skip_duplicates: bool = True
    ) -> Tuple[bool, str, int]:
        """
        Validates JSON backup format and safely imports memories without silent overwriting.
        Returns: (success: bool, status_message: str, imported_count: int)
        """
        try:
            data = json.loads(json_content)
        except Exception as e:
            return False, f"Invalid JSON format: {str(e)}", 0

        if not isinstance(data, dict):
            return False, "JSON root must be a dictionary object.", 0

        # Check required fields
        if "memories" not in data and "remembrance_profiles" not in data:
            return False, "Invalid Echoes AI backup: missing 'memories' or 'remembrance_profiles' list.", 0

        memories = data.get("memories", [])
        if not isinstance(memories, list):
            return False, "Backup field 'memories' must be a list.", 0

        imported_count = 0
        existing_memories = self.repo.get_all_memories()
        existing_signatures = {
            (m.get("title", "").strip().lower(), m.get("raw_notes", "").strip().lower())
            for m in existing_memories
        }

        for mem in memories:
            if not isinstance(mem, dict):
                continue

            raw_notes = mem.get("raw_notes", "").strip()
            title = mem.get("title", "").strip() or "Untitled Imported Memory"

            if not raw_notes and not mem.get("enhanced_story"):
                continue  # skip invalid empty entries

            sig = (title.lower(), raw_notes.lower())
            if skip_duplicates and sig in existing_signatures:
                continue

            # Strip existing ID so it creates fresh non-conflicting records
            new_record = dict(mem)
            if "id" in new_record:
                del new_record["id"]

            self.repo.save_memory(new_record)
            existing_signatures.add(sig)
            imported_count += 1

        # Also import remembrance profiles if available
        profiles = data.get("remembrance_profiles", [])
        profile_count = 0
        if isinstance(profiles, list):
            existing_profiles = self.repo.get_all_remembrance_profiles()
            existing_prof_names = {p.get("honoree_name", "").strip().lower() for p in existing_profiles}
            for prof in profiles:
                if not isinstance(prof, dict):
                    continue
                name = prof.get("honoree_name", "").strip()
                if not name:
                    continue
                if skip_duplicates and name.lower() in existing_prof_names:
                    continue
                new_prof = dict(prof)
                if "id" in new_prof:
                    del new_prof["id"]
                self.repo.save_remembrance_profile(new_prof)
                profile_count += 1

        msg = f"Successfully imported {imported_count} memories and {profile_count} remembrance profiles."
        return True, msg, imported_count

from pathlib import Path
from typing import Dict, Any, Optional
from services.ollama_client import OllamaClient
import config

class StoryWriter:
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_file = config.BASE_DIR / "prompts" / "story_enhancement.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        # Fallback template if file is missing
        return (
            "Rewrite the following personal memory notes into a warm, factual narrative "
            "preserving all names and details without hallucinating facts: {raw_notes}"
        )

    def enhance_story(
        self,
        raw_notes: str,
        title: str = "Untitled Memory",
        approximate_date: str = "",
        people: str = "",
        category: str = "General",
        tags: str = "",
        style: str = "warm",
        model: str = config.DEFAULT_MODEL
    ) -> Dict[str, Any]:
        """
        Enhances rough user notes into a polished personal story.
        Preserves all facts and respects user constraints.
        """
        if not raw_notes or not raw_notes.strip():
            return {
                "success": False,
                "story": "",
                "error": "Cannot enhance memory: Raw notes are empty."
            }

        style_info = config.STORY_STYLES.get(style, config.STORY_STYLES["warm"])
        style_description = f"{style_info['label']}: {style_info['description']}"

        prompt = self.prompt_template.format(
            title=title or "Untitled Memory",
            approximate_date=approximate_date or "Not specified",
            people=people or "Not specified",
            category=category or "General",
            tags=tags or "None",
            style_description=style_description,
            raw_notes=raw_notes.strip()
        )

        res = self.ollama.generate(
            prompt=prompt,
            model=model,
            system="You are an empathetic, faithful biographer preserving real personal memories. Never invent deceased persons, false tragedies, or claim psychic contact.",
            temperature=0.6,
            max_tokens=1500
        )

        if not res["success"]:
            return {
                "success": False,
                "story": "",
                "error": res["error"]
            }

        story = res["text"].strip()
        return {
            "success": True,
            "story": story,
            "error": None
        }

    def suggest_title(
        self,
        raw_notes: str,
        category: str = "General",
        model: str = config.DEFAULT_MODEL
    ) -> Dict[str, Any]:
        """
        Suggests a short, evocative title for a memory.
        """
        if not raw_notes or not raw_notes.strip():
            return {"success": False, "title": "", "error": "No notes provided."}

        prompt = (
            f"Based on the following memory notes, suggest 1 concise, evocative title (under 7 words). "
            f"Output ONLY the title string, without quotes or explanation.\n\n"
            f"Category: {category}\nNotes:\n{raw_notes.strip()}"
        )

        res = self.ollama.generate(
            prompt=prompt,
            model=model,
            temperature=0.4,
            max_tokens=30
        )

        if res["success"]:
            title = res["text"].strip().strip('"').strip("'")
            return {"success": True, "title": title, "error": None}
        return {"success": False, "title": "", "error": res["error"]}

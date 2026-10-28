from pathlib import Path
from typing import Dict, Any, List, Optional
from services.ollama_client import OllamaClient
import config

class RemembranceBuilder:
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_file = config.BASE_DIR / "prompts" / "remembrance_page.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return (
            "Create a respectful tribute for {name} ({dates}) based on:\n"
            "Stories: {stories}\nSayings: {sayings}\nTraditions: {traditions}"
        )

    def draft_tribute(
        self,
        name: str,
        dates: str = "",
        stories: str = "",
        sayings: str = "",
        traditions: str = "",
        notes: str = "",
        model: str = config.DEFAULT_MODEL
    ) -> Dict[str, Any]:
        """
        Drafts a respectful memorial tribute page using user-provided details.
        Never impersonates or pretends to contact the deceased.
        """
        if not name or not name.strip():
            return {
                "success": False,
                "tribute": "",
                "error": "Honoree name is required."
            }

        prompt = self.prompt_template.format(
            name=name.strip(),
            dates=dates or "Undated",
            stories=stories.strip() or "No specific stories provided.",
            sayings=sayings.strip() or "None listed.",
            traditions=traditions.strip() or "None listed.",
            notes=notes.strip() or "None."
        )

        res = self.ollama.generate(
            prompt=prompt,
            model=model,
            system=(
                "You are a compassionate memorial writer. Honor the real person with dignity. "
                "Never simulate conversations with the deceased or pretend to channel their voice."
            ),
            temperature=0.5,
            max_tokens=1800
        )

        if not res["success"]:
            # Provide an elegant deterministic template if local model is offline
            fallback_markdown = self._generate_static_tribute(
                name=name,
                dates=dates,
                stories=stories,
                sayings=sayings,
                traditions=traditions,
                notes=notes
            )
            return {
                "success": True,
                "tribute": fallback_markdown,
                "is_fallback": True,
                "error": f"Generated using offline template ({res['error']})"
            }

        return {
            "success": True,
            "tribute": res["text"].strip(),
            "is_fallback": False,
            "error": None
        }

    def _generate_static_tribute(
        self,
        name: str,
        dates: str,
        stories: str,
        sayings: str,
        traditions: str,
        notes: str
    ) -> str:
        date_str = f" *({dates})*" if dates else ""
        out = [
            f"# In Loving Memory of {name}{date_str}",
            "",
            "> *\"Every memory deserves to live on.\"*",
            "",
            "## Honoring a Cherished Life",
            f"We hold dear the laughter, wisdom, and quiet moments shared with {name}. "
            "Though time passes, the love and lessons they gifted to our lives remain forever steadfast in our hearts.",
            ""
        ]

        if sayings.strip():
            out.extend([
                "## Words of Wisdom & Favorite Sayings",
                sayings.strip(),
                ""
            ])

        if traditions.strip():
            out.extend([
                "## Traditions & Enduring Legacy",
                traditions.strip(),
                ""
            ])

        if stories.strip():
            out.extend([
                "## Stories We Keep Close",
                stories.strip(),
                ""
            ])

        if notes.strip():
            out.extend([
                "## Personal Reflection",
                notes.strip(),
                ""
            ])

        out.extend([
            "---",
            f"*Preserved with care in Echoes AI — a private, local-first memory journal.*"
        ])
        return "\n".join(out)

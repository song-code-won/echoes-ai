import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from services.ollama_client import OllamaClient
import config

class InterviewQuestionsGenerator:
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_file = config.BASE_DIR / "prompts" / "interview_questions.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return (
            "Generate 5 gentle follow-up questions to help expand this personal memory:\n"
            "Title: {title}\nCategory: {category}\nNotes: {raw_notes}"
        )

    def generate_questions(
        self,
        raw_notes: str,
        title: str = "Untitled Memory",
        category: str = "General",
        people: str = "",
        model: str = config.DEFAULT_MODEL
    ) -> Dict[str, Any]:
        """
        Generates 5 gentle, respectful oral history interview questions.
        """
        if not raw_notes or not raw_notes.strip():
            return {
                "success": False,
                "questions": [],
                "error": "Cannot generate questions: Memory notes are empty."
            }

        prompt = self.prompt_template.format(
            title=title or "Untitled Memory",
            category=category or "General",
            people=people or "Not specified",
            raw_notes=raw_notes.strip()
        )

        res = self.ollama.generate(
            prompt=prompt,
            model=model,
            system="You are a gentle, respectful personal oral historian. Ask tender, non-intrusive questions.",
            temperature=0.5,
            max_tokens=600
        )

        if not res["success"]:
            # Provide sensible fallback default questions if offline / Ollama down
            fallback_questions = [
                "What sensory detail (a sound, smell, or color) stands out most clearly when you picture this?",
                "Who was there with you, and how did their presence make you feel?",
                "Was there a small ritual, object, or tradition tied to this particular moment?",
                "What is something someone said or laughed about during this event?",
                "Why has this memory stayed in your heart over all these years?"
            ]
            return {
                "success": False,
                "questions": fallback_questions,
                "error": f"{res['error']} (Showing gentle default questions as offline guide)"
            }

        parsed_questions = self._parse_questions(res["text"])
        if not parsed_questions:
            parsed_questions = [
                "What sensory detail stands out most clearly when you picture this moment?",
                "What conversation or expression do you remember most warmly?",
                "Was there a family tradition or habit connected with this event?",
                "What feelings come back to you when you reflect on this time?",
                "What lesson or warmth from this memory would you like future generations to know?"
            ]

        return {
            "success": True,
            "questions": parsed_questions[:5],
            "error": None
        }

    def _parse_questions(self, raw_text: str) -> List[str]:
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        questions = []
        for line in lines:
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            cleaned = cleaned.strip('"').strip("'")
            if cleaned.endswith("?") or len(cleaned) > 15:
                questions.append(cleaned)
        return questions

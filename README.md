# 📖 Echoes AI — A Private, Local-First Memory Journal

> *“Every memory deserves to live on.”*

[![License: MIT](https://img.shields.io/badge/License-MIT-burgundy.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit: 1.35+](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![Ollama: Local](https://img.shields.io/badge/Ollama-Local%20Inference-orange.svg)](https://ollama.com/)
[![Tests: 20 passed](https://img.shields.io/badge/Tests-20%20passed-green.svg)](tests/)

---

## 🌟 Project Motivation

Family stories, childhood traditions, and the quiet wisdom of loved ones are fragile. Too often, they slip away because we only have scattered notes, half-remembered fragments, or lack the time to craft them into a lasting narrative.

Yet handing personal, emotionally intimate memories over to cloud-based AI services comes at an unacceptable privacy cost: personal grief and family history sent over third-party networks, analyzed, and ingested into corporate training models. Furthermore, many commercial tools cross ethical lines by promising creepy digital avatars or claiming to "talk to the dead."

**Echoes AI** was created for the **Hacktoberfest 2026 DEV Open-Source AI Challenge, Week 4: “Ghost in the Machine”**. It is a respectful, quiet digital sanctuary that preserves true personal stories entirely on your own computer.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User([User / Storyteller]) -->|Warm Scrapbook UI| Streamlit[Streamlit Frontend (app.py)]
    
    subgraph UI_Modules ["Interface Modules"]
        Streamlit --> Editor[Memory Editor & Interview Assistant]
        Streamlit --> Library[Memory Library & Search]
        Streamlit --> Remembrance[Remembrance Tribute Builder]
        Streamlit --> Backup[Export & JSON Restore]
        Streamlit --> Privacy[Privacy Controls & Wipe]
    end

    subgraph Service_Core ["Modular Services"]
        Editor --> StoryWriter[StoryWriter]
        Editor --> InterviewGen[InterviewQuestionsGenerator]
        Remembrance --> RemBuilder[RemembranceBuilder]
        Backup --> ExportService[ExportService]
        Library --> MemoryRepo[MemoryRepository]
        Privacy --> MemoryRepo
    end

    subgraph Local_Storage ["Local-Only Persistence"]
        MemoryRepo --> SQLite[(SQLite: echoes_memories.db)]
        ExportService --> SQLite
        ExportService --> Files[Markdown / TXT / JSON Files]
    end

    subgraph Local_AI ["Local Open-Weight AI (Ollama)"]
        StoryWriter --> OllamaClient[Ollama Client]
        InterviewGen --> OllamaClient
        RemBuilder --> OllamaClient
        OllamaClient -->|HTTP 127.0.0.1:11434| OllamaDaemon[Ollama Service]
        OllamaDaemon --> QwenModel[Qwen 2.5 (Apache 2.0)]
    end
```

---

## ✨ Core Features

### 1. Memory Editor & Raw Preservation
- Record rough memory fragments, approximate dates, people/relationships, categories, and tags.
- Option to save original raw notes immediately without AI transformation.
- Suggest evocative memory titles using local intelligence.

### 2. AI Story Enhancement (With Style Selection)
- Weaves rough notes into polished, heartfelt narratives.
- Three carefully tuned voices:
  - **Warm & Heartfelt**: Emphasizes emotional warmth, familial tenderness, and bonding.
  - **Simple & Conversational**: Natural, easy to read aloud as if sharing over tea.
  - **Nostalgic & Reflective**: Sensory-rich, lingering on sights, sounds, scents, and time.
- **Factual Fidelity**: Strictly preserves user facts, names, and relationships without hallucinating false history or unmentioned events.
- Full user review and editing before saving.

### 3. Gentle Oral-History Interview Assistant
- Generates 5 gentle, open-ended follow-up questions tailored to your notes.
- Prompts for sensory details, memorable sayings, and subtle traditions.
- Fully non-intrusive and optional with a one-click button to append reflection answers into your notes.

### 4. Personal Memory Library (SQLite)
- Browse saved stories with category and tag filters.
- Real-time search across titles, people, and narrative text.
- Side-by-side view of the original raw notes and the polished story.
- Safe entry editing and confirmation-protected deletion.

### 5. Personal Remembrance Page
- Calm, respectful memorial tributes honoring loved ones.
- Incorporates life dates, favorite sayings, important traditions, and linked stories.
- **Anti-Necromancy Guarantee**: Rejects simulated consciousness or psychic claims; focuses purely on honoring real legacies.

### 6. Export, Backup & Data Sovereignty
- Single-click export of any memory to clean **Markdown (.md)** or plain **TXT**.
- Full-database **JSON backup** and validated **JSON restore** with duplicate detection.
- Complete local database wipe with explicit confirmation.

---

## 🎨 Visual Design

Echoes AI is crafted with a gentle scrapbook aesthetic:
- **Warm Cream Background (`#FAF7F2`)** reminiscent of aged journal pages.
- **Muted Burgundy Accents (`#6B1D2F`)** providing reverent, grounding contrast.
- **Subtle Marigold Touches (`#D9822B`)** evoking autumn leaves and warm hearths.
- **Serif Typography (`Crimson Pro`)** for headings and tributes paired with clean body text (`Inter`).

---

## 🤖 Recommended Open-Weight Model

Echoes AI runs with any model supported by Ollama. We strongly recommend **Qwen 2.5:3b** or **Qwen 2.5:7b**:
- **Model**: `qwen2.5:3b`
- **License**: Apache 2.0 (Open-source, commercial-friendly)
- **Hardware Requirements**:
  - RAM: 8 GB minimum (16 GB recommended)
  - VRAM: 3.5 GB (runs smoothly on CPU or consumer GPUs)
  - Disk: ~2.0 GB download
- **Alternative Supported Models**: `llama3.2:3b`, `mistral:7b`, `qwen2.5:1.5b`.

---

## 🚀 Quickstart Guide

### Prerequisites
1. **Python 3.10+**
2. **Ollama** installed on your system ([Download Ollama](https://ollama.com/download))

### Step 1: Install Ollama & Pull Recommended Model
```bash
# Pull the lightweight, high-performance Qwen 2.5 3B model
ollama pull qwen2.5:3b

# Ensure Ollama daemon is running
ollama serve
```

### Step 2: Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-username/echoes-ai.git
cd echoes-ai

# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Run Echoes AI
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 📴 Offline Operation

Echoes AI is designed to work completely offline:
- Once the Python dependencies and the Ollama model are downloaded, **no internet connection is required**.
- If Ollama is temporarily stopped, Echoes AI gracefully falls back to deterministic tribute templates and gentle offline interview prompts.
- All SQLite database transactions and file exports occur strictly on your local disk.

---

## 🔒 Privacy & Limitations Disclosure

- **Unencrypted Local Storage**: Stories are stored in an unencrypted SQLite file at `data/echoes_memories.db`. They rely on your operating system's local user account permissions. If full encryption-at-rest is required, run Echoes AI on an encrypted drive volume (e.g., BitLocker, LUKS, or FileVault).
- **Untrusted Input Protection**: Imported JSON backup files are strictly validated before parsing.
- **No Telemetry**: No user analytics, metrics, or logs are transmitted off your machine.

---

## 🧪 Automated Testing

Echoes AI includes a test suite covering repository operations, JSON import/export validation, and mocked AI inference.

Run the test suite:
```bash
pytest tests/
```

### Test Results
```
tests\test_export_import.py ....                                         [ 20%]
tests\test_memory_repository.py ......                                   [ 50%]
tests\test_privacy_controls.py ..                                        [ 60%]
tests\test_story_writer.py ........                                      [100%]

============================= 20 passed in 0.52s ==============================
```

---

## 📝 Sample Fictional Demonstration Memory

```
Title: Sunday Lemonade on the Screened Porch
Category: Childhood
Approximate Date: Summer 1994
People: Grandmother Clara, Cousin Leo
Tags: porch, lemonade, summer, wooden swing

Raw Notes:
Hot July afternoon in Ohio. Cicadas loud in the maple trees. Grandma Clara squeezed lemons into a cracked yellow pitcher. Used real cane sugar and fresh spearmint leaves from behind the garden shed. Cousin Leo and I took turns on the creaky cedar swing. Grandma told us that patience makes sweet lemonade and hurried lemonade always stays sour.
```

---

## 📂 Repository Structure

```
echoes-ai/
├── app.py                         # Streamlit application entry point
├── config.py                      # Global configurations, categories & paths
├── requirements.txt               # Python package requirements
├── README.md                      # Comprehensive user & developer guide
├── LICENSE                        # MIT Open Source License
├── .gitignore                     # Git exclusions (caches, dbs, backups)
├── services/
│   ├── memory_repository.py       # Thread-safe SQLite database manager
│   ├── ollama_client.py           # Safe local Ollama REST client
│   ├── story_writer.py            # AI narrative enhancement service
│   ├── interview_questions.py     # Gentle oral history prompt generator
│   ├── remembrance_builder.py     # Memorial tribute synthesizer
│   └── export_service.py          # Markdown, TXT & JSON backup service
├── prompts/
│   ├── story_enhancement.txt      # Structured prompt for memory rewriting
│   ├── interview_questions.txt    # Structured prompt for interview assistant
│   └── remembrance_page.txt       # Structured prompt for remembrance tributes
├── tests/
│   ├── test_memory_repository.py  # Tests for SQLite CRUD, search & filters
│   ├── test_story_writer.py       # Tests for narrative & interview generation
│   ├── test_export_import.py      # Tests for JSON backup integrity & Markdown
│   └── test_privacy_controls.py   # Tests for data deletion & safety confirmations
└── docs/
    ├── architecture.md            # Detailed system design & Mermaid diagrams
    └── dev_community_post.md      # Draft article for DEV Community challenge
```

---

## 🤝 Contributing & Hacktoberfest

Contributions are welcome! Please adhere to our ethical guidelines:
1. Ensure all features maintain 100% local-first data isolation.
2. Never introduce paid closed-cloud dependencies as defaults.
3. Write automated unit tests for new service methods.
4. Open a pull request or issue on GitHub.

---

## 📜 License & Acknowledgments

- **License**: Released under the [MIT License](LICENSE).
- **Challenge**: Built for the Hacktoberfest 2026 DEV Open-Source AI Challenge (Week 4: “Ghost in the Machine”).
- **Model Credits**: Qwen 2.5 by Alibaba Cloud (Apache 2.0).
- Special thanks to the open-source community for Streamlit, Ollama, and SQLite.

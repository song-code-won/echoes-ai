# Echoes AI System Architecture

## Overview
**Echoes AI** is an open-source, local-first memory journal designed for Hacktoberfest 2026: *Ghost in the Machine*. It provides a quiet, respectful sanctuary to preserve personal stories, family traditions, and memories of loved ones using local AI (Ollama + Qwen2.5) without transmitting personal memories over the internet.

## High-Level Architecture Diagram

```mermaid
flowchart TD
    User([User / Family Biographer]) -->|Interactive UI| Streamlit[Streamlit App (app.py)]
    
    subgraph UI_Layer ["Presentation & UX Layer"]
        Streamlit --> Editor[Memory Editor]
        Streamlit --> Library[Memory Library]
        Streamlit --> Remembrance[Remembrance Builder]
        Streamlit --> ExportUI[Export & Backup]
        Streamlit --> PrivacyUI[Privacy & Settings]
    end

    subgraph Service_Layer ["Application Services"]
        Editor --> StoryWriter[Story Writer Service]
        Editor --> InterviewGen[Interview Questions Generator]
        Remembrance --> RemBuilder[Remembrance Builder Service]
        ExportUI --> ExportService[Export Service]
        Library --> Repo[Memory Repository]
        PrivacyUI --> Repo
    end

    subgraph Storage_Layer ["Local Persistence (Zero-Cloud)"]
        Repo --> SQLite[(SQLite Local DB: echoes_memories.db)]
        ExportService --> SQLite
        ExportService --> JSONBackup[(JSON Backup / Markdown / TXT)]
    end

    subgraph Inference_Layer ["Local AI Inference (100% Offline)"]
        StoryWriter --> OllamaClient[Ollama Client]
        InterviewGen --> OllamaClient
        RemBuilder --> OllamaClient
        OllamaClient -->|HTTP localhost:11434| LocalOllama[Local Ollama Engine]
        LocalOllama --> Qwen[Open-Weight Qwen 2.5 LLM]
    end
```

## Component Breakdown

### 1. Presentation Layer (`app.py`)
- Custom CSS utilizing warm cream (`#FAF7F2`), muted burgundy (`#6B1D2F`), and subtle marigold accents (`#D9822B`).
- Tabbed memory preservation workflow: original notes input, oral history interview assistant, style-selectable AI story enhancement, and preview/editing.
- Dual-view Memory Library presenting original notes alongside AI-enhanced narratives.
- Remembrance tribute creator compiling traditions, wisdom, and life stories.

### 2. Service Layer
- **`MemoryRepository`**: Thread-safe SQLite abstraction managing memories, categories, tags, and remembrance profiles.
- **`OllamaClient`**: Safe HTTP client connecting to `http://127.0.0.1:11434`. Includes timeout protection, model status interrogation, and graceful error handling.
- **`StoryWriter`**: Transforms rough notes into structured narratives across 3 styles (Warm & Heartfelt, Simple & Conversational, Nostalgic & Reflective) without hallucinating unverified historical facts.
- **`InterviewQuestionsGenerator`**: Formulates 5 gentle oral history interview questions to elicit forgotten sensory and cultural details.
- **`RemembranceBuilder`**: Formats dignified tributes with deterministic offline fallback templates if Ollama is unavailable.
- **`ExportService`**: Exports entries to Markdown, plain text, and validated JSON backups with duplicate collision prevention.

### 3. Privacy & Security Principles
- **No Cloud Transmission**: Zero remote telemetry, tracking, or external API dependencies.
- **No Model Training**: Personal memories are processed locally in volatile memory and never used for training.
- **No Spiritual Claims**: Explicit ethical boundaries against simulating consciousness or claiming psychic communication with deceased persons.
- **Untrusted Input Protection**: Imported JSON payloads are strictly validated before insertion.

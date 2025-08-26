# **AI Podcast Agent — Build Plan**

## **1\) Objective & Constraints**

**Goal:** Automatically ingest new podcast episodes from a curated list of AI/tech shows, generate high‑quality summaries \+ highlights, and deliver a daily digest via Email and Slack, with a local chat agent for deeper Q\&A.

**Non-goals (MVP):** Long‑form transcript editing UI, multi‑language translation, speaker diarization beyond basic labels.

**Constraints/Preferences:**

* **Local-first** processing (download, ASR, summarization) using open models; optional cloud LLM fallback.  
* Runs on **Linux/macOS** with GPU optional (NVIDIA/CUDA) for speed.  
* Modular, extensible, and legally compliant.

---

## **2\) Inputs & Sources**

**Top 5 AI Podcasts to Ingest:**

1. **AI Today Podcast** — RSS  
2. **CEO AI Podcast** — RSS  
3. **Latent Space** — RSS  
4. **Practical AI** — RSS  
5. **The Cognitive Revolution** — RSS  
* **Metadata:** title, show, published date, duration, description, enclosure URL (MP3/MP4/AAC), episode link.

**Legal note:** Respect each show’s ToS. Prefer RSS enclosures. Avoid scraping behind paywalls. Use only for personal use; don’t redistribute transcripts verbatim.

---

## **3\) System Architecture (MVP)**

Scheduler (cron) ─┬─► Feed Fetcher ─► Episode Registry (SQLite)

                  │

                  ├─► Download Worker ─► Audio Store (/data/audio)

                  │

                  ├─► ASR Worker (Whisper) ─► Transcript Store (/data/transcripts)

                  │

                  ├─► Summarizer Worker (local LLM) ─► Summaries (/data/summaries)

                  │

                  └─► Digest Composer ─► Email (SMTP) \+ Slack Bot

                                              │

                                              └─► Chat Agent (RAG over transcripts & notes)

**Message bus:** Lightweight: SQLite job table \+ asyncio; or Celery \+ Redis for scale. **Storage:**

* `/data/db.sqlite` (episodes, runs, embeddings)  
* `/data/audio/{show}/{yyyy-mm-dd}-{slug}.mp3`  
* `/data/transcripts/{id}.jsonl` (segments \+ timestamps)  
* `/data/embeddings/{id}.faiss` (optional shared index)  
* `/data/summaries/{id}.md`

---

## **4\) Tech Choices (Local-first)**

* **Feed ingestion:** `feedparser`, `requests`.  
* **Downloader:** `yt-dlp` (for YouTube-only shows), `aiohttp` for direct enclosures.  
* **ASR:** OpenAI Whisper (`whisper.cpp` or `faster-whisper`) – `medium` or `large-v3` if GPU.  
* **LLM (local):** Llama 3.1 8B/70B, Qwen2, or Mistral via `llama.cpp`/`ollama`. Optional cloud: GPT‑4o/sonnet for upgrades.  
* **Embeddings:** `sentence-transformers` (e.g., `all-MiniLM-L6-v2`) or local E5.  
* **Vector store:** FAISS (in-process) or Chroma for simplicity.  
* **Orchestration:** Python `asyncio` tasks, or Celery \+ Redis (if you want retries \+ visibility).  
* **Email:** SMTP via `smtplib` or `resend` (if allowed). **Slack:** Slack Bot \+ Web API.  
* **Config:** `pydantic` \+ `.env`.  
* **Packaging:** Docker \+ docker-compose (optional). Makefile for dev.


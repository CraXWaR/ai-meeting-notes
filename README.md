# AI Meeting Notes

A FastAPI service for automatically generating meeting notes from transcripts using LLM (Groq / LangChain).

---

## Description

The service reads meeting transcripts from `.docx` / `.pdf` files, stores them in Supabase, and generates structured notes using Groq LLM.

---

## Project Structure
```
ai-meeting-notes/
├── app/
│   ├── main.py
│   ├── settings.py
│   ├── routers/
│   │   ├── meetings_router.py
│   │   └── notes_router.py
│   ├── services/
│   │   ├── database.py
│   │   ├── meeting_service.py
│   │   ├── notes_service.py
│   │   └── llm_service.py
│   ├── models/
│   │   ├── meetings_model.py
│   │   └── notes_model.py
│   ├── helpers/
│   │   ├── file_helpers.py
│   │   └── llm_helpers.py
│   └── validators/
│       └── validate_id.py
├── data/
├── .env
└── requirements.txt
```

---

## Installation & Setup
```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

Start the server:
```bash
python -m uvicorn app.main:app --reload
```

---

## Endpoints

### Ingest meetings from `data/` folder
```bash
curl -X POST http://localhost:8000/meetings
```

### Upload a meeting file
```bash
curl -X POST http://localhost:8000/meetings/upload \
  -F "file=@meeting.docx"
```

### Get all meetings
```bash
curl http://localhost:8000/meetings
```

### Get meeting by ID
```bash
curl http://localhost:8000/meetings/{meeting_id}
```

### Generate notes for a meeting
```bash
# Default (Groq)
curl -X POST http://localhost:8000/meetings/{meeting_id}/process

# With Mistral
curl -X POST "http://localhost:8000/meetings/{meeting_id}/process?llm=mistral"
```

### Generate notes for all meetings
```bash
curl -X POST http://localhost:8000/meetings/process-all
```

### Get notes for a meeting
```bash
curl http://localhost:8000/meetings/{meeting_id}/notes
```

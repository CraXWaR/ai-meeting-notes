import json

MAX_CHARS = 20000


def chunk_transcript(transcript):
    chunks = []
    while len(transcript) > MAX_CHARS:
        chunks.append(transcript[:MAX_CHARS])
        transcript = transcript[MAX_CHARS:]
    chunks.append(transcript)
    return chunks


def validate_notes(raw):
    try:
        notes = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
        notes = json.loads(cleaned)

    notes.setdefault("summary", "")
    notes.setdefault("action_items", [])
    notes.setdefault("decisions", [])
    notes.setdefault("key_takeaways", [])
    notes.setdefault("topics", [])
    notes.setdefault("next_steps", [])

    return notes


def merge_notes(all_notes):
    merged = {
        "summary": " ".join([n["summary"] for n in all_notes]),
        "action_items": [],
        "decisions": [],
        "key_takeaways": [],
        "topics": [],
        "next_steps": []
    }
    for note in all_notes:
        merged["action_items"].extend(note["action_items"])
        merged["decisions"].extend(note["decisions"])
        merged["key_takeaways"].extend(note["key_takeaways"])
        merged["topics"].extend(note["topics"])
        merged["next_steps"].extend(note["next_steps"])
    return merged


def log_retry(retry_state):
    print(f"Rate limit hit, retrying in {retry_state.next_action.sleep} seconds...")
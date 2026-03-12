import uuid
from app.services.database import supabase
from app.services.llm_service import llm_client
from app.helpers.llm_helpers import validate_notes

_cache: dict = {}


def process_meeting(meeting_id: str, llm_name: str = "groq") -> dict:
    cache_key = f"{meeting_id}:{llm_name}"
    if cache_key in _cache:
        return _cache[cache_key]

    meeting = supabase.table("meetings").select("raw_transcript").eq("id", meeting_id).execute()

    if not meeting.data:
        return None

    transcript = meeting.data[0]["raw_transcript"]
    raw = llm_client(transcript, llm_name)

    if raw is None:
        raise Exception("LLM failed to generate notes.")

    notes = validate_notes(raw)

    existing = supabase.table("notes").select("id").eq("meeting_id", meeting_id).eq("llm", llm_name).execute()

    if existing.data:
        supabase.table("notes").update({
            "summary": notes["summary"],
            "action_items": notes["action_items"],
            "decisions": notes["decisions"],
            "key_takeaways": notes["key_takeaways"],
            "topics": notes["topics"],
            "next_steps": notes["next_steps"],
            "llm_raw": raw,
            "llm": llm_name
        }).eq("meeting_id", meeting_id).eq("llm", llm_name).execute()
    else:
        supabase.table("notes").insert({
            "id": str(uuid.uuid4()),
            "meeting_id": meeting_id,
            "summary": notes["summary"],
            "action_items": notes["action_items"],
            "decisions": notes["decisions"],
            "key_takeaways": notes["key_takeaways"],
            "topics": notes["topics"],
            "next_steps": notes["next_steps"],
            "llm_raw": raw,
            "llm": llm_name
        }).execute()

    _cache[cache_key] = notes
    return notes


def process_all_meetings() -> dict:
    meetings = supabase.table("meetings").select("id").execute()
    existing_notes = supabase.table("notes").select("meeting_id").execute()
    existing_ids = {n["meeting_id"] for n in existing_notes.data}

    results = {"processed": [], "skipped": [], "failed": []}

    for meeting in meetings.data:
        meeting_id = meeting["id"]
        if meeting_id in existing_ids:
            results["skipped"].append(meeting_id)
            continue

        try:
            notes = process_meeting(meeting_id)
            if notes:
                results["processed"].append(meeting_id)
        except Exception as e:
            results["failed"].append({"meeting_id": meeting_id, "error": str(e)})
            break

    return results


def get_notes_by_meeting_id(meeting_id: str) -> dict | None:
    try:
        uuid.UUID(meeting_id)
    except ValueError:
        return None

    meeting = supabase.table("meetings").select("id").eq("id", meeting_id).execute()
    if not meeting.data:
        return None

    notes = supabase.table("notes").select("*").eq("meeting_id", meeting_id).execute()
    if not notes.data:
        return None

    return notes.data[0]

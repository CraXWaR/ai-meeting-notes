import json
import re
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.settings import settings
from app.helpers.llm_helpers import log_retry, merge_notes, validate_notes, chunk_transcript

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)

prompt_template = ChatPromptTemplate.from_template("""
You are a meeting notes assistant. Analyze the following meeting transcript and return ONLY valid JSON with no explanation, no markdown, no extra text.

Return this exact structure:
{{
  "summary": "string",
  "action_items": [{{ "text": "string", "owner": "string or null", "due_date": "string or null" }}],
  "decisions": ["string"],
  "key_takeaways": ["string"],
  "topics": ["string"],
  "next_steps": [{{ "text": "string", "owner": "string or null" }}]
}}

Transcript:
{transcript}
""")

chain = prompt_template | llm


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=10, max=40),
    stop=stop_after_attempt(2),
    before_sleep=log_retry
)
def _call_llm(transcript):
    response = chain.invoke({"transcript": transcript})
    content = response.content
    if content is None:
        raise ValueError("LLM returned empty response.")
    return content


def llm_client(transcript):
    try:
        chunks = chunk_transcript(transcript)

        if len(chunks) == 1:
            return _call_llm(chunks[0])

        all_notes = []
        for chunk in chunks:
            raw = _call_llm(chunk)
            all_notes.append(validate_notes(raw))

        return json.dumps(merge_notes(all_notes))

    except Exception as exception:
        original = exception.last_attempt.exception() if isinstance(exception, RetryError) else exception
        match = re.search(r"Please try again in (\d+m[\d.]+s)", str(original))
        wait_time = match.group(1) if match else "some time"
        raise Exception(f"Rate limit reached. Please try again in {wait_time}.")

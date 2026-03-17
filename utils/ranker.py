"""
AI Resume Ranking using Groq API with Llama models.
To switch models, change MODEL_NAME below.
"""

import os
import json
from groq import Groq

# ── Model config ─────────────────────────────────────────────
# Groq-supported models:
#   "llama-3.3-70b-versatile"  — best balance (recommended)
#   "llama-3.1-8b-instant"     — cheaper, faster, good for basic screening
#   "mixtral-8x7b-32768"       — good alternative
MODEL_NAME = "llama-3.1-8b-instant"

from dotenv import load_dotenv
load_dotenv()

# ── Groq API Key (loaded from .env — not exposed in frontend) ──────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are an expert HR analyst. Analyze the resume against the job description and return ONLY a JSON object.

Return ONLY valid JSON — no markdown, no backticks, no extra text before or after.

JSON structure:
{
  "candidate_name": "<full name from resume, or filename if not found>",
  "education": "<highest degree and institution, e.g. MBA, IIM Ahmedabad>",
  "years_exp": "<total years, e.g. 8 years>",
  "score": <integer 1-100 based on JD fit>,
  "matched_skills": ["skill1", "skill2", ...],
  "experience": "<2-3 sentence summary of experience relevant to THIS JD>",
  "strengths": ["strength relevant to JD", ...],
  "gaps": ["missing requirement", ...]
}

Scoring guide:
90-100: Exceptional match, meets all requirements
75-89:  Strong match, meets most requirements  
50-74:  Moderate match, meets some requirements
25-49:  Weak match, significant gaps
1-24:   Poor match, most requirements missing

Keep matched_skills to max 8 items. Keep strengths to 2-4 items. Keep gaps to 1-3 items.
Be specific and relevant to the job description — not generic."""


def rank_resume(resume_text: str, jd_text: str, filename: str) -> dict:
    """
    Send resume + JD to Groq (Llama) and get structured ranking back.
    Returns a dict with score, skills, strengths, gaps etc.
    """
    client = Groq(api_key=GROQ_API_KEY)

    user_content = f"""JOB DESCRIPTION:
{jd_text}

---

RESUME:
{resume_text[:5000]}"""  # Further trim to 5000 chars to stay within TPM limits

    import time
    max_retries = 3
    retry_delay = 10  # Increased delay for TPM reset
    
    response = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=800, # Reduced slightly to save tokens
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
            )
            break # Success!
        except Exception as e:
            if 'rate' in str(e).lower() and attempt < max_retries - 1:
                # If rate limit hit, wait significantly longer
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise e

    if not response:
        raise ValueError("AI failed to provide a response after multiple attempts.")

    try:
        raw = response.choices[0].message.content.strip()

        # Strip any accidental markdown fences
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        # Ensure required fields exist
        result.setdefault('candidate_name', filename.rsplit('.', 1)[0])
        result.setdefault('education', '')
        result.setdefault('years_exp', '')
        result.setdefault('score', 0)
        result.setdefault('matched_skills', [])
        result.setdefault('experience', '')
        result.setdefault('strengths', [])
        result.setdefault('gaps', [])
        result['fileName'] = filename

        # Clamp score
        result['score'] = max(0, min(100, int(result['score'])))

        return result

    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        if 'authentication' in error_msg.lower() or 'api key' in error_msg.lower():
            raise ValueError("Invalid Groq API key. Please check the key configured in the server.")
        elif 'rate' in error_msg.lower() and 'limit' in error_msg.lower():
            raise ValueError("API rate limit hit. Please wait a moment and try again.")
        raise ValueError(error_msg)

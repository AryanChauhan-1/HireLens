import json
import re

from google import genai
from google.genai import types

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def extract_json(text: str) -> dict:
    """
    Safely extracts JSON from Gemini responses.
    Handles:
    - Markdown fences
    - Extra text before/after JSON
    - Whitespace
    """

    if not text:
        raise ValueError("Empty response received from JD Agent.")

    text = text.strip()

    # Remove markdown fences if present
    text = text.replace("```json", "")
    text = text.replace("```", "").strip()

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(
            f"JD Agent did not return valid JSON.\n\n{text}"
        )

    json_text = match.group(0)

    return json.loads(json_text)


def run_jd_agent(jd_content: str) -> dict:

    prompt = f"""
You are Agent 2 of HireLens (MAVS).

ROLE
-----
Job Intelligence Agent

TASK
-----
Analyze ONLY the Job Description.

DO NOT compare it with any resume.

Return ONLY valid JSON.

JOB DESCRIPTION
----------------
{jd_content}

OUTPUT SCHEMA

{{
    "role": "",
    "required_skills": [],
    "preferred_skills": [],
    "experience": "",
    "education": "",
    "responsibilities": [],
    "tools_and_technologies": []
}}

RULES

1. Return ONLY JSON.
2. No markdown.
3. No explanation.
4. Every key MUST exist.
5. Use [] instead of null.
6. Use "" instead of null.
7. Never include trailing commas.
8. Never invent skills not present in the JD.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )

    print("\n" + "=" * 80)
    print("RAW JD RESPONSE")
    print("=" * 80)
    print(response.text)
    print("=" * 80 + "\n")

    return extract_json(response.text)
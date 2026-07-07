import json

from google import genai
from google.genai import types

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def run_resume_agent(resume_content: str) -> dict:

    prompt = f"""
You are Agent 1 of MAVS.

Role:
Resume Intelligence Agent.

Your ONLY responsibility is to analyze the candidate resume.

DO NOT compare it with any Job Description.

Extract the following information.

Return ONLY valid JSON.

Resume:

{resume_content}

JSON Format:

{{
    "candidate_name":"",
    "skills":[],
    "experience":"",
    "education":"",
    "projects":[],
    "programming_languages":[],
    "frameworks":[],
    "databases":[],
    "cloud_technologies":[]
}}

Return ONLY JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)
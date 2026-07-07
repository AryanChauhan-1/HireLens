import json

from google import genai
from google.genai import types

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def run_validation_agent(resume_data: dict, jd_data: dict) -> dict:

    prompt = f"""
You are Agent 3 of MAVS.

ROLE:
Technical Validation Agent.

Your ONLY responsibility is to compare the structured Resume data and structured Job Description data.

Do NOT re-analyze the resume.

Do NOT re-analyze the Job Description.

Use ONLY the information provided below.

==========================
RESUME DATA
==========================

{json.dumps(resume_data, indent=2)}

==========================
JOB DESCRIPTION DATA
==========================

{json.dumps(jd_data, indent=2)}

==========================

Perform the following tasks.

1. Calculate

• Skills Match (0-100)

• Experience Match (0-100)

• Education Match (0-100)

• Overall Match (0-100)

2. Identify

• Strengths

• Weaknesses

• Missing Skills

3. Assign

• Risk Score
(Low / Medium / High)

• Candidate Status
(Strong Match / Potential Match / Low Match)

4. Generate recruiter reasoning.

Explain WHY the candidate received the score.

Keep it concise.

Maximum 80 words.

5. Generate EXACTLY 3 interview questions.

Question 1 → Easy

Question 2 → Medium

Question 3 → Hard

Each question MUST contain:

• difficulty

• targeted_skill

• question

• why_this_question

==========================

Return ONLY VALID JSON.

JSON FORMAT

{{
    "match_breakdown":
    {{
        "skills_match":0,
        "experience_match":0,
        "education_match":0
    }},

    "overall_match":0,

    "candidate_match":"0%",

    "strengths":[],

    "weaknesses":[],

    "missing_skills":[],

    "risk_score":"",

    "status":"",

    "reasoning":
    {{
        "summary":"",
        "recommendation":""
    }},

    "interview_questions":
    [
        {{
            "difficulty":"Easy",
            "targeted_skill":"",
            "question":"",
            "why_this_question":""
        }},
        {{
            "difficulty":"Medium",
            "targeted_skill":"",
            "question":"",
            "why_this_question":""
        }},
        {{
            "difficulty":"Hard",
            "targeted_skill":"",
            "question":"",
            "why_this_question":""
        }}
    ]
}}

Rules:

- Return ONLY JSON.
- No markdown.
- No explanations.
- No additional text.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    print("\n" + "=" * 100)
    print("RAW GEMINI RESPONSE")
    print("=" * 100)
    print(response.text)
    print("=" * 100 + "\n")

    # return json.loads(response.text)
    try:
        return json.loads(response.text)
    except Exception as e:
        print(e)
        print(response.text)
        raise
import json
from google import genai
from google.genai import types
from app.core.config import settings

def run_mavs_pipeline(resume_content: str, jd_content: str) -> dict:
    """
    Executes the 3-step Multi-Agent verification logic for MAVS using Gemini 2.5 Flash.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    master_agent_prompt = f"""
    You are the core engine of MAVS (Multi-Agent Validation Suite). Your job is to catch fake technical claims by analyzing a resume against a Job Description and generating exactly 3 surgical questions.

    AGENT 1: [The Code Archaeologist]
    Task: Deeply analyze the provided Candidate Resume. Extract true engineering frameworks, system architectures, and explicit technical claims.
    Candidate Resume Text:
    ---
    {resume_content}
    ---

    AGENT 2: [The JD Deconstructer]
    Task: Extract core engineering requirements and stack prerequisites from the Job Description.
    Job Description Text:
    ---
    {jd_content}
    ---

    AGENT 3: [The Technical Critic]
    Task: Cross-match the profiles. Identify high-level architectural claims in the resume that match the JD. Generate EXACTLY 3 deep validation questions based directly on the candidate's stated projects to test if they actually wrote the code. Provide strict evaluation metrics for each.

    STRICT OUTPUT FORMAT RULE:
    Return ONLY a valid JSON array containing exactly 3 objects. Do not wrap the response in markdown code blocks like ```json ... ```. No conversational filler text allowed.

    Format Template:
    [
      {{
        "question_number": 1,
        "targeted_claim": "Specific framework or project claim being tested",
        "question": "The deep engineering validation question",
        "expected_evaluation_metric": "Keywords or technical concepts required in the answer to pass"
      }},
      ...
    ]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=master_agent_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=1024)
            )
        )
        
        clean_json_output = json.loads(response.text.strip())
        return {
            "status": "Success",
            "mavs_report": clean_json_output
        }
    except json.JSONDecodeError:
        return {
            "status": "Format Error",
            "raw_output": response.text,
            "error_detail": "Failed to parse system agents output as structured JSON."
        }
    except Exception as e:
        return {
            "status": "Pipeline Failed",
            "error_detail": str(e)
        }
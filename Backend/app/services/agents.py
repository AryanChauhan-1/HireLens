from concurrent.futures import ThreadPoolExecutor

from app.services.resume_agent import run_resume_agent
from app.services.jd_agent import run_jd_agent
from app.services.validation_agent import run_validation_agent


def run_mavs_pipeline(resume_content: str, jd_content: str) -> dict:
    """
    MAVS Orchestrator

    Resume Agent
           │
           ├──────────────┐
           │              │
           ▼              ▼
      Resume Agent    JD Agent
           │              │
           └──────┬───────┘
                  ▼
        Validation Agent
                  ▼
         Final Recruiter Report
    """

    # Run Resume Agent and JD Agent in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:

        resume_future = executor.submit(
            run_resume_agent,
            resume_content
        )

        jd_future = executor.submit(
            run_jd_agent,
            jd_content
        )

        resume_analysis = resume_future.result()
        jd_analysis = jd_future.result()

    # Keep only relevant fields for validation
    resume_summary = {
        "candidate_name": resume_analysis.get("candidate_name", ""),
        "skills": resume_analysis.get("skills", []),
        "experience": resume_analysis.get("experience", ""),
        "education": resume_analysis.get("education", "")
    }

    jd_summary = {
        "role": jd_analysis.get("role", ""),
        "required_skills": jd_analysis.get("required_skills", []),
        "experience": jd_analysis.get("experience", ""),
        "education": jd_analysis.get("education", "")
    }

    validation_report = run_validation_agent(
        resume_summary,
        jd_summary
    )

    return {
        "resume_analysis": resume_analysis,
        "jd_analysis": jd_analysis,
        **validation_report
    }

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import traceback

from database import get_db
import models

from app.services.extract import extract_text_from_pdf
from app.services.agents import run_mavs_pipeline

router = APIRouter(prefix="/api", tags=["Validation"])


@router.post("/validate")
async def process_validation(
    resume: UploadFile = File(...),
    jd: str = Form(...),
    db: Session = Depends(get_db)
):
    try:

        # --------------------------------------------------
        # Read uploaded resume
        # --------------------------------------------------

        resume_bytes = await resume.read()

        resume_text = extract_text_from_pdf(resume_bytes)

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Unable to extract text from uploaded resume."
            )

        # --------------------------------------------------
        # Store in database
        # --------------------------------------------------

        candidate = models.Candidate(
            name=resume.filename,
            resume_text=resume_text
        )

        job = models.JobDescription(
            title="Uploaded Job Description",
            jd_text=jd
        )

        db.add(candidate)
        db.add(job)
        db.commit()

        # --------------------------------------------------
        # Run Gemini pipeline
        # --------------------------------------------------

        result = run_mavs_pipeline(
            resume_content=resume_text,
            jd_content=jd
        )

        # --------------------------------------------------
        # Save generated interview questions
        # --------------------------------------------------

        if "interview_questions" in result:
            candidate.generated_questions = json.dumps(
                result["interview_questions"]
            )
            db.commit()

        return result

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print("\n" + "=" * 80)
        traceback.print_exc()
        print("=" * 80 + "\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
    )

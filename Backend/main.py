from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from app.core import config
from app.services.agents import run_mavs_pipeline
from pydantic import BaseModel

# Tables automatic initialize karne ke liye on server launch
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MAVS Suite Engine Gateway", version="2.0")
settings = config.settings

class ValidationRequest(BaseModel):
    resume_text: str
    jd_text: str
    candidate_name: str
    jd_title: str

@app.get("/")
def read_root():
    return {"status": "online", "project": "MAVS Suite Complete Production Ready Layout"}

@app.post("/api/validate")
def trigger_validation_pipeline(payload: ValidationRequest, db: Session = Depends(get_db)):
    """
    Accepts data fields from the frontend dashboard, saves to SQLite database, 
    and returns 3 precise architectural validation questions.
    """
    try:
        # Step 1: Save data fields directly to SQLite tables
        db_jd = models.JobDescription(title=payload.jd_title, jd_text=payload.jd_text)
        db_candidate = models.Candidate(name=payload.candidate_name, resume_text=payload.resume_text)
        
        db.add(db_jd)
        db.add(db_candidate)
        db.commit()
        
        # Step 2: Push variables input parameter context straight to agents loop pipeline
        ai_report_output = run_mavs_pipeline(
            resume_content=payload.resume_text, 
            jd_content=payload.jd_text
        )
        
        # Step 3: Append processed validation block text data to backend profile reports
        if ai_report_output["status"] == "Success":
            db_candidate.generated_questions = json.dumps(ai_report_output["mavs_report"])
            db.commit()
            
        return ai_report_output
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"MAVS Engine Error: {str(e)}")
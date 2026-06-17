from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from models import get_db, Assessment

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, assessment_id: int = None, db: Session = Depends(get_db)):
    from rendering import render
    if assessment_id:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    else:
        assessment = db.query(Assessment).order_by(Assessment.created_at.desc()).first()
    if not assessment: return HTMLResponse("请先完成一项评估", status_code=404)
    items = assessment.items
    from engine import AssessmentEngine
    result = AssessmentEngine.calculate(items)
    return await render("workflow/dashboard.html", {"request": request, "assessment": assessment, "result": result})

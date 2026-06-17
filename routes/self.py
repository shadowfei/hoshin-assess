from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from models import get_db, Assessment, AssessmentItem

router = APIRouter()

@router.get("/{assessment_id}", response_class=HTMLResponse)
async def client_survey(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    from rendering import render
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment: return HTMLResponse("问卷链接无效", status_code=404)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).order_by(AssessmentItem.question_no).all()
    dimensions = {}
    for item in items: dimensions.setdefault(item.dimension, []).append(item)
    return await render("self/survey.html", {"request": request, "assessment": assessment, "dimensions": sorted(dimensions.items())})

@router.post("/{assessment_id}")
async def submit_survey(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    form = await request.form()
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).all()
    for item in items:
        k = f"score_{item.id}"
        if k in form: item.score = int(form[k])
    db.commit()
    return RedirectResponse(url=f"/self/{assessment_id}/result", status_code=303)

@router.get("/{assessment_id}/result", response_class=HTMLResponse)
async def client_result(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    from rendering import render
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment: return HTMLResponse("评估不存在", status_code=404)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).all()
    from engine import AssessmentEngine
    result = AssessmentEngine.calculate(items)
    return await render("self/result.html", {"request": request, "assessment": assessment, "result": result})

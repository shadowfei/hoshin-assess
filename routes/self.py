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
    # 已提交过则跳转到结果页，不可重复填写
    existing = db.query(AssessmentItem).filter(
        AssessmentItem.assessment_id == assessment_id, AssessmentItem.score > 0
    ).first()
    if existing:
        return RedirectResponse(url=f"/self/{assessment_id}/result", status_code=303)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).order_by(AssessmentItem.question_no).all()
    dimensions = {}
    for item in items: dimensions.setdefault(item.dimension, []).append(item)
    return await render("self/survey.html", {"request": request, "assessment": assessment, "dimensions": sorted(dimensions.items())})

@router.post("/{assessment_id}")
async def submit_survey(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    # 防止重复提交
    existing = db.query(AssessmentItem).filter(
        AssessmentItem.assessment_id == assessment_id, AssessmentItem.score > 0
    ).first()
    if existing:
        return RedirectResponse(url=f"/self/{assessment_id}/result", status_code=303)
    form = await request.form()
    # 保存企业信息
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment:
        assessment.industry = form.get("industry", "")
        try: assessment.year_established = int(form["year_established"]) if form.get("year_established") else None
        except: assessment.year_established = None
        try: assessment.employee_count = int(form["employee_count"]) if form.get("employee_count") else None
        except: assessment.employee_count = None
        try: assessment.annual_revenue = float(form["annual_revenue"]) if form.get("annual_revenue") else None
        except: assessment.annual_revenue = None
        try: assessment.manager_count = int(form["manager_count"]) if form.get("manager_count") else None
        except: assessment.manager_count = None
        assessment.assessor = form.get("assessor", "")
        assessment.company_vision = form.get("company_vision", "")
        assessment.company_mission = form.get("company_mission", "")
    # 保存评分
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).all()
    for item in items:
        k = f"score_{item.id}"
        if k in form: item.score = int(form[k])
    db.commit()
    return RedirectResponse(url=f"/self/{assessment_id}/result", status_code=303)

@router.get("/{assessment_id}/result", response_class=HTMLResponse)
async def client_result(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    from rendering import render
    from models import Attachment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment: return HTMLResponse("评估不存在", status_code=404)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).all()
    from engine import AssessmentEngine
    result = AssessmentEngine.calculate(items)
    # 查询附件
    item_ids = [i.id for i in items]
    attachments = db.query(Attachment).filter(Attachment.item_id.in_(item_ids)).all() if item_ids else []
    attach_by_q = {}
    for att in attachments:
        for item in items:
            if item.id == att.item_id:
                attach_by_q.setdefault(item.question_no, []).append(att)
                break
    return await render("assess/report.html", {"request": request, "assessment": assessment, "result": result, "attachments": attach_by_q})

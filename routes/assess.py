from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from models import get_db, Assessment, AssessmentItem, Attachment

router = APIRouter()

def _get_dim_range(dim):
    return {1: (1,8), 2: (9,15), 3: (16,23), 4: (24,30)}[dim]

@router.get("/new", response_class=HTMLResponse)
async def new_assessment(request: Request):
    from rendering import render
    return await render("assess/company_info.html", {"request": request})

@router.post("/new")
async def create_assessment(
    request: Request,
    company_name: str = Form(""), company_vision: str = Form(""), company_mission: str = Form(""),
    year_established: int = Form(None), annual_revenue: float = Form(None),
    employee_count: int = Form(None), manager_count: int = Form(None),
    industry: str = Form(""), assessor: str = Form(""),
    db: Session = Depends(get_db),
):
    assessment = Assessment(company_name=company_name, company_vision=company_vision, company_mission=company_mission,
        year_established=year_established, annual_revenue=annual_revenue, employee_count=employee_count,
        manager_count=manager_count, industry=industry, assessor=assessor, type="assess")
    db.add(assessment)
    db.flush()
    from questions_data import QUESTIONS
    for dim in range(1,5):
        start, end = _get_dim_range(dim)
        for qn in range(start, end+1):
            qdata = QUESTIONS.get(qn, {})
            db.add(AssessmentItem(
                assessment_id=assessment.id,
                dimension=dim,
                question_no=qn,
                question_text=qdata.get("text", ""),
                reference_text=qdata.get("ref", ""),
            ))
    db.commit()
    return RedirectResponse(url=f"/assess/form/{assessment.id}", status_code=303)

@router.get("/form/{assessment_id}", response_class=HTMLResponse)
async def scoring_form(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    from rendering import render
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment: return HTMLResponse("评估不存在", status_code=404)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).order_by(AssessmentItem.question_no).all()
    dimensions = {}
    for item in items: dimensions.setdefault(item.dimension, []).append(item)
    return await render("assess/form.html", {"request": request, "assessment": assessment, "dimensions": sorted(dimensions.items())})

@router.post("/form/{assessment_id}")
async def save_scores(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    form = await request.form()
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).all()
    for item in items:
        k = f"score_{item.id}"
        if k in form: item.score = int(form[k])
    from engine import AssessmentEngine
    result = AssessmentEngine.calculate(items)
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    assessment.desire_score = result["desire_score"]
    assessment.capacity_score = result["capacity_score"]
    assessment.quadrant = result["quadrant_key"]
    assessment.overall_score = result["overall_score"]
    db.commit()
    return RedirectResponse(url=f"/assess/report/{assessment_id}", status_code=303)

@router.get("/report/{assessment_id}", response_class=HTMLResponse)
async def view_report(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    from rendering import render
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

@router.get("/history", response_class=HTMLResponse)
async def assessment_history(request: Request, db: Session = Depends(get_db)):
    from rendering import render
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
    return await render("assess/history.html", {"request": request, "assessments": assessments})

@router.get("/create-client", response_class=HTMLResponse)
async def create_client_survey(request: Request):
    from rendering import render
    return await render("assess/create_client.html", {"request": request})

@router.post("/create-client")
async def do_create_client_survey(
    request: Request,
    company_name: str = Form(""),
    db: Session = Depends(get_db),
):
    assessment = Assessment(company_name=company_name, type="self")
    db.add(assessment)
    db.flush()
    from questions_data import QUESTIONS
    for dim in range(1,5):
        start, end = {1:(1,8),2:(9,15),3:(16,23),4:(24,30)}[dim]
        for qn in range(start, end+1):
            qdata = QUESTIONS.get(qn, {})
            db.add(AssessmentItem(
                assessment_id=assessment.id, dimension=dim, question_no=qn,
                question_text=qdata.get("text",""), reference_text=qdata.get("ref",""),
            ))
    db.commit()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/assess/client-done/{assessment.id}", status_code=303)

@router.get("/client-done/{assessment_id}", response_class=HTMLResponse)
async def client_survey_created(request: Request, assessment_id: int):
    from rendering import render
    from models import get_db
    db = next(get_db())
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    db.close()
    return await render("assess/client_done.html", {"request": request, "assessment": assessment})

@router.get("/score-detail/{assessment_id}", response_class=HTMLResponse)
async def score_detail(request: Request, assessment_id: int, from_client: str = None, db: Session = Depends(get_db)):
    from rendering import render
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment: return HTMLResponse("评估不存在", status_code=404)
    items = db.query(AssessmentItem).filter(AssessmentItem.assessment_id == assessment_id).order_by(AssessmentItem.question_no).all()
    dimensions = {}
    for item in items: dimensions.setdefault(item.dimension, []).append(item)
    return await render("assess/score_detail.html", {"request": request, "assessment": assessment, "dimensions": sorted(dimensions.items()), "from_client": from_client})

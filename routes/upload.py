import os, uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import get_db, Attachment, AssessmentItem
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter()

@router.post("/upload")
async def upload_file(item_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    item = db.query(AssessmentItem).filter(AssessmentItem.id == item_id).first()
    if not item: return JSONResponse({"error":"题目不存在"}, status_code=404)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS: return JSONResponse({"error":f"不支持的文件类型:{ext}"}, status_code=400)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE: return JSONResponse({"error":"文件超过10MB限制"}, status_code=400)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name
    with open(file_path, "wb") as f: f.write(content)
    attachment = Attachment(item_id=item.id, file_name=file.filename, file_path=str(file_path), file_size=len(content), file_type=ext[1:])
    db.add(attachment)
    item.has_attachment = True
    db.commit()
    return JSONResponse({"success":True, "file_name":file.filename})

@router.get("/files/{item_id}")
async def list_files(item_id: int, db: Session = Depends(get_db)):
    files = db.query(Attachment).filter(Attachment.item_id == item_id).all()
    return JSONResponse([{"id":f.id,"name":f.file_name,"size":f.file_size,"type":f.file_type} for f in files])

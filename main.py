from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models import init_db
from routes.assess import router as assess_router
from routes.workflow import router as workflow_router
from routes.self import router as self_router
from routes.upload import router as upload_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="方针管理导入评估系统", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(assess_router, prefix="/assess", tags=["评估工具"])
app.include_router(workflow_router, prefix="/workflow", tags=["咨询师工作流"])
app.include_router(self_router, prefix="/self", tags=["客户自评"])
app.include_router(upload_router, prefix="/upload", tags=["附件"])

@app.get("/")
async def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/assess/new")

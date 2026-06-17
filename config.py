import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# 支持环境变量覆盖（Zeabur/Railway 用 PostgreSQL 时设置）
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'hoshin.db'}"
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".xlsx", ".docx"}

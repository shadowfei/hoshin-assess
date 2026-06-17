from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), default="")
    company_vision = Column(Text, default="")
    company_mission = Column(Text, default="")
    year_established = Column(Integer, nullable=True)
    annual_revenue = Column(Float, nullable=True)
    employee_count = Column(Integer, nullable=True)
    manager_count = Column(Integer, nullable=True)
    industry = Column(String(100), default="")
    assessor = Column(String(100), default="")
    type = Column(String(20), default="assess")
    notes = Column(Text, default="")
    desire_score = Column(Float, nullable=True)
    capacity_score = Column(Float, nullable=True)
    quadrant = Column(String(50), nullable=True)
    overall_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    items = relationship("AssessmentItem", back_populates="assessment", cascade="all, delete-orphan")
    plans = relationship("ImprovementPlan", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentItem(Base):
    __tablename__ = "assessment_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    dimension = Column(Integer)
    question_no = Column(Integer)
    score = Column(Integer, default=0)
    question_text = Column(Text, default="")
    reference_text = Column(Text, default="")
    note = Column(Text, default="")
    has_attachment = Column(Boolean, default=False)
    assessment = relationship("Assessment", back_populates="items")
    attachments = relationship("Attachment", back_populates="item", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("assessment_items.id"))
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(20))
    uploaded_at = Column(DateTime, default=datetime.now)
    item = relationship("AssessmentItem", back_populates="attachments")

class ImprovementPlan(Base):
    __tablename__ = "improvement_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    plan_type = Column(String(20))
    title = Column(String(200))
    owner = Column(String(100), default="")
    target_date = Column(String(20), default="")
    status = Column(String(20), default="todo")
    a3_content = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    assessment = relationship("Assessment", back_populates="plans")

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

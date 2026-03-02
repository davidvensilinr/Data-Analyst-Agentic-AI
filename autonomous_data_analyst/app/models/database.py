from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    datasets = relationship("Dataset", back_populates="owner")
    runs = relationship("Run", back_populates="user")


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String, nullable=False)  # csv, json, parquet, etc.
    schema_info = Column(JSON)  # Column names, types, etc.
    profile_info = Column(JSON)  # Data profiling results
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="datasets")
    runs = relationship("Run", back_populates="dataset")


class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    plan = Column(JSON)  # The execution plan
    status = Column(String, default="pending")  # pending, running, completed, failed
    result = Column(JSON)  # Final results
    metrics = Column(JSON)  # Performance metrics
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="runs")
    dataset = relationship("Dataset", back_populates="runs")
    steps = relationship("RunStep", back_populates="run", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="run", cascade="all, delete-orphan")


class RunStep(Base):
    __tablename__ = "run_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    step_id = Column(String, nullable=False)  # Step identifier from plan
    step_type = Column(String, nullable=False)  # profile, clean, sql, analysis, etc.
    spec = Column(JSON)  # Step specification
    status = Column(String, default="pending")  # pending, running, completed, failed
    result = Column(JSON)  # Step execution result
    error_message = Column(Text)
    model_prompt = Column(Text)  # LLM prompt if applicable
    model_output = Column(Text)  # LLM output if applicable
    tool_call = Column(JSON)  # Tool call details
    tool_result = Column(JSON)  # Tool execution result
    rationale = Column(Text)  # Human-readable explanation
    confidence = Column(Float)  # Confidence score 0-1
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    run = relationship("Run", back_populates="steps")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    event_type = Column(String, nullable=False)  # step_started, step_completed, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)  # Event data
    content_hash = Column(String, nullable=False)  # SHA256 hash for immutability
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    run = relationship("Run", back_populates="audit_logs")
    user = relationship("User")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String, unique=True, nullable=False)  # Hashed API key
    name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    permissions = Column(JSON)  # List of permissions
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")


# Database connection
engine = create_engine(
    "sqlite:///./data/analyst.db",
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)

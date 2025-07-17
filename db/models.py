from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class JobStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
class FileStatusEnum(str, Enum):
    PENDING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    wsi_id = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    status = Column(SqlEnum(JobStatusEnum, native_enum=False), default=JobStatusEnum.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint for deduplication
    __table_args__ = (
        UniqueConstraint("wsi_id", "tool_name", name="uq_wsi_tool"),
    )

class ResultFile(Base):
    __tablename__ = "result_files"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    status = Column(SqlEnum(FileStatusEnum, native_enum=False), default=FileStatusEnum.RUNNING)
    file_path = Column(String)
    file_type = Column(String)
    description = Column(String)

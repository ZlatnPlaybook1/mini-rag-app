from .minirag_base import SQLAIchemyBase
from sqlalchemy import Column, DateTime, ForeignKey, Index
from sqlalchemy import Integer, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB


class CeleryTaskExecution(SQLAIchemyBase):
    __tablename__ = "celery_task_executions"


    execution_id = Column(Integer, primary_key=True, autoincrement=True)

    task_name = Column(String(255) , nullable=False)
    task_args_hash = Column(String(64) , nullable=False) # SHA-256 hash of the task arguments to identify unique executions
    celery_task_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, STARTED, SUCCESS, FAILURE
   
    task_args = Column(JSONB, nullable=False)
    result = Column(JSONB, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_task_name_args_celery_hash", task_name, task_args_hash, celery_task_id, unique=True),
        Index('ix_task_executtion_status', status),
        Index('ix_task_executtion_created_at', created_at),
        Index('ix_celery_task_id', celery_task_id)
    )
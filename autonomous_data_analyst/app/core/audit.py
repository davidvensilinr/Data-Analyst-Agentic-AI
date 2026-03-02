import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import AuditLog, Run, User
from app.models.schemas import EventType


class AuditLogger:
    """Immutable audit logging system with content hashing."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _compute_content_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA256 hash of content for immutability."""
        content_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def log_event(
        self,
        run_id: str,
        event_type: Union[EventType, str],
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> AuditLog:
        """Log an audit event with immutable hash."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if data is None:
            data = {}
        
        # Ensure event_type is string
        if isinstance(event_type, EventType):
            event_type = event_type.value
        
        # Create the audit log entry
        audit_entry = AuditLog(
            run_id=run_id,
            event_type=event_type,
            timestamp=timestamp,
            data=data,
            content_hash="",  # Will be set after computing
            user_id=user_id
        )
        
        # Compute content hash
        content_data = {
            "run_id": run_id,
            "event_type": event_type,
            "timestamp": timestamp.isoformat(),
            "data": data,
            "user_id": user_id
        }
        audit_entry.content_hash = self._compute_content_hash(content_data)
        
        # Save to database
        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)
        
        return audit_entry
    
    def verify_integrity(self, run_id: str) -> bool:
        """Verify the integrity of audit logs for a run."""
        audit_logs = self.db.query(AuditLog).filter(
            AuditLog.run_id == run_id
        ).order_by(AuditLog.timestamp).all()
        
        for log in audit_logs:
            # Recompute hash
            content_data = {
                "run_id": log.run_id,
                "event_type": log.event_type,
                "timestamp": log.timestamp.isoformat(),
                "data": log.data,
                "user_id": log.user_id
            }
            computed_hash = self._compute_content_hash(content_data)
            
            if computed_hash != log.content_hash:
                return False
        
        return True
    
    def get_run_history(self, run_id: str) -> list[AuditLog]:
        """Get complete audit history for a run."""
        return self.db.query(AuditLog).filter(
            AuditLog.run_id == run_id
        ).order_by(AuditLog.timestamp).all()
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> list[AuditLog]:
        """Get recent activity for a user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()


class StepAuditor:
    """Specialized auditor for step execution."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def log_step_started(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        spec: Dict[str, Any],
        user_id: str
    ) -> AuditLog:
        """Log step start event."""
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.STEP_STARTED,
            data={
                "step_id": step_id,
                "step_type": step_type,
                "spec": spec
            },
            user_id=user_id
        )
    
    def log_step_completed(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        result: Dict[str, Any],
        model_prompt: Optional[str] = None,
        model_output: Optional[str] = None,
        tool_call: Optional[Dict[str, Any]] = None,
        tool_result: Optional[Dict[str, Any]] = None,
        rationale: Optional[str] = None,
        confidence: Optional[float] = None,
        user_id: str
    ) -> AuditLog:
        """Log step completion event."""
        event_data = {
            "step_id": step_id,
            "step_type": step_type,
            "result": result,
            "rationale": rationale,
            "confidence": confidence
        }
        
        # Add optional fields if provided
        if model_prompt:
            event_data["model_prompt"] = model_prompt
        if model_output:
            event_data["model_output"] = model_output
        if tool_call:
            event_data["tool_call"] = tool_call
        if tool_result:
            event_data["tool_result"] = tool_result
        
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.STEP_COMPLETED,
            data=event_data,
            user_id=user_id
        )
    
    def log_step_failed(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        error_message: str,
        user_id: str
    ) -> AuditLog:
        """Log step failure event."""
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.STEP_FAILED,
            data={
                "step_id": step_id,
                "step_type": step_type,
                "error_message": error_message
            },
            user_id=user_id
        )
    
    def log_run_started(
        self,
        run_id: str,
        question: str,
        dataset_id: str,
        plan: Dict[str, Any],
        user_id: str
    ) -> AuditLog:
        """Log run start event."""
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.RUN_STARTED,
            data={
                "question": question,
                "dataset_id": dataset_id,
                "plan": plan
            },
            user_id=user_id
        )
    
    def log_run_completed(
        self,
        run_id: str,
        result: Dict[str, Any],
        metrics: Dict[str, Any],
        user_id: str
    ) -> AuditLog:
        """Log run completion event."""
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.RUN_COMPLETED,
            data={
                "result": result,
                "metrics": metrics
            },
            user_id=user_id
        )
    
    def log_run_failed(
        self,
        run_id: str,
        error_message: str,
        user_id: str
    ) -> AuditLog:
        """Log run failure event."""
        return self.audit_logger.log_event(
            run_id=run_id,
            event_type=EventType.RUN_FAILED,
            data={
                "error_message": error_message
            },
            user_id=user_id
        )

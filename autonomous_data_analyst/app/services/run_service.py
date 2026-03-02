from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Run, RunStep, Dataset, User
from app.models.schemas import RunWithDetails, Plan, StepSpec, StepType, RunStatus, SystemMetrics
from app.services.orchestrator import Orchestrator
from app.services.websocket_manager import WebSocketManager
from app.planners.llm_planner import LLMPlanner
from config.settings import settings


class RunService:
    """Service for managing analysis runs."""
    
    def __init__(self, db: Session, websocket_manager: WebSocketManager):
        self.db = db
        self.websocket_manager = websocket_manager
        self.orchestrator = Orchestrator(db, websocket_manager)
        self.planner = LLMPlanner()
    
    async def create_analysis_run(
        self,
        dataset_id: str,
        question: str,
        dry_run: bool = False,
        user_id: str = None
    ) -> Tuple[str, Plan]:
        """Create a new analysis run."""
        # Get dataset
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Create plan using LLM planner
        plan = await self.planner.create_plan(
            question=question,
            dataset=dataset,
            db=self.db
        )
        
        # Create run record
        run = Run(
            question=question,
            plan=plan.dict(),
            status=RunStatus.PENDING,
            user_id=user_id,
            dataset_id=dataset_id
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        
        return run.id, plan
    
    async def create_cleaning_run(
        self,
        dataset_id: str,
        plan: Plan,
        apply_changes: bool = False,
        user_id: str = None
    ) -> str:
        """Create a new cleaning run."""
        # Get dataset
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Create run record
        run = Run(
            question=f"Clean dataset {dataset.name}",
            plan=plan.dict(),
            status=RunStatus.PENDING,
            user_id=user_id,
            dataset_id=dataset_id
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        
        return run.id
    
    async def execute_run(self, run_id: str) -> Dict[str, any]:
        """Execute a run."""
        run = self.db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        if run.status != RunStatus.PENDING:
            raise ValueError(f"Run {run_id} is not in pending status")
        
        # Parse plan
        plan = Plan(**run.plan)
        
        # Execute using orchestrator
        result = await self.orchestrator.execute_plan(
            run_id=run_id,
            plan=plan,
            dry_run=False,
            user_id=run.user_id
        )
        
        return result
    
    async def get_run_with_details(self, run_id: str) -> RunWithDetails:
        """Get run with all details including dataset and steps."""
        run = self.db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        # Get dataset
        dataset = self.db.query(Dataset).filter(Dataset.id == run.dataset_id).first()
        
        # Get steps
        steps = self.db.query(RunStep).filter(RunStep.run_id == run_id).all()
        
        # Convert to response format
        run_dict = {
            "id": run.id,
            "question": run.question,
            "plan": run.plan,
            "status": run.status,
            "result": run.result,
            "metrics": run.metrics,
            "user_id": run.user_id,
            "dataset_id": run.dataset_id,
            "created_at": run.created_at,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "dataset": dataset,
            "steps": steps
        }
        
        return RunWithDetails(**run_dict)
    
    async def get_user_runs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Run]:
        """Get runs for a user."""
        runs = self.db.query(Run).filter(
            Run.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return runs
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get system metrics."""
        # Get total runs
        total_runs = self.db.query(func.count(Run.id)).scalar() or 0
        
        # Get active runs
        active_runs = self.db.query(func.count(Run.id)).filter(
            Run.status == RunStatus.RUNNING
        ).scalar() or 0
        
        # Get completed runs
        completed_runs = self.db.query(func.count(Run.id)).filter(
            Run.status == RunStatus.COMPLETED
        ).scalar() or 0
        
        # Calculate success rate
        success_rate = (completed_runs / total_runs) if total_runs > 0 else 0.0
        
        # Calculate average duration
        avg_duration_result = self.db.query(
            func.avg(
                func.extract('epoch', Run.completed_at - Run.started_at)
            )
        ).filter(
            Run.status == RunStatus.COMPLETED,
            Run.completed_at.isnot(None),
            Run.started_at.isnot(None)
        ).scalar()
        
        average_duration = float(avg_duration_result) if avg_duration_result else 0.0
        
        # For uptime, we'll use a placeholder (in production, track actual start time)
        uptime_seconds = 0.0
        
        return SystemMetrics(
            active_runs=active_runs,
            total_runs=total_runs,
            success_rate=success_rate,
            average_duration=average_duration,
            uptime_seconds=uptime_seconds
        )
    
    async def cancel_run(self, run_id: str, user_id: str) -> bool:
        """Cancel a running run."""
        run = self.db.query(Run).filter(
            Run.id == run_id,
            Run.user_id == user_id
        ).first()
        
        if not run:
            return False
        
        if run.status not in [RunStatus.PENDING, RunStatus.RUNNING]:
            return False
        
        run.status = RunStatus.FAILED
        run.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Send cancellation event via WebSocket
        await self.websocket_manager.send_run_failed(
            run_id=run_id,
            error_message="Run cancelled by user"
        )
        
        return True
    
    async def retry_run(self, run_id: str, user_id: str) -> str:
        """Retry a failed run."""
        run = self.db.query(Run).filter(
            Run.id == run_id,
            Run.user_id == user_id
        ).first()
        
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        if run.status != RunStatus.FAILED:
            raise ValueError(f"Run {run_id} is not in failed status")
        
        # Reset run status
        run.status = RunStatus.PENDING
        run.started_at = None
        run.completed_at = None
        run.result = None
        run.metrics = None
        
        # Clear step results
        self.db.query(RunStep).filter(RunStep.run_id == run_id).delete()
        
        self.db.commit()
        
        # Execute the run
        await self.execute_run(run_id)
        
        return run_id

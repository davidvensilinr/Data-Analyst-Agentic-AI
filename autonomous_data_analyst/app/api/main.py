from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.models.database import get_db, create_tables
from app.models.schemas import *
from app.core.security import get_current_active_user, authenticate_api_key, check_dataset_permission, check_run_permission
from app.core.audit import AuditLogger
from app.services.dataset_service import DatasetService
from app.services.run_service import RunService
from app.services.websocket_manager import WebSocketManager
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Data Analyst Backend API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# WebSocket manager
websocket_manager = WebSocketManager()

# Create database tables
create_tables()


# Dependency to get current user (supports both JWT and API key)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user supporting both JWT and API key authentication."""
    if not credentials:
        return None
    
    try:
        # Try API key authentication first
        return await authenticate_api_key(credentials, db)
    except HTTPException:
        try:
            # Fall back to JWT authentication
            return await get_current_active_user(credentials, db)
        except HTTPException:
            return None


# API Endpoints

@app.post("/api/upload", response_model=UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Upload a dataset for analysis."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    dataset_service = DatasetService(db)
    
    try:
        dataset = await dataset_service.upload_dataset(
            file=file,
            name=name or file.filename,
            description=description,
            is_public=is_public,
            owner_id=current_user.id
        )
        
        return UploadResponse(
            dataset_id=dataset.id,
            name=dataset.name,
            file_type=dataset.file_type,
            file_size=dataset.file_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/profile/{dataset_id}", response_model=ProfileResponse)
async def get_dataset_profile(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get data profiling information for a dataset."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_dataset_permission(current_user, dataset_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dataset"
        )
    
    dataset_service = DatasetService(db)
    
    try:
        profile_info = await dataset_service.profile_dataset(dataset_id)
        return ProfileResponse(
            dataset_id=dataset_id,
            profile_info=profile_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/clean/plan", response_model=CleanPlanResponse)
async def create_cleaning_plan(
    request: CleanPlanRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Create a data cleaning plan."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_dataset_permission(current_user, request.dataset_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dataset"
        )
    
    dataset_service = DatasetService(db)
    
    try:
        plan, rationale = await dataset_service.create_cleaning_plan(
            dataset_id=request.dataset_id,
            cleaning_goals=request.cleaning_goals
        )
        
        return CleanPlanResponse(
            plan=plan,
            rationale=rationale
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/clean/execute", response_model=CleanExecuteResponse)
async def execute_cleaning_plan(
    request: CleanExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Execute a data cleaning plan."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_dataset_permission(current_user, request.dataset_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dataset"
        )
    
    run_service = RunService(db, websocket_manager)
    
    try:
        run_id = await run_service.create_cleaning_run(
            dataset_id=request.dataset_id,
            plan=request.plan,
            apply_changes=request.apply_changes,
            user_id=current_user.id
        )
        
        # Execute in background
        background_tasks.add_task(
            run_service.execute_run,
            run_id
        )
        
        return CleanExecuteResponse(
            run_id=run_id,
            cleaned_dataset_id=None,  # Will be set after execution
            changes_applied=request.apply_changes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Ask a question about a dataset."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_dataset_permission(current_user, request.dataset_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dataset"
        )
    
    run_service = RunService(db, websocket_manager)
    
    try:
        run_id, plan = await run_service.create_analysis_run(
            dataset_id=request.dataset_id,
            question=request.question,
            dry_run=request.dry_run,
            user_id=current_user.id
        )
        
        # Execute in background if not dry run
        if not request.dry_run:
            background_tasks.add_task(
                run_service.execute_run,
                run_id
            )
        
        return AskResponse(
            run_id=run_id,
            plan=plan
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/run/{run_id}", response_model=RunWithDetails)
async def get_run_status(
    run_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get the status and details of a run."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_run_permission(current_user, run_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this run"
        )
    
    run_service = RunService(db, websocket_manager)
    
    try:
        run = await run_service.get_run_with_details(run_id)
        return run
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/api/audit/{run_id}", response_model=List[AuditLogEntry])
async def get_audit_logs(
    run_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get audit logs for a run."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not check_run_permission(current_user, run_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this run"
        )
    
    audit_logger = AuditLogger(db)
    
    try:
        logs = audit_logger.get_run_history(run_id)
        return [
            AuditLogEntry(
                id=log.id,
                run_id=log.run_id,
                event_type=log.event_type,
                timestamp=log.timestamp,
                data=log.data,
                content_hash=log.content_hash,
                user_id=log.user_id
            )
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/datasets", response_model=List[Dataset])
async def list_datasets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """List accessible datasets."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    dataset_service = DatasetService(db)
    
    try:
        datasets = await dataset_service.list_user_datasets(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return datasets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get system metrics."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    run_service = RunService(db, websocket_manager)
    
    try:
        metrics = await run_service.get_system_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# WebSocket endpoint
@app.websocket("/ws/runs/{run_id}")
async def websocket_endpoint(websocket, run_id: str):
    """WebSocket endpoint for real-time run updates."""
    await websocket_manager.connect(websocket, run_id)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

import os
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.database import Dataset
from app.models.schemas import Dataset as DatasetSchema, Plan, StepSpec, StepType
from app.executors.profiler_executor import ProfilerExecutor
from app.planners.llm_planner import LLMPlanner
from config.settings import settings
import mimetypes


class DatasetService:
    """Service for managing datasets."""
    
    def __init__(self, db: Session):
        self.db = db
        self.profiler = ProfilerExecutor(db)
        self.planner = LLMPlanner()
    
    async def upload_dataset(
        self,
        file: UploadFile,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
        owner_id: str = None
    ) -> Dataset:
        """Upload and process a dataset."""
        # Validate file
        if not self._is_valid_file_type(file.filename):
            raise ValueError(f"Unsupported file type: {file.filename}")
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_size = len(content)
            
            # Validate file size
            if file_size > settings.MAX_FILE_SIZE:
                os.remove(file_path)
                raise ValueError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes")
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Failed to save file: {str(e)}")
        
        # Determine file type
        file_type = self._get_file_type(file.filename)
        
        # Create dataset record
        dataset = Dataset(
            name=name,
            description=description,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            owner_id=owner_id,
            is_public=is_public
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        
        # Profile the dataset
        try:
            profile_info = await self.profiler.execute(
                dataset=dataset,
                spec={"operation": "full_profile"},
                previous_results={}
            )
            dataset.profile_info = profile_info.get("result", {})
            dataset.schema_info = profile_info.get("result", {}).get("schema", {})
            self.db.commit()
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Failed to profile dataset {dataset.id}: {str(e)}")
        
        return dataset
    
    async def profile_dataset(self, dataset_id: str) -> Dict[str, any]:
        """Profile a dataset."""
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # If already profiled, return cached result
        if dataset.profile_info:
            return dataset.profile_info
        
        # Profile the dataset
        profile_result = await self.profiler.execute(
            dataset=dataset,
            spec={"operation": "full_profile"},
            previous_results={}
        )
        
        # Update dataset with profile info
        dataset.profile_info = profile_result.get("result", {})
        dataset.schema_info = profile_result.get("result", {}).get("schema", {})
        self.db.commit()
        
        return dataset.profile_info
    
    async def create_cleaning_plan(
        self,
        dataset_id: str,
        cleaning_goals: Optional[List[str]] = None
    ) -> Tuple[Plan, str]:
        """Create a data cleaning plan."""
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Get profile info
        profile_info = dataset.profile_info or await self.profile_dataset(dataset_id)
        
        # Create cleaning plan using LLM planner
        plan = await self.planner.create_cleaning_plan(
            dataset=dataset,
            profile_info=profile_info,
            cleaning_goals=cleaning_goals,
            db=self.db
        )
        
        rationale = f"Created cleaning plan with {len(plan.steps)} steps based on data quality issues and user requirements."
        
        return plan, rationale
    
    async def list_user_datasets(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[DatasetSchema]:
        """List datasets accessible to a user."""
        datasets = self.db.query(Dataset).filter(
            (Dataset.owner_id == user_id) | (Dataset.is_public == True)
        ).offset(skip).limit(limit).all()
        
        return [DatasetSchema.from_orm(ds) for ds in datasets]
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a dataset by ID."""
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    async def delete_dataset(self, dataset_id: str, user_id: str) -> bool:
        """Delete a dataset."""
        dataset = self.db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.owner_id == user_id
        ).first()
        
        if not dataset:
            return False
        
        # Delete file
        try:
            if os.path.exists(dataset.file_path):
                os.remove(dataset.file_path)
        except Exception as e:
            print(f"Failed to delete file {dataset.file_path}: {str(e)}")
        
        # Delete database record
        self.db.delete(dataset)
        self.db.commit()
        
        return True
    
    async def update_dataset(
        self,
        dataset_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Optional[Dataset]:
        """Update dataset metadata."""
        dataset = self.db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.owner_id == user_id
        ).first()
        
        if not dataset:
            return None
        
        # Update fields
        if name is not None:
            dataset.name = name
        if description is not None:
            dataset.description = description
        if is_public is not None:
            dataset.is_public = is_public
        
        dataset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(dataset)
        
        return dataset
    
    def _is_valid_file_type(self, filename: str) -> bool:
        """Check if file type is supported."""
        if not filename:
            return False
        
        file_extension = os.path.splitext(filename)[1].lower()
        valid_extensions = {'.csv', '.json', '.parquet', '.xlsx', '.xls', '.tsv'}
        
        return file_extension in valid_extensions
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from filename."""
        if not filename:
            return 'unknown'
        
        file_extension = os.path.splitext(filename)[1].lower()
        
        type_mapping = {
            '.csv': 'csv',
            '.json': 'json',
            '.parquet': 'parquet',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.tsv': 'tsv'
        }
        
        return type_mapping.get(file_extension, 'unknown')
    
    async def get_dataset_sample(
        self,
        dataset_id: str,
        n_rows: int = 10
    ) -> Dict[str, any]:
        """Get a sample of the dataset."""
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        try:
            # Read file based on type
            if dataset.file_type == 'csv':
                df = pd.read_csv(dataset.file_path, nrows=n_rows)
            elif dataset.file_type == 'excel':
                df = pd.read_excel(dataset.file_path, nrows=n_rows)
            elif dataset.file_type == 'json':
                df = pd.read_json(dataset.file_path, nrows=n_rows)
            elif dataset.file_type == 'parquet':
                df = pd.read_parquet(dataset.file_path)
            else:
                raise ValueError(f"Unsupported file type: {dataset.file_type}")
            
            # Convert to dict for JSON serialization
            sample_data = {
                "columns": df.columns.tolist(),
                "data": df.fillna("").to_dict('records'),
                "shape": df.shape,
                "dtypes": df.dtypes.astype(str).to_dict()
            }
            
            return sample_data
            
        except Exception as e:
            raise ValueError(f"Failed to read dataset sample: {str(e)}")
    
    async def refresh_profile(self, dataset_id: str) -> Dict[str, any]:
        """Refresh the profile of a dataset."""
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Re-profile the dataset
        profile_result = await self.profiler.execute(
            dataset=dataset,
            spec={"operation": "full_profile"},
            previous_results={}
        )
        
        # Update dataset with new profile info
        dataset.profile_info = profile_result.get("result", {})
        dataset.schema_info = profile_result.get("result", {}).get("schema", {})
        dataset.updated_at = datetime.utcnow()
        self.db.commit()
        
        return dataset.profile_info

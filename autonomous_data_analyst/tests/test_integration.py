import pytest
import asyncio
import tempfile
import os
import json
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.models.database import get_db, Base, User, Dataset
from app.core.security import get_password_hash
from app.services.run_service import RunService
from app.services.websocket_manager import WebSocketManager

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        db = TestingSessionLocal()
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("test_password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield user
        db.delete(user)
        db.commit()
    
    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset."""
        import pandas as pd
        
        # Create test data with various data quality issues
        df = pd.DataFrame({
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', '', None, 'David'],
            'age': [25, 30, 35, 28, 32, None, 45, 150],  # Missing and outlier
            'city': ['NYC', 'LA', 'Chicago', 'NYC', 'LA', 'Boston', 'NYC', 'LA'],
            'salary': [50000, 60000, 70000, 55000, 65000, None, 80000, 1000000],  # Missing and outlier
            'join_date': ['2020-01-01', '2019-05-15', '2018-11-30', '2021-02-28', 
                         '2020-07-12', '2017-03-25', '2019-09-10', '2016-01-01']
        })
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        # Create dataset record
        db = TestingSessionLocal()
        dataset = Dataset(
            id="integration-test-dataset",
            name="Integration Test Dataset",
            description="Dataset for integration testing",
            file_path=temp_file.name,
            file_type="csv",
            file_size=os.path.getsize(temp_file.name),
            owner_id="test-user"
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        yield dataset
        
        # Cleanup
        db.delete(dataset)
        db.commit()
        os.unlink(temp_file.name)
    
    def test_complete_analysis_workflow(self, sample_dataset):
        """Test complete analysis workflow from upload to results."""
        # Step 1: Profile the dataset
        profile_response = client.get(f"/api/profile/{sample_dataset.id}")
        assert profile_response.status_code == 401  # Expected without auth
        
        # For testing, we'll work directly with services
        db = TestingSessionLocal()
        websocket_manager = WebSocketManager()
        run_service = RunService(db, websocket_manager)
        
        # Step 2: Create analysis run
        run_id, plan = asyncio.run(run_service.create_analysis_run(
            dataset_id=sample_dataset.id,
            question="Analyze the employee data and provide insights",
            dry_run=False,
            user_id="test-user"
        ))
        
        assert run_id is not None
        assert plan is not None
        assert len(plan.steps) > 0
        
        # Step 3: Execute the run
        result = asyncio.run(run_service.execute_run(run_id))
        
        assert result is not None
        assert "summary" in result
        assert "insights" in result
        assert "recommendations" in result
        
        # Step 4: Verify run completion
        run_details = asyncio.run(run_service.get_run_with_details(run_id))
        assert run_details.status == "completed"
        assert run_details.result is not None
    
    def test_cleaning_workflow(self, sample_dataset):
        """Test data cleaning workflow."""
        db = TestingSessionLocal()
        websocket_manager = WebSocketManager()
        run_service = RunService(db, websocket_manager)
        
        # Step 1: Create cleaning plan
        from app.services.dataset_service import DatasetService
        dataset_service = DatasetService(db)
        
        plan, rationale = asyncio.run(dataset_service.create_cleaning_plan(
            dataset_id=sample_dataset.id,
            cleaning_goals=["handle_missing_values", "remove_duplicates"]
        ))
        
        assert plan is not None
        assert len(plan.steps) > 0
        assert "clean" in [step.step_type for step in plan.steps]
        
        # Step 2: Execute cleaning run
        run_id = asyncio.run(run_service.create_cleaning_run(
            dataset_id=sample_dataset.id,
            plan=plan,
            apply_changes=False,  # Don't actually modify for testing
            user_id="test-user"
        ))
        
        assert run_id is not None
        
        # Step 3: Execute the cleaning run
        result = asyncio.run(run_service.execute_run(run_id))
        
        assert result is not None
        assert "changes_made" in result
    
    def test_orchestrator_step_execution(self, sample_dataset):
        """Test orchestrator step execution."""
        from app.services.orchestrator import Orchestrator
        from app.models.schemas import Plan, StepSpec, StepType
        
        db = TestingSessionLocal()
        websocket_manager = WebSocketManager()
        orchestrator = Orchestrator(db, websocket_manager)
        
        # Create a simple plan
        plan = Plan(
            steps=[
                StepSpec(
                    step_id="step_1",
                    step_type=StepType.PROFILE,
                    spec={"operation": "basic_profile"},
                    dependencies=[]
                ),
                StepSpec(
                    step_id="step_2",
                    step_type=StepType.ANALYSIS,
                    spec={"operation": "descriptive"},
                    dependencies=["step_1"]
                )
            ]
        )
        
        # Create a test run
        from app.models.database import Run
        run = Run(
            id="orchestrator-test-run",
            question="Test orchestrator",
            plan=plan.dict(),
            status="pending",
            user_id="test-user",
            dataset_id=sample_dataset.id
        )
        db.add(run)
        db.commit()
        
        # Execute the plan
        result = asyncio.run(orchestrator.execute_plan(
            run_id=run.id,
            plan=plan,
            dry_run=True,  # Use dry run for testing
            user_id="test-user"
        ))
        
        assert result is not None
        assert "summary" in result
    
    def test_websocket_events(self, sample_dataset):
        """Test WebSocket event streaming."""
        from app.services.websocket_manager import WebSocketManager
        from app.models.schemas import WebSocketEvent, EventType
        
        websocket_manager = WebSocketManager()
        
        # Test event broadcasting
        event = WebSocketEvent(
            run_id="test-run",
            timestamp=time.time(),
            event_type=EventType.STEP_STARTED,
            step_id="step_1",
            data={"message": "Test event"}
        )
        
        # This would normally be sent over WebSocket
        # For testing, we just verify the event structure
        assert event.run_id == "test-run"
        assert event.event_type == EventType.STEP_STARTED
        assert event.step_id == "step_1"
        assert "message" in event.data
    
    def test_audit_logging(self, sample_dataset):
        """Test audit logging functionality."""
        from app.core.audit import AuditLogger
        
        db = TestingSessionLocal()
        audit_logger = AuditLogger(db)
        
        # Log an event
        audit_entry = audit_logger.log_event(
            run_id="test-run",
            event_type="step_completed",
            data={"step_id": "step_1", "result": "success"},
            user_id="test-user"
        )
        
        assert audit_entry is not None
        assert audit_entry.run_id == "test-run"
        assert audit_entry.event_type == "step_completed"
        assert audit_entry.content_hash is not None
        
        # Verify integrity
        is_valid = audit_logger.verify_integrity("test-run")
        assert is_valid
        
        # Get run history
        history = audit_logger.get_run_history("test-run")
        assert len(history) >= 1
        assert history[0].event_type == "step_completed"
    
    def test_error_handling(self, sample_dataset):
        """Test error handling in various scenarios."""
        from app.executors.base_executor import BaseExecutor
        from app.executors.profiler_executor import ProfilerExecutor
        
        db = TestingSessionLocal()
        executor = ProfilerExecutor(db)
        
        # Test with invalid dataset
        from app.models.database import Dataset
        invalid_dataset = Dataset(
            id="invalid-dataset",
            name="Invalid Dataset",
            file_path="nonexistent.csv",
            file_type="csv"
        )
        
        # Should handle file not found gracefully
        with pytest.raises(ValueError):
            asyncio.run(executor.execute(
                dataset=invalid_dataset,
                spec={"operation": "basic_profile"},
                previous_results={}
            ))
        
        # Test with invalid spec
        with pytest.raises(ValueError):
            asyncio.run(executor.execute(
                dataset=sample_dataset,
                spec={"operation": "invalid_operation"},
                previous_results={}
            ))
    
    def test_system_metrics(self, sample_dataset):
        """Test system metrics collection."""
        db = TestingSessionLocal()
        websocket_manager = WebSocketManager()
        run_service = RunService(db, websocket_manager)
        
        # Get system metrics
        metrics = asyncio.run(run_service.get_system_metrics())
        
        assert metrics is not None
        assert hasattr(metrics, 'active_runs')
        assert hasattr(metrics, 'total_runs')
        assert hasattr(metrics, 'success_rate')
        assert hasattr(metrics, 'average_duration')
        assert metrics.active_runs >= 0
        assert metrics.total_runs >= 0
        assert 0 <= metrics.success_rate <= 1
    
    def test_concurrent_runs(self, sample_dataset):
        """Test handling of concurrent runs."""
        db = TestingSessionLocal()
        websocket_manager = WebSocketManager()
        run_service = RunService(db, websocket_manager)
        
        # Create multiple runs concurrently
        tasks = []
        for i in range(3):
            task = asyncio.create_task(run_service.create_analysis_run(
                dataset_id=sample_dataset.id,
                question=f"Test question {i}",
                dry_run=True,
                user_id="test-user"
            ))
            tasks.append(task)
        
        # Wait for all to complete
        results = asyncio.gather(*tasks)
        
        # Verify all runs were created
        assert len(results) == 3
        for run_id, plan in results:
            assert run_id is not None
            assert plan is not None


class TestPerformance:
    """Performance tests."""
    
    @pytest.fixture
    def large_dataset(self):
        """Create a larger dataset for performance testing."""
        import pandas as pd
        import numpy as np
        
        # Generate larger dataset
        np.random.seed(42)
        n_rows = 10000
        
        df = pd.DataFrame({
            'id': range(n_rows),
            'value1': np.random.normal(100, 15, n_rows),
            'value2': np.random.exponential(50, n_rows),
            'category': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
            'date': pd.date_range('2020-01-01', periods=n_rows, freq='H')
        })
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        # Create dataset record
        db = TestingSessionLocal()
        dataset = Dataset(
            id="performance-test-dataset",
            name="Performance Test Dataset",
            file_path=temp_file.name,
            file_type="csv",
            file_size=os.path.getsize(temp_file.name),
            owner_id="test-user"
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        yield dataset
        
        # Cleanup
        db.delete(dataset)
        db.commit()
        os.unlink(temp_file.name)
    
    def test_profiling_performance(self, large_dataset):
        """Test profiling performance on larger dataset."""
        from app.executors.profiler_executor import ProfilerExecutor
        import time
        
        db = TestingSessionLocal()
        executor = ProfilerExecutor(db)
        
        start_time = time.time()
        result = asyncio.run(executor.execute(
            dataset=large_dataset,
            spec={"operation": "basic_profile"},
            previous_results={}
        ))
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result["success"]
        assert execution_time < 30  # Should complete within 30 seconds
        
        print(f"Profiling {large_dataset.file_size} bytes took {execution_time:.2f} seconds")
    
    def test_analysis_performance(self, large_dataset):
        """Test analysis performance on larger dataset."""
        from app.executors.analyzer_executor import AnalyzerExecutor
        import time
        
        db = TestingSessionLocal()
        executor = AnalyzerExecutor(db)
        
        start_time = time.time()
        result = asyncio.run(executor.execute(
            dataset=large_dataset,
            spec={"operation": "descriptive"},
            previous_results={}
        ))
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result["success"]
        assert execution_time < 60  # Should complete within 60 seconds
        
        print(f"Analysis took {execution_time:.2f} seconds")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

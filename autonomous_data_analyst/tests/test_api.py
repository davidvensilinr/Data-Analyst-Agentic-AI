import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
import json

from app.api.main import app
from app.models.database import get_db, Base
from app.core.security import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

class TestAPI:
    """Test API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_upload_dataset(self):
        """Test dataset upload endpoint."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = client.post(
                    "/api/upload",
                    files={"file": ("test.csv", f, "text/csv")},
                    data={"name": "Test Dataset", "description": "Test dataset"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert "dataset_id" in data
            assert data["name"] == "Test Dataset"
            assert data["file_type"] == "csv"
        
        finally:
            os.unlink(temp_file)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a valid dataset file")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = client.post(
                    "/api/upload",
                    files={"file": ("test.txt", f, "text/plain")},
                    data={"name": "Invalid Dataset"}
                )
            
            assert response.status_code == 400
        
        finally:
            os.unlink(temp_file)
    
    def test_get_datasets_empty(self):
        """Test getting datasets when none exist."""
        response = client.get("/api/datasets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_ask_question_no_dataset(self):
        """Test asking question without valid dataset."""
        response = client.post(
            "/api/ask",
            json={
                "question": "What is the average age?",
                "dataset_id": "invalid-dataset-id"
            }
        )
        assert response.status_code == 401  # Unauthorized without auth
    
    def test_profile_invalid_dataset(self):
        """Test profiling invalid dataset."""
        response = client.get("/api/profile/invalid-dataset-id")
        assert response.status_code == 401  # Unauthorized without auth
    
    def test_clean_plan_invalid_dataset(self):
        """Test creating cleaning plan for invalid dataset."""
        response = client.post(
            "/api/clean/plan",
            json={
                "dataset_id": "invalid-dataset-id",
                "cleaning_goals": ["remove_duplicates"]
            }
        )
        assert response.status_code == 401  # Unauthorized without auth
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/api/metrics")
        assert response.status_code == 401  # Unauthorized without auth


class TestValidation:
    """Test input validation."""
    
    def test_question_validation(self):
        """Test question validation."""
        from app.core.validation import InputValidator
        
        # Valid question
        valid_question = InputValidator.validate_question("What is the average age?")
        assert valid_question == "What is the average age?"
        
        # Empty question
        with pytest.raises(ValidationError):
            InputValidator.validate_question("")
        
        # Too long question
        with pytest.raises(ValidationError):
            InputValidator.validate_question("a" * 2001)
        
        # Dangerous content
        with pytest.raises(ValidationError):
            InputValidator.validate_question("DROP TABLE users")
    
    def test_sql_validation(self):
        """Test SQL validation."""
        from app.core.validation import InputValidator
        
        # Valid SELECT query
        valid_spec = {"query": "SELECT * FROM data WHERE age > 25"}
        InputValidator.validate_step_spec("sql", valid_spec)
        
        # Invalid SQL with DROP
        with pytest.raises(ValidationError):
            invalid_spec = {"query": "DROP TABLE data"}
            InputValidator.validate_step_spec("sql", invalid_spec)
        
        # Multiple statements
        with pytest.raises(ValidationError):
            invalid_spec = {"query": "SELECT * FROM data; DROP TABLE data;"}
            InputValidator.validate_step_spec("sql", invalid_spec)
    
    def test_cleaning_validation(self):
        """Test cleaning specification validation."""
        from app.core.validation import InputValidator
        
        # Valid cleaning spec
        valid_spec = {
            "operations": ["handle_missing_values", "remove_duplicates"],
            "missing_strategy": "impute_mean"
        }
        InputValidator.validate_step_spec("clean", valid_spec)
        
        # Invalid operation
        with pytest.raises(ValidationError):
            invalid_spec = {"operations": ["invalid_operation"]}
            InputValidator.validate_step_spec("clean", invalid_spec)
    
    def test_visualization_validation(self):
        """Test visualization specification validation."""
        from app.core.validation import InputValidator
        
        # Valid visualization spec
        valid_spec = {
            "chart_type": "histogram",
            "column": "age",
            "bins": 20
        }
        InputValidator.validate_step_spec("visualization", valid_spec)
        
        # Invalid chart type
        with pytest.raises(ValidationError):
            invalid_spec = {"chart_type": "invalid_chart"}
            InputValidator.validate_step_spec("visualization", invalid_spec)
        
        # Invalid bins
        with pytest.raises(ValidationError):
            invalid_spec = {"chart_type": "histogram", "bins": 200}
            InputValidator.validate_step_spec("visualization", invalid_spec)


class TestExecutors:
    """Test step executors."""
    
    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset for testing."""
        import pandas as pd
        from app.models.database import Dataset
        
        # Create test data
        df = pd.DataFrame({
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'age': [25, 30, 35, 28, 32],
            'city': ['NYC', 'LA', 'Chicago', 'NYC', 'LA'],
            'salary': [50000, 60000, 70000, 55000, 65000]
        })
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        # Create dataset object
        dataset = Dataset(
            id="test-dataset",
            name="Test Dataset",
            file_path=temp_file.name,
            file_type="csv",
            file_size=os.path.getsize(temp_file.name)
        )
        
        yield dataset
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_profiler_executor(self, sample_dataset):
        """Test profiler executor."""
        from app.executors.profiler_executor import ProfilerExecutor
        
        executor = ProfilerExecutor(TestingSessionLocal())
        
        # Test basic profile
        result = asyncio.run(executor.execute(
            dataset=sample_dataset,
            spec={"operation": "basic_profile"},
            previous_results={}
        ))
        
        assert result["success"]
        assert "result" in result
        assert "schema" in result["result"]
        assert "basic_stats" in result["result"]
    
    def test_analyzer_executor(self, sample_dataset):
        """Test analyzer executor."""
        from app.executors.analyzer_executor import AnalyzerExecutor
        
        executor = AnalyzerExecutor(TestingSessionLocal())
        
        # Test descriptive analysis
        result = asyncio.run(executor.execute(
            dataset=sample_dataset,
            spec={"operation": "descriptive"},
            previous_results={}
        ))
        
        assert result["success"]
        assert "result" in result
        assert "overall_statistics" in result["result"]
    
    def test_visualizer_executor(self, sample_dataset):
        """Test visualizer executor."""
        from app.executors.visualizer_executor import VisualizerExecutor
        
        executor = VisualizerExecutor(TestingSessionLocal())
        
        # Test histogram creation
        result = asyncio.run(executor.execute(
            dataset=sample_dataset,
            spec={"chart_type": "histogram", "column": "age"},
            previous_results={}
        ))
        
        assert result["success"]
        assert "result" in result
        assert "chart" in result["result"]
        assert result["result"]["chart"]["type"] == "histogram"


class TestPlanner:
    """Test LLM planner."""
    
    def test_mock_planner(self):
        """Test mock planner."""
        from app.planners.llm_planner import LLMPlanner
        from app.models.database import Dataset
        
        planner = LLMPlanner()
        
        # Create mock dataset
        dataset = Dataset(
            id="test-dataset",
            name="Test Dataset",
            file_path="test.csv",
            file_type="csv"
        )
        
        # Test plan creation
        plan = asyncio.run(planner.create_plan(
            question="What is the average age?",
            dataset=dataset,
            db=TestingSessionLocal()
        ))
        
        assert plan is not None
        assert hasattr(plan, 'steps')
        assert len(plan.steps) > 0


class TestSecurity:
    """Test security features."""
    
    def test_password_hashing(self):
        """Test password hashing."""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        from app.core.validation import SecurityValidator
        
        # Safe query
        safe_query = "SELECT * FROM users WHERE age > 25"
        assert not SecurityValidator.check_sql_injection(safe_query)
        
        # Dangerous queries
        dangerous_queries = [
            "SELECT * FROM users; DROP TABLE users;",
            "SELECT * FROM users WHERE 1=1 OR '1'='1'",
            "SELECT * FROM users UNION SELECT * FROM passwords",
            "EXEC xp_cmdshell 'dir'"
        ]
        
        for query in dangerous_queries:
            assert SecurityValidator.check_sql_injection(query)
    
    def test_api_key_validation(self):
        """Test API key validation."""
        from app.core.validation import SecurityValidator
        
        # Valid API key
        valid_key = "test_api_key_12345678"
        assert SecurityValidator.validate_api_key(valid_key)
        
        # Invalid API keys
        invalid_keys = ["", "short", "key with spaces", "key$with$symbols"]
        
        for key in invalid_keys:
            assert not SecurityValidator.validate_api_key(key)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import json
import re
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.database import Dataset, Run
from app.models.schemas import Plan, StepSpec, StepType
from app.llm.base_llm import BaseLLM
from app.llm.openai_llm import OpenAILLM
from app.llm.anthropic_llm import AnthropicLLM
from app.llm.mock_llm import MockLLM
from config.settings import settings


class LLMPlanner:
    """LLM-based planner for creating analysis plans."""
    
    def __init__(self):
        # Initialize LLM based on settings
        if settings.MOCK_LLM_MODE:
            self.llm = MockLLM()
        elif settings.DEFAULT_LLM_PROVIDER == "openai":
            self.llm = OpenAILLM()
        elif settings.DEFAULT_LLM_PROVIDER == "anthropic":
            self.llm = AnthropicLLM()
        else:
            self.llm = MockLLM()  # Fallback to mock
    
    async def create_plan(
        self,
        question: str,
        dataset: Dataset,
        db: Session
    ) -> Plan:
        """Create an analysis plan based on the question and dataset."""
        
        # Get dataset schema and profile info
        schema_info = dataset.schema_info or {}
        profile_info = dataset.profile_info or {}
        
        # Get recent runs for context
        recent_runs = self._get_recent_runs(db, dataset.id, limit=3)
        
        # Build prompt
        prompt = self._build_planning_prompt(
            question=question,
            dataset_name=dataset.name,
            schema_info=schema_info,
            profile_info=profile_info,
            recent_runs=recent_runs
        )
        
        # Get plan from LLM
        llm_response = await self.llm.generate_response(
            prompt=prompt,
            max_tokens=settings.MAX_TOKENS_PER_REQUEST,
            temperature=settings.TEMPERATURE
        )
        
        # Parse plan
        plan = self._parse_plan_response(llm_response)
        
        # Verify plan with critic
        verified_plan = await self._verify_plan(
            plan=plan,
            question=question,
            dataset=dataset,
            db=db
        )
        
        return verified_plan
    
    async def create_cleaning_plan(
        self,
        dataset: Dataset,
        profile_info: Dict[str, Any],
        cleaning_goals: Optional[List[str]] = None,
        db: Session = None
    ) -> Plan:
        """Create a data cleaning plan."""
        
        # Build cleaning prompt
        prompt = self._build_cleaning_prompt(
            dataset_name=dataset.name,
            schema_info=dataset.schema_info or {},
            profile_info=profile_info,
            cleaning_goals=cleaning_goals or []
        )
        
        # Get plan from LLM
        llm_response = await self.llm.generate_response(
            prompt=prompt,
            max_tokens=settings.MAX_TOKENS_PER_REQUEST,
            temperature=settings.TEMPERATURE
        )
        
        # Parse plan
        plan = self._parse_plan_response(llm_response)
        
        return plan
    
    def _get_recent_runs(self, db: Session, dataset_id: str, limit: int = 3) -> List[Dict]:
        """Get recent runs for the dataset."""
        runs = db.query(Run).filter(
            Run.dataset_id == dataset_id,
            Run.status == "completed"
        ).order_by(Run.created_at.desc()).limit(limit).all()
        
        return [
            {
                "question": run.question,
                "plan": run.plan,
                "result": run.result
            }
            for run in runs
        ]
    
    def _build_planning_prompt(
        self,
        question: str,
        dataset_name: str,
        schema_info: Dict[str, Any],
        profile_info: Dict[str, Any],
        recent_runs: List[Dict]
    ) -> str:
        """Build the planning prompt."""
        
        prompt = f"""You are an expert data analyst creating a step-by-step analysis plan. 

DATASET: {dataset_name}

SCHEMA:
{json.dumps(schema_info, indent=2)}

DATA PROFILE:
{json.dumps(profile_info, indent=2)}

RECENT ANALYSES:
{json.dumps(recent_runs, indent=2)}

USER QUESTION: {question}

Create a detailed plan to answer the user's question. The plan should be a sequence of steps that will:
1. Profile the data if needed
2. Clean the data if necessary
3. Perform the analysis
4. Generate visualizations
5. Provide insights and recommendations

Available step types:
- profile: Analyze data structure, statistics, and quality
- clean: Clean and preprocess data (handle missing values, outliers, etc.)
- sql: Execute SQL queries for analysis
- analysis: Perform statistical analysis, correlations, etc.
- visualization: Create charts and visualizations
- anomaly: Detect anomalies and outliers
- recommendation: Generate insights and recommendations

Return your response as a JSON object with this structure:
{{
  "steps": [
    {{
      "step_id": "step_1",
      "step_type": "profile",
      "spec": {{"operation": "basic_profile"}},
      "dependencies": []
    }},
    {{
      "step_id": "step_2", 
      "step_type": "clean",
      "spec": {{"operations": ["handle_missing_values", "remove_duplicates"]}},
      "dependencies": ["step_1"]
    }}
  ],
  "estimated_duration": 60,
  "confidence": 0.85
}}

Make sure each step has:
- A unique step_id
- A valid step_type from the list above
- A spec object with the details of what to do
- A dependencies list (can be empty for first step)

Be specific about what each step should do. For cleaning steps, specify exact operations. For analysis steps, specify the type of analysis. For visualization steps, specify chart types and variables."""
        
        return prompt
    
    def _build_cleaning_prompt(
        self,
        dataset_name: str,
        schema_info: Dict[str, Any],
        profile_info: Dict[str, Any],
        cleaning_goals: List[str]
    ) -> str:
        """Build the cleaning prompt."""
        
        prompt = f"""You are a data quality expert creating a data cleaning plan.

DATASET: {dataset_name}

SCHEMA:
{json.dumps(schema_info, indent=2)}

DATA PROFILE:
{json.dumps(profile_info, indent=2)}

CLEANING GOALS:
{json.dumps(cleaning_goals, indent=2)}

Create a plan to clean this dataset. Focus on:
1. Handling missing values
2. Removing duplicates
3. Fixing data types
4. Handling outliers
5. Standardizing formats

Available cleaning operations:
- handle_missing_values: Remove or impute missing values
- remove_duplicates: Remove duplicate rows
- fix_data_types: Convert columns to appropriate types
- handle_outliers: Detect and handle outliers
- standardize_formats: Standardize text, dates, etc.
- validate_data: Check data validity and constraints

Return your response as a JSON object with this structure:
{{
  "steps": [
    {{
      "step_id": "clean_1",
      "step_type": "clean",
      "spec": {{
        "operations": ["handle_missing_values", "remove_duplicates"],
        "missing_strategy": "impute_mean",
        "duplicate_subset": ["id", "email"]
      }},
      "dependencies": []
    }}
  ],
  "estimated_duration": 30,
  "confidence": 0.9
}}

Be specific about the cleaning operations and their parameters."""
        
        return prompt
    
    def _parse_plan_response(self, llm_response: str) -> Plan:
        """Parse the LLM response into a Plan object."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\\{.*\\}', llm_response, re.DOTALL)
            if json_match:
                plan_json = json.loads(json_match.group())
            else:
                # Try parsing the entire response as JSON
                plan_json = json.loads(llm_response)
            
            # Validate and create Plan object
            steps = []
            for i, step_data in enumerate(plan_json.get("steps", [])):
                step = StepSpec(
                    step_id=step_data.get("step_id", f"step_{i+1}"),
                    step_type=StepType(step_data.get("step_type")),
                    spec=step_data.get("spec", {}),
                    dependencies=step_data.get("dependencies", [])
                )
                steps.append(step)
            
            return Plan(
                steps=steps,
                estimated_duration=plan_json.get("estimated_duration"),
                confidence=plan_json.get("confidence")
            )
            
        except Exception as e:
            # Fallback to a basic plan
            return Plan(
                steps=[
                    StepSpec(
                        step_id="fallback_profile",
                        step_type=StepType.PROFILE,
                        spec={"operation": "basic_profile"},
                        dependencies=[]
                    ),
                    StepSpec(
                        step_id="fallback_analysis",
                        step_type=StepType.ANALYSIS,
                        spec={"operation": "basic_analysis"},
                        dependencies=["fallback_profile"]
                    )
                ],
                estimated_duration=60,
                confidence=0.5
            )
    
    async def _verify_plan(
        self,
        plan: Plan,
        question: str,
        dataset: Dataset,
        db: Session
    ) -> Plan:
        """Verify the plan using a critic LLM."""
        
        # Build verification prompt
        verification_prompt = f"""You are a critical reviewer of data analysis plans.

ORIGINAL QUESTION: {question}

DATASET: {dataset.name}

PROPOSED PLAN:
{json.dumps(plan.dict(), indent=2)}

Review this plan for:
1. Safety and appropriateness
2. Logical flow and dependencies
3. Completeness for answering the question
4. Efficiency and cost-effectiveness
5. Potential risks or issues

Return your response as JSON:
{{
  "approved": true/false,
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "modified_plan": {{...}} // Only if changes needed
}}

If the plan is good, set approved=true and leave modified_plan empty.
If changes are needed, provide a modified plan."""
        
        # Get verification from LLM
        verification_response = await self.llm.generate_response(
            prompt=verification_prompt,
            max_tokens=2000,
            temperature=0.1  # Lower temperature for more consistent verification
        )
        
        try:
            # Parse verification response
            json_match = re.search(r'\\{.*\\}', verification_response, re.DOTALL)
            if json_match:
                verification = json.loads(json_match.group())
            else:
                verification = json.loads(verification_response)
            
            # If plan is approved, return as-is
            if verification.get("approved", False):
                return plan
            
            # If there's a modified plan, use that
            if "modified_plan" in verification and verification["modified_plan"]:
                modified_plan_data = verification["modified_plan"]
                steps = []
                for i, step_data in enumerate(modified_plan_data.get("steps", [])):
                    step = StepSpec(
                        step_id=step_data.get("step_id", f"step_{i+1}"),
                        step_type=StepType(step_data.get("step_type")),
                        spec=step_data.get("spec", {}),
                        dependencies=step_data.get("dependencies", [])
                    )
                    steps.append(step)
                
                return Plan(
                    steps=steps,
                    estimated_duration=modified_plan_data.get("estimated_duration"),
                    confidence=modified_plan_data.get("confidence")
                )
            
            # If no modified plan but issues exist, add a safety step
            if verification.get("issues"):
                safety_step = StepSpec(
                    step_id="safety_check",
                    step_type=StepType.RECOMMENDATION,
                    spec={
                        "operation": "safety_review",
                        "issues": verification.get("issues", []),
                        "suggestions": verification.get("suggestions", [])
                    },
                    dependencies=[]
                )
                plan.steps.insert(0, safety_step)
                plan.confidence = max(0.1, plan.confidence - 0.2)
            
            return plan
            
        except Exception as e:
            # If verification fails, return original plan with reduced confidence
            plan.confidence = max(0.1, plan.confidence - 0.1)
            return plan

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.database import Run, RunStep, Dataset, User
from app.models.schemas import StepType, StepStatus, RunStatus, Plan, StepSpec
from app.core.audit import AuditLogger, StepAuditor
from app.services.websocket_manager import WebSocketManager
from app.executors.base_executor import BaseExecutor
from app.executors.profiler_executor import ProfilerExecutor
from app.executors.cleaner_executor import CleanerExecutor
from app.executors.sql_executor import SQLExecutor
from app.executors.analyzer_executor import AnalyzerExecutor
from app.executors.visualizer_executor import VisualizerExecutor
from app.executors.anomaly_executor import AnomalyExecutor
from app.executors.recommendation_executor import RecommendationExecutor
from config.settings import settings
import traceback


class Orchestrator:
    """Orchestrates the execution of analysis plans."""
    
    def __init__(self, db: Session, websocket_manager: WebSocketManager):
        self.db = db
        self.websocket_manager = websocket_manager
        self.audit_logger = AuditLogger(db)
        self.step_auditor = StepAuditor(self.audit_logger)
        
        # Initialize executors
        self.executors = {
            StepType.PROFILE: ProfilerExecutor(db),
            StepType.CLEAN: CleanerExecutor(db),
            StepType.SQL: SQLExecutor(db),
            StepType.ANALYSIS: AnalyzerExecutor(db),
            StepType.VISUALIZATION: VisualizerExecutor(db),
            StepType.ANOMALY: AnomalyExecutor(db),
            StepType.RECOMMENDATION: RecommendationExecutor(db)
        }
    
    async def execute_plan(
        self,
        run_id: str,
        plan: Plan,
        dry_run: bool = False,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Execute a plan and return results."""
        run = self.db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        dataset = self.db.query(Dataset).filter(Dataset.id == run.dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {run.dataset_id} not found")
        
        try:
            # Update run status
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            self.db.commit()
            
            # Send run started event
            await self.websocket_manager.send_run_started(
                run_id=run_id,
                question=run.question,
                plan=plan.dict()
            )
            
            # Log run started
            await self.step_auditor.log_run_started(
                run_id=run_id,
                question=run.question,
                dataset_id=dataset.id,
                plan=plan.dict(),
                user_id=user_id
            )
            
            # Execute steps in order
            results = {}
            step_metrics = {}
            
            for step_spec in plan.steps:
                try:
                    # Check if step has dependencies
                    if step_spec.dependencies:
                        dependencies_met = all(
                            dep_id in results and results[dep_id].get("success", False)
                            for dep_id in step_spec.dependencies
                        )
                        if not dependencies_met:
                            raise ValueError(f"Dependencies not met for step {step_spec.step_id}")
                    
                    # Execute step
                    step_result = await self.execute_step(
                        run_id=run_id,
                        step_spec=step_spec,
                        dataset=dataset,
                        previous_results=results,
                        dry_run=dry_run,
                        user_id=user_id
                    )
                    
                    results[step_spec.step_id] = step_result
                    
                    # If this is a dry run, stop after first step
                    if dry_run:
                        break
                    
                    # Check if we should continue (human approval for destructive operations)
                    if step_spec.step_type == StepType.CLEAN and settings.REQUIRE_HUMAN_APPROVAL:
                        # In a real implementation, this would wait for human approval
                        # For now, we'll continue automatically
                        pass
                    
                except Exception as e:
                    # Log step failure
                    await self.websocket_manager.send_step_failed(
                        run_id=run_id,
                        step_id=step_spec.step_id,
                        step_type=step_spec.step_type.value,
                        error_message=str(e)
                    )
                    
                    await self.step_auditor.log_step_failed(
                        run_id=run_id,
                        step_id=step_spec.step_id,
                        step_type=step_spec.step_type.value,
                        error_message=str(e),
                        user_id=user_id
                    )
                    
                    # Fail the entire run
                    run.status = RunStatus.FAILED
                    run.completed_at = datetime.utcnow()
                    self.db.commit()
                    
                    await self.websocket_manager.send_run_failed(
                        run_id=run_id,
                        error_message=f"Step {step_spec.step_id} failed: {str(e)}"
                    )
                    
                    await self.step_auditor.log_run_failed(
                        run_id=run_id,
                        error_message=f"Step {step_spec.step_id} failed: {str(e)}",
                        user_id=user_id
                    )
                    
                    raise e
            
            # Compile final result
            final_result = self.compile_final_result(results, plan)
            
            # Update run with results
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            run.result = final_result
            run.metrics = step_metrics
            self.db.commit()
            
            # Send run completed event
            await self.websocket_manager.send_run_completed(
                run_id=run_id,
                result=final_result,
                metrics=step_metrics
            )
            
            await self.step_auditor.log_run_completed(
                run_id=run_id,
                result=final_result,
                metrics=step_metrics,
                user_id=user_id
            )
            
            return final_result
            
        except Exception as e:
            # Ensure run is marked as failed
            run.status = RunStatus.FAILED
            run.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Send run failed event
            await self.websocket_manager.send_run_failed(
                run_id=run_id,
                error_message=str(e)
            )
            
            await self.step_auditor.log_run_failed(
                run_id=run_id,
                error_message=str(e),
                user_id=user_id
            )
            
            raise e
    
    async def execute_step(
        self,
        run_id: str,
        step_spec: StepSpec,
        dataset: Dataset,
        previous_results: Dict[str, Any],
        dry_run: bool = False,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Execute a single step."""
        step_start_time = datetime.utcnow()
        
        # Create step record
        step = RunStep(
            run_id=run_id,
            step_id=step_spec.step_id,
            step_type=step_spec.step_type.value,
            spec=step_spec.spec,
            status=StepStatus.RUNNING,
            started_at=step_start_time
        )
        self.db.add(step)
        self.db.commit()
        
        try:
            # Send step started event
            await self.websocket_manager.send_step_started(
                run_id=run_id,
                step_id=step_spec.step_id,
                step_type=step_spec.step_type.value,
                spec=step_spec.spec
            )
            
            # Log step started
            await self.step_auditor.log_step_started(
                run_id=run_id,
                step_id=step_spec.step_id,
                step_type=step_spec.step_type.value,
                spec=step_spec.spec,
                user_id=user_id
            )
            
            # Get executor for this step type
            executor = self.executors.get(step_spec.step_type)
            if not executor:
                raise ValueError(f"No executor found for step type {step_spec.step_type}")
            
            # Execute the step
            if dry_run:
                # For dry run, just return a mock result
                result = {
                    "success": True,
                    "message": f"Dry run: would execute {step_spec.step_type} step",
                    "spec": step_spec.spec
                }
                model_prompt = None
                model_output = None
                tool_call = None
                tool_result = None
                rationale = f"Dry run execution of {step_spec.step_type} step"
                confidence = 1.0
            else:
                # Actual execution
                execution_result = await executor.execute(
                    dataset=dataset,
                    spec=step_spec.spec,
                    previous_results=previous_results
                )
                
                result = execution_result.get("result", {})
                model_prompt = execution_result.get("model_prompt")
                model_output = execution_result.get("model_output")
                tool_call = execution_result.get("tool_call")
                tool_result = execution_result.get("tool_result")
                rationale = execution_result.get("rationale")
                confidence = execution_result.get("confidence")
            
            # Update step record
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            step.result = result
            step.model_prompt = model_prompt
            step.model_output = model_output
            step.tool_call = tool_call
            step.tool_result = tool_result
            step.rationale = rationale
            step.confidence = confidence
            self.db.commit()
            
            # Send step completed event
            await self.websocket_manager.send_step_completed(
                run_id=run_id,
                step_id=step_spec.step_id,
                step_type=step_spec.step_type.value,
                result=result,
                confidence=confidence,
                rationale=rationale
            )
            
            # Log step completed
            await self.step_auditor.log_step_completed(
                run_id=run_id,
                step_id=step_spec.step_id,
                step_type=step_spec.step_type.value,
                result=result,
                model_prompt=model_prompt,
                model_output=model_output,
                tool_call=tool_call,
                tool_result=tool_result,
                rationale=rationale,
                confidence=confidence,
                user_id=user_id
            )
            
            return {
                "success": True,
                "result": result,
                "confidence": confidence,
                "rationale": rationale,
                "duration": (datetime.utcnow() - step_start_time).total_seconds()
            }
            
        except Exception as e:
            # Update step record with error
            step.status = StepStatus.FAILED
            step.completed_at = datetime.utcnow()
            step.error_message = str(e)
            self.db.commit()
            
            # Re-raise exception
            raise e
    
    def compile_final_result(self, step_results: Dict[str, Any], plan: Plan) -> Dict[str, Any]:
        """Compile final result from step results."""
        final_result = {
            "summary": "",
            "insights": [],
            "recommendations": [],
            "charts": [],
            "tables": [],
            "confidence": 0.0,
            "step_results": step_results
        }
        
        # Extract insights from analysis steps
        insights = []
        recommendations = []
        charts = []
        tables = []
        confidences = []
        
        for step_id, step_result in step_results.items():
            if step_result.get("success"):
                result = step_result.get("result", {})
                
                # Collect insights
                if "insights" in result:
                    insights.extend(result["insights"])
                
                # Collect recommendations
                if "recommendations" in result:
                    recommendations.extend(result["recommendations"])
                
                # Collect charts
                if "charts" in result:
                    charts.extend(result["charts"])
                
                # Collect tables
                if "tables" in result:
                    tables.extend(result["tables"])
                
                # Collect confidence scores
                if "confidence" in step_result:
                    confidences.append(step_result["confidence"])
        
        # Compile summary
        final_result["insights"] = insights
        final_result["recommendations"] = recommendations
        final_result["charts"] = charts
        final_result["tables"] = tables
        
        # Calculate overall confidence
        if confidences:
            final_result["confidence"] = sum(confidences) / len(confidences)
        else:
            final_result["confidence"] = 0.5
        
        # Generate summary
        if insights:
            final_result["summary"] = f"Analysis completed with {len(insights)} key insights and {len(recommendations)} recommendations."
        else:
            final_result["summary"] = "Analysis completed successfully."
        
        return final_result

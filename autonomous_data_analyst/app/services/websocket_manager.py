import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from app.models.schemas import WebSocketEvent, EventType


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections: {run_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.connection_counter = 0
    
    async def connect(self, websocket: WebSocket, run_id: str):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        
        # Generate unique connection ID
        connection_id = f"conn_{self.connection_counter}"
        self.connection_counter += 1
        
        # Store connection
        if run_id not in self.active_connections:
            self.active_connections[run_id] = {}
        self.active_connections[run_id][connection_id] = websocket
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "connection_id": connection_id,
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        return connection_id
    
    def disconnect(self, run_id: str, connection_id: str):
        """Remove a WebSocket connection."""
        if run_id in self.active_connections:
            if connection_id in self.active_connections[run_id]:
                del self.active_connections[run_id][connection_id]
            
            # Clean up empty run entries
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def broadcast_to_run(self, run_id: str, event: WebSocketEvent):
        """Broadcast an event to all connections for a run."""
        if run_id not in self.active_connections:
            return
        
        message = {
            "run_id": event.run_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "step_id": event.step_id,
            "data": event.data
        }
        
        # Create a list of connections to avoid modification during iteration
        connections = list(self.active_connections[run_id].values())
        connection_ids = list(self.active_connections[run_id].keys())
        
        for i, websocket in enumerate(connections):
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                # Remove failed connection
                connection_id = connection_ids[i]
                self.disconnect(run_id, connection_id)
                print(f"Removed failed connection {connection_id}: {e}")
    
    async def send_step_started(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        spec: dict
    ):
        """Send step started event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_STARTED,
            step_id=step_id,
            data={
                "step_type": step_type,
                "spec": spec
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_step_completed(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        result: dict,
        confidence: float = None,
        rationale: str = None
    ):
        """Send step completed event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_COMPLETED,
            step_id=step_id,
            data={
                "step_type": step_type,
                "result": result,
                "confidence": confidence,
                "rationale": rationale
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_step_failed(
        self,
        run_id: str,
        step_id: str,
        step_type: str,
        error_message: str
    ):
        """Send step failed event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.STEP_FAILED,
            step_id=step_id,
            data={
                "step_type": step_type,
                "error_message": error_message
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_run_started(
        self,
        run_id: str,
        question: str,
        plan: dict
    ):
        """Send run started event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.RUN_STARTED,
            data={
                "question": question,
                "plan": plan
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_run_completed(
        self,
        run_id: str,
        result: dict,
        metrics: dict
    ):
        """Send run completed event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.RUN_COMPLETED,
            data={
                "result": result,
                "metrics": metrics
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_run_failed(
        self,
        run_id: str,
        error_message: str
    ):
        """Send run failed event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.RUN_FAILED,
            data={
                "error_message": error_message
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    async def send_plan_updated(
        self,
        run_id: str,
        plan: dict
    ):
        """Send plan updated event."""
        event = WebSocketEvent(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            event_type=EventType.PLAN_UPDATED,
            data={
                "plan": plan
            }
        )
        await self.broadcast_to_run(run_id, event)
    
    def get_connection_count(self, run_id: str = None) -> int:
        """Get number of active connections."""
        if run_id:
            return len(self.active_connections.get(run_id, {}))
        else:
            return sum(len(conns) for conns in self.active_connections.values())
    
    def get_active_runs(self) -> List[str]:
        """Get list of runs with active connections."""
        return list(self.active_connections.keys())

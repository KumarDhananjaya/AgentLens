import json
import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from .server import manager

class AgentLensCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that pushes LangGraph/LangChain events to the AgentLens WebSocket manager.
    """
    
    async def _emit(self, event: Dict[str, Any]):
        await manager.broadcast(json.dumps(event))

    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        node_id = None
        # LangGraph typically puts different identifiers in metadata
        if metadata:
            if "langgraph_node" in metadata:
                node_id = metadata["langgraph_node"]
            
        event = {
            "type": "chain_start",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "node_id": node_id,
            "tags": tags,
             # Optionally serialize inputs if needed for UI details
        }
        await self._emit(event)

    async def on_chain_end(
        self, outputs: Dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        event = {
            "type": "chain_end",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            # Optionally serialize outputs
        }
        await self._emit(event)
        
    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        event = {
            "type": "tool_start",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "name": serialized.get("name"),
            "input": input_str
        }
        await self._emit(event)

    async def on_tool_end(
        self, output: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        event = {
            "type": "tool_end",
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "output": output
        }
        await self._emit(event)

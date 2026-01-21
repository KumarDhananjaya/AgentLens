import os
import json
import asyncio
from typing import Any, List
from .parser import parse_langgraph

# Global manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Any] = [] # WebSocket objects

    async def connect(self, websocket: Any):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: Any):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Broadcast to all connected clients
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Handle disconnection or errors gracefully
                pass

manager = ConnectionManager()

class Server:
    @staticmethod
    def attach_fastapi(app: Any, graph: Any, route: str):
        from fastapi import APIRouter, WebSocket, WebSocketDisconnect
        from fastapi.responses import JSONResponse
        from fastapi.staticfiles import StaticFiles
        
        router = APIRouter(prefix=route)

        @router.get("/schema")
        async def get_schema():
            return parse_langgraph(graph)

        @router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive, maybe listen for ping/commands
                    data = await websocket.receive_text()
            except WebSocketDisconnect:
                manager.disconnect(websocket)
            except Exception:
                manager.disconnect(websocket)

        app.include_router(router)
        
        # Mount static files
        frontend_path = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(frontend_path):
            app.mount(route, StaticFiles(directory=frontend_path, html=True), name="agentlens")

    @staticmethod
    def attach_flask(app: Any, graph: Any, route: str):
        # NOTE: Flask WebSocket support requires flask-sock or similar. 
        # For now, we focus on FastAPI for streaming support as per plan.
        from flask import jsonify, send_from_directory
        
        @app.route(f"{route}/schema")
        def get_schema():
            return jsonify(parse_langgraph(graph))

        # Serve static files
        frontend_path = os.path.join(os.path.dirname(__file__), "static")
        
        @app.route(f"{route}/", defaults={"path": ""})
        @app.route(f"{route}/<path:path>")
        def serve_static(path):
            if not path or path == "":
                return send_from_directory(frontend_path, "index.html")
            return send_from_directory(frontend_path, path)

def attach(app: Any, graph: Any, route: str = "/agentlens"):
    """
    Auto-detects the app type and attaches the visualizer.
    """
    app_type = type(app).__name__
    
    if app_type == "FastAPI":
        Server.attach_fastapi(app, graph, route)
    elif app_type == "Flask":
        Server.attach_flask(app, graph, route)
    else:
        # Try checking modules if class name isn't enough
        module_name = type(app).__module__
        if "fastapi" in module_name:
            Server.attach_fastapi(app, graph, route)
        elif "flask" in module_name:
            Server.attach_flask(app, graph, route)
        else:
            raise ValueError(f"Unsupported app type: {app_type}. AgentLens currently supports FastAPI and Flask.")

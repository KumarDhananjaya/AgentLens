import os
import json
from typing import Any
from .parser import parse_langgraph

class Server:
    @staticmethod
    def attach_fastapi(app: Any, graph: Any, route: str):
        from fastapi import APIRouter
        from fastapi.responses import JSONResponse
        from fastapi.staticfiles import StaticFiles
        
        router = APIRouter(prefix=route)

        @router.get("/schema")
        async def get_schema():
            return parse_langgraph(graph)

        app.include_router(router)
        
        # Mount static files
        frontend_path = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(frontend_path):
            app.mount(route, StaticFiles(directory=frontend_path, html=True), name="agentlens")

    @staticmethod
    def attach_flask(app: Any, graph: Any, route: str):
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

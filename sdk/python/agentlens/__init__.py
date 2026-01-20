from .parser import parse_langgraph
from .server import attach as internal_attach

class Visualizer:
    @staticmethod
    def attach(app: Any, graph: Any, route: str = "/agentlens"):
        """
        Attaches the AgentLens visualizer to a FastAPI or Flask application.
        """
        return internal_attach(app, graph, route)

    @staticmethod
    def get_schema(graph: Any):
        """
        Returns the React Flow schema for the given graph.
        """
        return parse_langgraph(graph)

from dataclasses import dataclass
from typing import Dict, List
from agentlens import parse_langgraph

@dataclass
class MockNode:
    id: str

@dataclass
class MockEdge:
    source: str
    target: str
    label: str = None

class MockGraph:
    def __init__(self, nodes: Dict[str, dict], edges: List[MockEdge]):
        self.nodes = nodes
        self.edges = edges

def test_parser():
    # Create a mock graph structure similar to LangGraph's drawable graph
    nodes = {
        "__start__": {},
        "agent": {},
        "tool_call": {},
        "__end__": {}
    }
    edges = [
        MockEdge("__start__", "agent"),
        MockEdge("agent", "tool_call", "needs_tool"),
        MockEdge("agent", "__end__", "done"),
        MockEdge("tool_call", "agent")
    ]
    
    mock_graph = MockGraph(nodes, edges)
    
    # In real LangGraph, we'd call workflow.compile().get_graph()
    result = parse_langgraph(mock_graph)
    
    print("Nodes:")
    for n in result["nodes"]:
        print(f"  {n['id']} ({n['type']})")
    
    print("\nEdges:")
    for e in result["edges"]:
        print(f"  {e['source']} -> {e['target']} (label: {e.get('label')})")

if __name__ == "__main__":
    test_parser()

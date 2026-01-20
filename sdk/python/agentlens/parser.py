import json
from typing import Any, Dict, List, Optional

def parse_langgraph(graph: Any) -> Dict[str, Any]:
    """
    Parses a LangGraph (StateGraph) object and returns a React Flow compatible JSON.
    """
    # LangGraph objects typically have a get_graph() method which returns a drawable graph object.
    # We can extract nodes and edges from that.
    
    try:
        drawable_graph = graph.get_graph()
    except AttributeError:
        # If it's already the drawable graph
        drawable_graph = graph

    nodes = []
    edges = []

    # Map LangGraph nodes to React Flow nodes
    for node_id, node_data in drawable_graph.nodes.items():
        # node_id is the key, node_data contains metadata
        # React Flow expects: { id, data: { label }, position, type }
        
        node_type = "default"
        if node_id == "__start__":
            node_type = "input"
            label = "START"
        elif node_id == "__end__":
            node_type = "output"
            label = "END"
        else:
            label = node_id # Usually the function name or node label
            
        nodes.append({
            "id": node_id,
            "type": node_type,
            "data": {"label": label, "type": node_type},
            "position": {"x": 0, "y": 0} # Layout will be handled by frontend
        })

    # Map LangGraph edges to React Flow edges
    for edge in drawable_graph.edges:
        # edge usually has source, target, and sometimes a condition/label
        source = edge.source
        target = edge.target
        
        edge_id = f"e-{source}-{target}"
        edges.append({
            "id": edge_id,
            "source": source,
            "target": target,
            "label": getattr(edge, "label", None),
            "animated": True
        })

    return {
        "nodes": nodes,
        "edges": edges
    }

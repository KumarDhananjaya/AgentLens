import os
import sys
from typing import Annotated, TypedDict, List
from fastapi import FastAPI
import uvicorn

# Add the sdk path so we can import agentlens
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))

from agentlens import Visualizer
from langgraph.graph import StateGraph, START, END

# 1. Define the state
class AgentState(TypedDict):
    task: str
    plan: List[str]
    draft: str
    review_comments: str
    final_report: str
    iteration: int

# 2. Define nodes (Agents)

def planner_agent(state: AgentState):
    print("--- PLANNER AGENT ---")
    return {
        "plan": ["Research topic", "Write draft", "Review & Edit"],
        "iteration": state.get("iteration", 0) + 1
    }

def research_agent(state: AgentState):
    print("--- RESEARCH AGENT ---")
    return {"task": f"Researched facts for: {state['task']}"}

def writer_agent(state: AgentState):
    print("--- WRITER AGENT ---")
    return {"draft": f"This is a professional draft about {state['task']}."}

def reviewer_agent(state: AgentState):
    print("--- REVIEWER AGENT ---")
    # Simulate a review cycle
    if state["iteration"] < 2:
        return {"review_comments": "Needs more detail in section 2."}
    return {"final_report": f"FINALIZED: {state['draft']}"}

# 3. Define conditional logic
def should_continue(state: AgentState):
    if state.get("final_report"):
        return "end"
    return "revise"

# 4. Build the complex graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_agent)
workflow.add_node("researcher", research_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("reviewer", reviewer_agent)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "reviewer")

# Conditional routing from Reviewer
workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "revise": "planner",
        "end": END
    }
)

graph = workflow.compile()

# 5. Create FastAPI app
app = FastAPI(title="AgentLens Multi-Agent Demo")

Visualizer.attach(app, graph)

if __name__ == "__main__":
    print("Starting Multi-Agent Demo on http://localhost:8000")
    print("Visualizer: http://localhost:8000/agentlens/")
    uvicorn.run(app, host="0.0.0.0", port=8000)

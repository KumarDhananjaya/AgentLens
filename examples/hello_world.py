import os
import sys
from typing import Annotated, TypedDict
from fastapi import FastAPI
import uvicorn

# Add the sdk path so we can import agentlens
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))

from agentlens import Visualizer
from langgraph.graph import StateGraph, START, END

# 1. Define the state
class State(TypedDict):
    input: str
    count: int

# 2. Define nodes
def agent(state: State):
    print(f"Agent processing: {state['input']}")
    return {"count": state["count"] + 1}

def tool(state: State):
    print("Tool performing action...")
    return {"input": state["input"] + " (processed by tool)"}

# 3. Build the graph
workflow = StateGraph(State)

workflow.add_node("agent", agent)
workflow.add_node("tool", tool)

workflow.add_edge(START, "agent")
workflow.add_edge("agent", "tool")
workflow.add_edge("tool", END)

graph = workflow.compile()

# 4. Create FastAPI app and attach AgentLens
app = FastAPI(title="AgentLens Demo")

@app.get("/")
async def root():
    return {"message": "AgentLens is running at /agentlens"}

# This is the "One-Line" magic
Visualizer.attach(app, graph)

if __name__ == "__main__":
    print("Starting AgentLens Demo on http://localhost:8000")
    print("Visualizer available at http://localhost:8000/agentlens/")
    uvicorn.run(app, host="0.0.0.0", port=8000)

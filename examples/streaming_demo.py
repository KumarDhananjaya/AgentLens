import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from fastapi import FastAPI
import uvicorn
from agentlens import Visualizer, AgentLensCallbackHandler

# Define state
class State(TypedDict):
    input: str
    output: str

# Define nodes with some delay to visualize "active" state
async def node_a(state: State):
    print("Executing Node A...")
    await asyncio.sleep(2)
    return {"output": state["input"] + " -> A"}

async def node_b(state: State):
    print("Executing Node B...")
    await asyncio.sleep(2)
    return {"output": state["output"] + " -> B"}

# Build graph
builder = StateGraph(State)
builder.add_node("Node A", node_a)
builder.add_node("Node B", node_b)
builder.add_edge(START, "Node A")
builder.add_edge("Node A", "Node B")
builder.add_edge("Node B", END)

graph = builder.compile()

# Setup App
app = FastAPI()
Visualizer.attach(app, graph)

# Simulate execution trigger
@app.get("/trigger")
async def trigger_graph():
    # Run in background to not block response
    asyncio.create_task(run_graph())
    return {"status": "Graph started"}

async def run_graph():
    print("Starting graph execution...")
    inputs = {"input": "Start"}
    handler = AgentLensCallbackHandler()
    
    # Invoke the graph with the callback handler
    # Note: For async graphs, use ainvoke
    await graph.ainvoke(inputs, config={"callbacks": [handler]})
    print("Graph execution finished.")

if __name__ == "__main__":
    print("Starting AgentLens Streaming Demo...")
    print("1. Open http://localhost:8000/agentlens/ in your browser.")
    print("2. Call http://localhost:8000/trigger (or use curl) to see the visualization update.")
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

app = FastAPI(title="LangGraph Human-in-the-Loop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. State Definition
class State(BaseModel):
    message: str = ""

# 2. Nodes
def generate_message(state: State):
    return {"message": "Hello, Unviverse!"}  # Typo for testing

def finalize(state: State):
    return {"message": state.message}  # Post-approval step

# 3. Build and Compile Graph with a subsequent node so state.next isn't empty
workflow = StateGraph(State)
workflow.add_node("generate_message", generate_message)
workflow.add_node("finalize", finalize)

workflow.add_edge(START, "generate_message")
workflow.add_edge("generate_message", "finalize")
workflow.add_edge("finalize", END)

memory = MemorySaver()
# Pause after generate_message. Because 'finalize' is next, state.next will be non-empty!
graph = workflow.compile(checkpointer=memory, interrupt_after=["generate_message"])

class FeedbackRequest(BaseModel):
    thread_id: str
    message: str

@app.post("/run-agent")
def run_agent(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    
    for event in graph.stream({"message": ""}, config):
        pass
        
    state = graph.get_state(config)
    
    # Now state.next will contain 'finalize', so this evaluates correctly!
    if state.next:
        return {
            "status": "waiting_for_approval",
            "current_message": state.values.get("message"),
            "thread_id": thread_id
        }
    return {"status": "completed", "result": state.values}

@app.post("/resume-agent")
def resume_agent(data: FeedbackRequest):
    config = {"configurable": {"thread_id": data.thread_id}}
    
    # Update state with human feedback
    graph.update_state(config, {"message": data.message})
    
    # Resume graph execution to the final node
    results = []
    for event in graph.stream(None, config):
        results.append(event)
        
    return {"status": "resumed_and_completed", "events": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
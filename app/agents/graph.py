from .nodes import classifier, extractor, validator
from .state import GraphState
from langgraph.graph import StateGraph, END

def should_continue(state: GraphState):
    tasks = state.get("extraction_tasks", [])
    current_idx = state.get("schema_index", 0)

    if current_idx < len(tasks):
        return "extract"
    
    return "validate"

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("classify", classifier.run)
    workflow.add_node("extract", extractor.run)
    workflow.add_node("validate", validator.run)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")

    workflow.add_conditional_edges(
        "extract",
        should_continue,
        {
            "extract": "extract",
            "validate": "validate"
        }
    )

    workflow.add_edge("validate", END)

    return workflow.compile()

app = create_workflow()
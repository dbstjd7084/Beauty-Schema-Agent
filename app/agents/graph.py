from .nodes import classifier, extractor, validator
from .state import GraphState
from langgraph.graph import StateGraph, END

def should_continue(state: GraphState):
    if state["schema_index"] < len(state["selected_schemas"]):
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
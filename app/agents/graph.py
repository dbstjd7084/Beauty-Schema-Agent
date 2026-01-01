from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import classifier, extractor, validator

def create_workflow():
    workflow = StateGraph(GraphState)

    # 1. 노드 등록
    workflow.add_node("classify", classifier.run)
    workflow.add_node("extract", extractor.run)
    workflow.add_node("validate", validator.run)

    # 2. 연결 (Edges)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "validate")

    workflow.add_edge("validate", END)

    return workflow.compile()

app = create_workflow()
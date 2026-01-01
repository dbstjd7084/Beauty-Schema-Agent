from ..state import GraphState

def run(state: GraphState):
    print("---분류 단계---")
    return {"selected_schemas": ["Product", "Review"], "retry_count": 0}
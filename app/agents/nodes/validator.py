from ..state import GraphState

def run(state: GraphState):
    print("--- 검증 단계 ---")
    extracted_data = state.get("extracted_data")
    errors = []

    # 1. 추출된 데이터 자체가 없는 경우
    if not extracted_data:
        return {"errors": ["데이터 추출에 실패했습니다."]}

    # 2. Schema에 정의한 필수 필드(name) 검증
    # 현재 ProductSchema에는 name만 필수이므로 name만 체크합니다.
    if not extracted_data.get("name"):
        errors.append("상품명(name) 정보가 누락되었습니다.")

    # (참고) 나중에 price를 추가하신다면 그때 아래 주석을 해제하세요.
    # if not extracted_data.get("price"):
    #     errors.append("가격 정보가 누락되었습니다.")

    return {"errors": errors}
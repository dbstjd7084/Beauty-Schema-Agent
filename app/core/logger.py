import logging
import json
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

crawler_logger = logging.getLogger("Crawler")
extractor_logger = logging.getLogger("Extractor")

class ExecutionLogger:
    """FastAPI 응답에 포함할 세션별 로그 수집기"""
    def __init__(self):
        self.logs = []

    def add(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.logs.append(formatted_msg)
        
        if level == "ERROR":
            crawler_logger.error(message)
        else:
            crawler_logger.info(message)

    def get_logs(self):
        return self.logs
    
def log_extraction_result(schema_name: str, data: dict, ex_log: ExecutionLogger = None):
    extractor_logger.info(f"[Extractor] [{schema_name}] 추출 성공")

    if ex_log:
        ex_log.add(f"Extractor: [{schema_name}] 정보 추출 및 미디어 매핑 완료")
    
    try:
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        print(f"\n{'='*20} {schema_name} RESULT {'='*20}")
        print(formatted_json)
        print(f"{'='*50}\n")
    except Exception as e:
        extractor_logger.error(f"JSON 출력 에러: {e}")

def log_classification_result(schemas: list, reason: str, ex_log: ExecutionLogger = None):
    crawler_logger.info("[Classifier] 스키마 분류 완료")

    if ex_log:
        # 프런트엔드 로그용 요약 정보 추가
        schema_types = [s.schema_type if hasattr(s, 'schema_type') else str(s) for s in schemas]
        ex_log.add(f"Classifier: 분석 대상 식별 완료 -> {', '.join(schema_types)}")
    
    print(f"\n{'='*20} Classification RESULT {'='*20}")
    print(f"Selected : {schemas}")
    print(f"Reason   : {reason}")
    print(f"{'='*54}\n")

def log_validation_result(is_valid: bool, reason: str, missing_fields: list, ex_log: ExecutionLogger = None):
    """LLM의 데이터 검증 결과를 터미널에 깔끔하게 출력"""
    status_icon = "✅ PASSED" if is_valid else "❌ FAILED"
    crawler_logger.info("[Validator] 데이터 품질 검증 완료")

    if ex_log:
        msg = f"Validator: 검증 {'성공' if is_valid else '실패'} ({reason})"
        ex_log.add(msg, level="INFO" if is_valid else "ERROR")
    
    print(f"\n{'='*20} Validation RESULT {'='*20}")
    print(f"Status  : {status_icon}")
    print(f"Reason  : {reason}")
    if missing_fields:
        print(f"Missing : {', '.join(missing_fields)}")
    print(f"{'='*53}\n")


def log_final_output(final_data: dict, ex_log: ExecutionLogger = None):
    """모든 태스크가 완료된 후 최종적으로 추출된 전체 JSON-LD 데이터를 출력"""
    crawler_logger.info("[System] 최종 결과물(Final JSON-LD) 생성 완료")
    
    if ex_log:
        ex_log.add("System: 모든 스키마 데이터 통합 및 검증 완료")

    print(f"\n{'#'*25} FINAL OUTPUT {'#'*25}")
    try:
        formatted_json = json.dumps(final_data, indent=2, ensure_ascii=False)
        print(formatted_json)
    except Exception as e:
        print(f"출력 중 오류 발생: {e}")
    print(f"{'#'*64}\n")
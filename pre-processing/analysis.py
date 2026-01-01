import pandas as pd
import re
import json

# 1. 파일 불러오기 (CSV 대신 JSON 로드)
# 파일 경로는 실제 환경에 맞춰 .json으로 변경해주세요.
file_path = 'pre-processing/amore_url_groups_summary_final.json' 

try:
    # 일반적인 JSON 배열 형태([...])일 경우
    df = pd.read_json(file_path, encoding='utf-8')
except ValueError:
    # 만약 각 행이 개별 JSON 객체인 형태(JSON Lines)일 경우
    df = pd.read_json(file_path, lines=True, encoding='utf-8')

# --- [전처리 함수 정의] ---
def clean_info_text(text):
    if pd.isna(text) or text == "":
        return ""
    text = str(text)
    
    # 1. 미디어 태그 기본 정리 (이모티콘 및 '발견' 제거)
    text = re.sub(r'🖼️\s*이미지\s*발견', '이미지', text)
    text = re.sub(r'🎥\s*동영상\s*발견', '동영상', text)
    text = re.sub(r'📺\s*외부\s*동영상', '외부 동영상', text)

    # 2. #으로 시작하고 :로 끝나는 식별자 제거
    text = re.sub(r'#[^:]*:\s*', '', text)

    # 3. 특정 패턴 및 중복 문자 제거 (2개 이상 연속 시 삭제)
    text = re.sub(r',{2,}', '', text)
    text = re.sub(r'\.{2,}', '', text)
    text = re.sub(r'\*{2,}', '', text)

    # 4. 경로 정보 삭제 (| 로 시작해서 ] 로 끝나면 ]만 남김)
    text = re.sub(r'\|[^\]]*]', ']', text)

    # 5. 공백 및 줄바꿈 정리
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # 대괄호/중괄호 내부 불필요한 공백 정리
    text = re.sub(r'\s+\]', ']', text)
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\{\s+', '{', text)

    return text.strip()

# 2. 전처리 수행 및 길이 계산
# JSON 로드 시 info 컬럼이 비어있을 수 있으므로 처리
df['info_len_before'] = df['info'].fillna('').astype(str).apply(len)
df['info_cleaned'] = df['info'].apply(clean_info_text)
df['info_len_after'] = df['info_cleaned'].apply(len)

# 3. 통계 비교 함수
def get_detailed_stats(df, col_len, col_text):
    return {
        "총 데이터 개수": len(df),
        "유니크 텍스트 수": df[col_text].nunique(),
        "평균 글자수": df[col_len].mean(),
        "중간값": df[col_len].median(),
        "최소값": df[col_len].min(),
        "최대값": df[col_len].max()
    }

stats_before = get_detailed_stats(df, 'info_len_before', 'info')
stats_after = get_detailed_stats(df, 'info_len_after', 'info_cleaned')

# 4. 결과 출력
print("### 🔍 전처리 전/후 데이터 통계 비교 (JSON 로드) ###")
comparison_df = pd.DataFrame([stats_before, stats_after], index=['전처리 전', '전처리 후']).T
print(comparison_df.to_string())

print("\n" + "="*60)

# 5. 전처리 효과 요약
diff_avg = stats_before['평균 글자수'] - stats_after['평균 글자수']
unique_reduction = stats_before['유니크 텍스트 수'] - stats_after['유니크 텍스트 수']

print(f"### 💡 전처리 요약 분석 ###")
print(f"* 평균 글자 수 약 {diff_avg:.2f}자 감소")
print(f"* 유니크 데이터 {unique_reduction}개 감소 (노이즈 제거 완료)")

print("\n" + "-"*60)

# 6. 최소값 데이터 다시 추출 및 저장
min_len_after = df['info_len_after'].min()
min_df_after = df[df['info_len_after'] == min_len_after]

print(f"### 📂 전처리 후 최소값 데이터 (길이: {min_len_after}자) ###")
print(f"해당 행 개수: {len(min_df_after)}개")

if not min_df_after.empty:
    # 저장 시에도 필요에 따라 JSON으로 저장할 수 있습니다.
    output_path = 'pre-processing/min_info_after_cleaning.json'
    min_df_after.to_json(output_path, orient='records', force_ascii=False, indent=4)
    print(f"최소값 리스트 JSON 저장됨: {output_path}")

# 7. 실제 텍스트 변화 샘플 (최대 길이 행 기준)
if not df.empty and stats_before['최대값'] > 0:
    max_idx = df['info_len_before'].idxmax()
    print("\n" + "-"*60)
    print("### 📝 전처리 실제 예시 ###")
    print(f"[Before]: {df.loc[max_idx, 'info'][:100]}...")
    print(f"[After]:  {df.loc[max_idx, 'info_cleaned'][:100]}...")

# 7. 가장 글자 수가 많았던 행의 상세 시각화 비교
if not df.empty and stats_before['최대값'] > 0:
    max_idx = df['info_len_before'].idxmax()
    
    # 데이터 추출
    before_text = df.loc[max_idx, 'info']
    after_text = df.loc[max_idx, 'info_cleaned']
    len_before = df.loc[max_idx, 'info_len_before']
    len_after = df.loc[max_idx, 'info_len_after']
    reduction_rate = ((len_before - len_after) / len_before) * 100

    print("\n" + "★" * 30)
    print(" [상세 분석] 가장 긴 데이터의 전처리 결과 ")
    print("★" * 30)
    
    # 기본 정보 출력
    if 'final_target_url' in df.columns:
        print(f"■ 대상 URL: {df.loc[max_idx, 'final_target_url']}")
    elif 'target_url' in df.columns:
        print(f"■ 대상 URL: {df.loc[max_idx, 'target_url']}")
        
    print(f"■ 글자 수 변화: {len_before:,}자 -> {len_after:,}자")
    print(f"■ 토큰 최적화율: {reduction_rate:.1f}% 감소")
    
    print("\n" + "=" * 60)
    print(" [1] 원본 데이터 (Before) ")
    print("-" * 60)
    # 텍스트가 너무 길 경우를 대비해 필요시 슬라이싱 하거나 전문 출력
    print(before_text) 
    
    print("\n" + "=" * 60)
    print(" [2] 정제된 데이터 (After) ")
    print("-" * 60)
    print(after_text)
    
    print("\n" + "=" * 60)
    print(" [3] 주요 제거 항목 확인 ")
    print("-" * 60)
    # 어떤 부분들이 주로 제거되었는지 요약
    print(f"- 중복 특수문자(.,*) 및 미디어 이모티콘 제거 완료")
    print(f"- 이미지/영상 경로 정보 (| 경로: ...]) 삭제 완료")
    print(f"- 메타데이터 태그 식별자 (#area:, #name:) 삭제 완료")
    print("-" * 60)
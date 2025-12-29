document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('runBtn');
    const urlInput = document.getElementById('urlInput');
    const logWindow = document.getElementById('logWindow');
    const jsonOutput = document.getElementById('jsonOutput');
    const validationArea = document.getElementById('validationArea');

    runBtn.addEventListener('click', async () => {
        const url = urlInput.value;
        if (!url) return alert("URL을 입력해주세요.");

        // 초기화
        logWindow.innerHTML = '';
        jsonOutput.innerHTML = '<span class="text-muted">// Analyzing...</span>';
        validationArea.style.display = 'none';
        runBtn.disabled = true;

        // 에이전트 로그 시뮬레이션
        await addLog("Crawler Agent: 페이지 접속 및 HTML 파싱 중...", 800);
        await addLog("Crawler Agent: 상품명, 가격, 리뷰 수 데이터 추출 성공.", 1000);
        await addLog("Context Agent: 뷰티 카테고리 특성 데이터 분류 중 (성분, 용량)...", 1200);
        await addLog("Linker Agent: Schema.org v24.0 가이드라인에 맞춰 구조화 중...", 1000);
        await addLog("System: 모든 프로세스 완료. JSON-LD를 생성합니다.", 500);

        // 결과 표시 (샘플 데이터 사용)
        displayResults();
        runBtn.disabled = false;
    });

    async function addLog(msg, delay) {
        return new Promise(resolve => {
            setTimeout(() => {
                const div = document.createElement('div');
                div.className = 'log-line';
                div.innerHTML = `<span style="color: #58a6ff;">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
                logWindow.appendChild(div);
                logWindow.scrollTop = logWindow.scrollHeight;
                resolve();
            }, delay);
        });
    }

    function displayResults() {
        // fetch('sample_response.json') 등으로 가져올 데이터
        const mockData = {
            "productName": "A사 수분 가득 히알루론산 크림 50ml",
            "price": "28,000",
            "rating": "4.8",
            "reviewCount": "1,540",
            "description": "피부 깊숙이 수분을 전달하는 고농축 히알루론산 크림입니다. 모든 피부 타입에 적합하며 24시간 보습이 지속됩니다."
        };

        // JSON-LD 텍스트 생성
        const jsonCode = `{
  <span class="json-key">"@context"</span>: <span class="json-value">"https://schema.org/"</span>,
  <span class="json-key">"@type"</span>: <span class="json-value">"Product"</span>,
  <span class="json-key">"name"</span>: <span class="json-value">"${mockData.productName}"</span>,
  <span class="json-key">"description"</span>: <span class="json-value">"${mockData.description}"</span>,
  <span class="json-key">"aggregateRating"</span>: {
    <span class="json-key">"@type"</span>: <span class="json-value">"AggregateRating"</span>,
    <span class="json-key">"ratingValue"</span>: <span class="json-value">"${mockData.rating}"</span>,
    <span class="json-key">"reviewCount"</span>: <span class="json-value">"${mockData.reviewCount}"</span>
  }
}`;
        jsonOutput.innerHTML = jsonCode;
        validationArea.style.display = 'block';

        // 구글 프리뷰 업데이트
        document.getElementById('prevTitle').innerText = mockData.productName;
        document.getElementById('prevDesc').innerText = mockData.description;
        document.getElementById('prevRating').innerText = `${mockData.rating} (${mockData.reviewCount} reviews)`;
        document.getElementById('prevPrice').innerText = `₩${mockData.price}`;
    }

    // 복사 기능
    document.getElementById('copyBtn').addEventListener('click', () => {
        const text = jsonOutput.innerText;
        navigator.clipboard.writeText(text).then(() => alert("복사되었습니다!"));
    });
});
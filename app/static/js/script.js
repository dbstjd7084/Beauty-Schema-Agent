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

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // 로그를 순차적으로 표시
                for (const log of data.result.logs) {
                    await addLog(log, 500);
                }

                // 결과 표시
                displayResults(data.result.json_ld);
            } else {
                alert('Error: ' + (data.message || '알 수 없는 오류'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('요청 중 오류가 발생했습니다.');
        }

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

    function displayResults(jsonLd) {
        // JSON-LD를 스타일링된 텍스트로 변환
        const jsonCode = JSON.stringify(jsonLd, null, 2)
            .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
            .replace(/: "([^"]+)"/g, ': <span class="json-value">"$1"</span>')
            .replace(/: ([^,\n}]+)/g, ': <span class="json-value">$1</span>');

        jsonOutput.innerHTML = jsonCode;
        validationArea.style.display = 'block';

        // 구글 프리뷰 업데이트 (jsonLd에서 데이터 추출)
        document.getElementById('prevTitle').innerText = jsonLd.name || 'Product Name';
        document.getElementById('prevDesc').innerText = jsonLd.description || 'Description';
        document.getElementById('prevRating').innerText = `${jsonLd.aggregateRating?.ratingValue || '0'} (${jsonLd.aggregateRating?.reviewCount || '0'} reviews)`;
        document.getElementById('prevPrice').innerText = `₩${jsonLd.offers?.price || '0'}`;
    }

    // 복사 기능
    document.getElementById('copyBtn').addEventListener('click', () => {
        const text = jsonOutput.innerText;
        navigator.clipboard.writeText(text).then(() => alert("복사되었습니다!"));
    });
});
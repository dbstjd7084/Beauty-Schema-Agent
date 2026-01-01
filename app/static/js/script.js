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
        const jsonCode = JSON.stringify(jsonLd, null, 2)
            .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
            .replace(/: "([^"]+)"/g, ': <span class="json-value">"$1"</span>')
            .replace(/: ([^,\n}]+)/g, ': <span class="json-value">$1</span>');

        document.getElementById('jsonOutput').innerHTML = jsonCode;
        document.getElementById('validationArea').style.display = 'block';

        updateGooglePreview(jsonLd); 
    }

    function updateGooglePreview(jsonLd) {
        const type = jsonLd['@type'];
        
        const sections = ['prevRatingArea', 'prevVideoArea', 'shoppingInfo', 'localInfo'];
        sections.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

        document.getElementById('prevTitle').innerText = jsonLd.name || jsonLd.headline || 'Product Name';
        document.getElementById('prevDesc').innerText = jsonLd.description || 'Description...';

        if (jsonLd.breadcrumb) {
            document.getElementById('prevBreadcrumb').innerText = "yoursite.com › products";
        }

        switch(type) {
            case 'Product':
                document.getElementById('shoppingInfo').style.display = 'flex';
                document.getElementById('prevPrice').innerText = `₩${jsonLd.offers?.price || '0'}`;
                renderReview(jsonLd.aggregateRating);
                break;

            case 'VideoObject':
                document.getElementById('prevVideoArea').style.display = 'block';
                break;

            case 'LocalBusiness':
                document.getElementById('localInfo').style.display = 'block';
                const address = jsonLd.address?.streetAddress || '서울시 강남구...';
                document.getElementById('localInfo').innerHTML = `<i class="bi bi-geo-alt"></i> ${address} · 영업중`;
                break;

            case 'Review': 
                renderReview(jsonLd);
                break;

            case 'Article':
                break;
        }
    }

    function renderReview(ratingData) {
        if (ratingData) {
            document.getElementById('prevRatingArea').style.display = 'block';
            const val = ratingData.ratingValue || '0';
            const count = ratingData.reviewCount || ratingData.ratingCount || '0';
            document.getElementById('prevRatingText').innerText = `${val} (${count} reviews)`;
        }
    }
});
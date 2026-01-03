document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('runBtn');
    const urlInput = document.getElementById('urlInput');
    const logWindow = document.getElementById('logWindow');
    const jsonOutput = document.getElementById('jsonOutput');
    const validationArea = document.getElementById('validationArea');

    runBtn.addEventListener('click', async () => {
        const url = urlInput.value;
        if (!url) return alert("URL을 입력해주세요.");

        document.getElementById('notifUrl').innerText = url;

        // 초기화
        logWindow.innerHTML = '';
        jsonOutput.innerHTML = '<span class="text-muted">// Analyzing...</span>';
        validationArea.style.display = 'none';
        
        const monitorCard = document.querySelector('.custom-card .bi-broadcast').closest('.custom-card');
        monitorCard.style.display = 'none'; 

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

                if (data.result.is_live) {
                    await addLog("실시간 라이브 스트리밍이 감지되었습니다.", 300);
                    monitorCard.style.display = 'block'; // 감지되었을 때만 표시
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
        let primaryData = jsonLd;
        if (!jsonLd['@type']) {
            const firstKey = Object.keys(jsonLd)[0];
            primaryData = jsonLd[firstKey];
        }

        if (!primaryData) return;

        const type = primaryData['@type'];
        
        const sections = ['prevRatingArea', 'prevVideoArea', 'ProductInfo', 'localInfo'];
        sections.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

        document.getElementById('prevTitle').innerText = primaryData.name || primaryData.headline || primaryData.title || '분석된 결과 없음';
        document.getElementById('prevDesc').innerText = primaryData.description || primaryData.articleBody?.substring(0, 150) || '설명이 없습니다.';
        
        // URL/브레드크럼 표시 업데이트
        const urlEl = document.getElementById('prevUrl');
        if (primaryData.url) {
            urlEl.innerText = primaryData.url.replace(/^https?:\/\//, '');
        }

        switch(type) {
            case 'Product':
                document.getElementById('ProductInfo').style.display = 'flex';
                
                const price = primaryData.offers?.price || primaryData.offers?.[0]?.price || '0';
                document.getElementById('prevPrice').innerText = `₩${price}`;
                renderReview(primaryData.aggregateRating);
                break;

            case 'Review': 
                renderReview(primaryData);
                break;

            case 'LocalBusiness':
            case 'Organization':
                document.getElementById('localInfo').style.display = 'block';
                const location = primaryData.address?.streetAddress || primaryData.address || primaryData.location || '정보 없음';
                document.getElementById('localInfo').innerHTML = `<i class="bi bi-geo-alt"></i> ${location}`;
                break;

            case 'VideoObject':
            case 'Video':
                document.getElementById('prevVideoArea').style.display = 'block';
                break;

            case 'Article':
                if (primaryData.author) {
                    urlEl.innerText += ` · ${primaryData.author.name || primaryData.author}`;
                }
                break;

            case 'BreadcrumbList':
            case 'Breadcrumb':
                if (primaryData.itemListElement) {
                    const path = primaryData.itemListElement.map(item => item.name).join(' › ');
                    urlEl.innerText = path;
                }
                break;

            case 'ImageObject':
            case 'ImageMeta':
                document.getElementById('prevTitle').innerHTML = `<i class="bi bi-image me-1"></i> ` + document.getElementById('prevTitle').innerText;
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
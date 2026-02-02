import os, requests, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Imperial Core Config ---
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>Strategic AI Core - segmented Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #0f0f0f; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; direction: rtl; }
        .sidebar { width: 280px; background: var(--panel); border-left: 1px solid var(--gold); padding: 20px; overflow-y: auto; }
        .main { flex: 1; padding: 30px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .input-box { width: 100%; max-width: 600px; background: #111; border: 1px solid var(--gold); color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px; text-align: right; }
        
        /* تصميم النوافذ المستقلة لكل نقطة */
        .output-segment { width: 100%; max-width: 700px; background: var(--panel); border-right: 4px solid var(--gold); padding: 20px; border-radius: 10px; margin-top: 15px; animation: fadeIn 0.5s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .segment-title { color: var(--gold); font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        button { background: var(--gold); color: black; border: none; padding: 12px 35px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .pdf-btn { background: #333; color: var(--gold); font-size: 0.75rem; margin-top: 10px; border: 1px solid var(--gold); cursor: pointer; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3 style="color:var(--gold)">الذاكرة السحابية</h3>
        <div id="historyList"></div>
    </div>
    <div class="main">
        <h1 style="color:var(--gold); letter-spacing:4px;">STRATEGIC-AI-CORE</h1>
        <textarea id="userInput" class="input-box" rows="3" placeholder="أدخل الرابط أو المطلب الاستراتيجي..."></textarea><br>
        <button onclick="executeSegmented()">تنفيذ الاستخراج المجزأ</button>
        <div id="resultsContainer" style="width:100%; display:flex; flex-direction:column; align-items:center; margin-top:20px;"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;

        async function executeSegmented() {
            const val = document.getElementById('userInput').value;
            if(!val) return;
            
            const container = document.getElementById('resultsContainer');
            container.innerHTML = `<p style="color:var(--gold)">جاري تحليل البيانات وتجزئة النوافذ السيادية...</p>`;

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val })
                });
                const d = await r.json();
                const rawResult = d.res || d.err;
                
                // تفكيك النص بناءً على النقاط (1, 2, 3...)
                const segments = rawResult.split(/(?=\\d\\.)/); 
                container.innerHTML = ""; // مسح رسالة التحميل

                segments.forEach((seg, index) => {
                    if(seg.trim().length < 5) return;
                    const card = document.createElement('div');
                    card.className = 'output-segment';
                    card.id = 'seg-' + index;
                    card.innerHTML = `
                        <div class="segment-title">المكون الاستراتيجي #${index + 1}</div>
                        <div style="line-height:1.6; color:#eee;">${seg.trim()}</div>
                        <button class="pdf-btn" onclick="exportSegmentPDF('seg-${index}')">حفظ هذه النافذة PDF</button>
                    `;
                    container.appendChild(card);
                });

            } catch { container.innerHTML = "فشل في مزامنة النواة."; }
        }

        function exportSegmentPDF(id) {
            const doc = new jsPDF();
            doc.text(document.getElementById(id).innerText, 10, 10, { maxWidth: 180, align: 'right' });
            doc.save('Strategic_Segment.pdf');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('prompt', '')
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Analyze the link. Format your output clearly as numbered points (1. Title... 2. Title...). Use professional M&A language."},
            {"role": "user", "content": user_input}
        ]
    }
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=30)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"err": "نظام الحماية: المحرك مشغول، حاول مجدداً."})

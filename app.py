import os, requests, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Imperial Core Config ---
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Strategic AI Core - Enterprise Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #0f0f0f; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: var(--panel); border-left: 1px solid var(--gold); padding: 20px; overflow-y: auto; }
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .input-box { width: 100%; max-width: 650px; background: #111; border: 1px solid var(--gold); color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
        .nav-controls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
        select, button { background: var(--gold); color: black; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .output-card { width: 100%; max-width: 750px; background: var(--panel); border-right: 5px solid var(--gold); padding: 20px; border-radius: 10px; margin-top: 15px; position: relative; }
        .copy-btn { position: absolute; left: 10px; top: 10px; font-size: 0.7rem; background: #333; color: var(--gold); }
        .history-item { background: #1a1a1a; padding: 10px; margin-bottom: 8px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; border: 1px solid #333; }
        .history-item:hover { border-color: var(--gold); }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3 style="color:var(--gold)">الذاكرة السحابية (التخزين الدائم)</h3>
        <div id="historyList"></div>
        <button onclick="clearHistory()" style="width:100%; margin-top:20px; background:#444; color:white;">تصفير الذاكرة</button>
    </div>

    <div class="main">
        <h1 style="color:var(--gold); letter-spacing:3px;">STRATEGIC-AI-CORE</h1>
        
        <div class="nav-controls">
            <select id="langSelect">
                <option value="Arabic">العربية</option>
                <option value="English">English</option>
                <option value="French">Français</option>
                <option value="German">Deutsch</option>
                <option value="Chinese">中文</option>
            </select>
            <button onclick="execute()">تنفيذ التحليل</button>
            <button onclick="exportFullPDF()" style="background:#d4d4d4;">تصدير PDF الشامل</button>
        </div>

        <textarea id="userInput" class="input-box" rows="3" placeholder="أدخل الرابط الاستراتيجي هنا..."></textarea>
        
        <div id="resultsContainer" style="width:100%;"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let memory = JSON.parse(localStorage.getItem('imp_memory') || '[]');

        function saveMemory(title, content) {
            memory.unshift({ title, content, id: Date.now() });
            localStorage.setItem('imp_memory', JSON.stringify(memory));
            renderHistory();
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = memory.map(m => `
                <div class="history-item" onclick="loadFromMem('${m.id}')">
                    ${m.title}<br><small style="color:#666">${new Date(m.id).toLocaleTimeString()}</small>
                </div>
            `).join('');
        }

        async function execute() {
            const val = document.getElementById('userInput').value;
            const lang = document.getElementById('langSelect').value;
            if(!val) return;

            const container = document.getElementById('resultsContainer');
            container.innerHTML = `<p style="color:var(--gold); text-align:center;">جاري المعالجة بلغة ${lang}...</p>`;

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: lang })
                });
                const d = await r.json();
                const segments = (d.res || d.err).split(/(?=\\d\\.)/);
                
                container.innerHTML = "";
                segments.forEach((seg, i) => {
                    const card = document.createElement('div');
                    card.className = 'output-card';
                    card.innerHTML = `
                        <button class="copy-btn" onclick="copyText(this)">نسخ النص</button>
                        <div class="content">${seg.trim()}</div>
                    `;
                    container.appendChild(card);
                });
                saveMemory(val.substring(0,30), d.res);
            } catch { container.innerHTML = "خطأ في الاتصال بالنواة."; }
        }

        function copyText(btn) {
            const txt = btn.nextElementSibling.innerText;
            navigator.clipboard.writeText(txt);
            btn.innerText = "تم النسخ!";
            setTimeout(() => btn.innerText = "نسخ النص", 2000);
        }

        function exportFullPDF() {
            const doc = new jsPDF();
            let y = 10;
            document.querySelectorAll('.content').forEach((el, i) => {
                const text = doc.splitTextToSize(el.innerText, 180);
                doc.text(text, 10, y);
                y += (text.length * 7) + 10;
                if(y > 270) { doc.addPage(); y = 10; }
            });
            doc.save('Strategic_Full_Report.pdf');
        }

        function clearHistory() { localStorage.removeItem('imp_memory'); memory = []; renderHistory(); }
        renderHistory();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"You are a global M&A analyst. Provide analysis in {data.get('lang')}. Format as numbered points."},
            {"role": "user", "content": data.get('prompt')}
        ]
    }
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=40)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"err": "نظام الحماية: المحرك مشغول."})

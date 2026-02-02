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
    <title>Strategic AI Core - Universal Access</title>
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
    </style>
</head>
<body>
    <div class="sidebar">
        <h3 style="color:var(--gold)">الذاكرة السحابية الدائمة</h3>
        <div id="historyList"></div>
    </div>

    <div class="main">
        <h1 style="color:var(--gold); letter-spacing:3px;">STRATEGIC-AI-CORE</h1>
        <div class="nav-controls">
            <select id="langSelect"><option value="Arabic">العربية</option><option value="English">English</option></select>
            <button onclick="execute()">تحليل الرابط السيادي</button>
            <button onclick="exportFullPDF()" style="background:#d4d4d4;">تصدير التقرير الشامل</button>
        </div>
        <textarea id="userInput" class="input-box" rows="3" placeholder="انسخ أي رابط (يوتيوب، مقال، تقرير سيبراني)..."></textarea>
        <div id="resultsContainer" style="width:100%;"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let memory = JSON.parse(localStorage.getItem('imp_memory') || '[]');

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = memory.map(m => `<div class="history-item">${m.title}</div>`).join('');
        }

        async function execute() {
            const val = document.getElementById('userInput').value;
            const lang = document.getElementById('langSelect').value;
            if(!val) return;

            const container = document.getElementById('resultsContainer');
            container.innerHTML = `<p style="color:var(--gold); text-align:center;">جاري اختراق الرابط واستخراج البيانات الاستراتيجية...</p>`;

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: lang, is_url: true })
                });
                const d = await r.json();
                const segments = (d.res).split(/(?=\\d\\.)/);
                
                container.innerHTML = "";
                segments.forEach((seg, i) => {
                    const card = document.createElement('div');
                    card.className = 'output-card';
                    card.innerHTML = `<button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)">نسخ</button><div class="content">${seg.trim()}</div>`;
                    container.appendChild(card);
                });
                
                memory.unshift({ title: val.substring(0,30), content: d.res });
                localStorage.setItem('imp_memory', JSON.stringify(memory));
                renderHistory();
            } catch { container.innerHTML = "النظام مشغول بمعالجة بيانات ضخمة، أعد المحاولة."; }
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
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    
    # تحسين البرومبت لإجبار الموديل على استخدام أدوات البحث الداخلية (Search Tools)
    system_instruction = f"""
    You are an advanced Strategic AI with direct web-access capabilities. 
    Analyze the provided URL: {data.get('prompt')}.
    1. If it is a YouTube link, extract the transcript and summarize key M&A insights.
    2. If it is a website, scrape the technical data.
    3. Output in {data.get('lang')} using numbered points and professional 'Whale' language.
    4. Provide specific financial or technical metrics found in the link.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_instruction}],
        "temperature": 0.2 # لضمان الدقة في نقل الأرقام
    }
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=50)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"res": "خطأ في الاتصال بالنواة."})

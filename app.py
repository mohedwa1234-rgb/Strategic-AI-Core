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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic AI Core - Imperial v8</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; --text: #eee; }
        body { background: var(--bg); color: var(--text); font-family: 'Tajawal', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: #0a0a0a; border-left: 2px solid var(--gold); display: flex; flex-direction: column; transition: all 0.3s ease; position: relative; z-index: 1000; }
        .sidebar.collapsed { margin-right: -300px; opacity: 0; }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #333; text-align: center; color: var(--gold); font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        .memory-list { flex: 1; overflow-y: auto; padding: 10px; }
        .mem-item { background: #1a1a1a; padding: 10px; margin-bottom: 8px; border-radius: 6px; border: 1px solid #333; cursor: pointer; position: relative; transition: 0.2s; }
        .mem-item:hover { border-color: var(--gold); background: #222; }
        .mem-title { font-size: 0.85rem; font-weight: bold; margin-bottom: 5px; padding-left: 25px; }
        .mem-date { font-size: 0.7rem; color: #888; }
        .del-btn { position: absolute; left: 5px; top: 5px; background: #500; color: white; border: none; width: 20px; height: 20px; border-radius: 50%; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; }
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); color: black; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; z-index: 2000; display: flex; align-items: center; gap: 5px; }
        .control-panel { width: 100%; max-width: 800px; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; margin-top: 40px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 10px; }
        input[type="text"] { flex: 1; background: #000; border: 1px solid var(--gold); color: white; padding: 10px; border-radius: 6px; }
        select { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 15px; border-radius: 6px; }
        .actions { display: flex; gap: 10px; }
        button.action-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-run { background: var(--gold); color: black; }
        .btn-pdf { background: #fff; color: black; }
        .btn-clear { background: #333; color: white; }
        .report-container { width: 100%; max-width: 850px; }
        .output-card { background: var(--panel); border-right: 5px solid var(--gold); padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); position: relative; }
        .card-tools { display: flex; justify-content: flex-end; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .copy-btn { background: #222; color: var(--gold); border: 1px solid #444; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
        .report-text { line-height: 1.8; font-size: 1rem; white-space: pre-wrap; }
        @media print { .sidebar, .control-panel, .card-tools, .toggle-btn { display: none !important; } .main { padding: 0; width: 100%; } .output-card { border: 1px solid #ccc; border-right: 5px solid black; break-inside: avoid; box-shadow: none; color: black; } h1 { color: black !important; text-align: center; } }
        @media (max-width: 600px) { .sidebar { position: absolute; right: 0; height: 100%; box-shadow: -5px 0 10px rgba(0,0,0,0.8); } }
    </style>
</head>
<body>
    <button class="toggle-btn" onclick="toggleSidebar()"><span>☰</span> الذاكرة</button>
    <div class="sidebar" id="mySidebar">
        <div class="sidebar-header"><span>السحابة الإمبراطورية</span><span style="cursor:pointer; font-size:1.2rem;" onclick="toggleSidebar()">×</span></div>
        <div class="memory-list" id="memList"></div>
    </div>
    <div class="main">
        <h1 style="color:var(--gold); margin-top:10px;">STRATEGIC-AI-CORE</h1>
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل الرابط أو الأمر الاستراتيجي...">
                <select id="langSelect">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                    <option value="Russian">Russian</option>
                    <option value="Chinese">Chinese</option>
                    <option value="French">French</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تنفيذ التحليل</button>
                <button class="action-btn btn-pdf" onclick="window.print()">تصدير PDF كامل</button>
                <button class="action-btn btn-clear" onclick="newSession()">جلسة جديدة</button>
            </div>
        </div>
        <div id="resultsArea" class="report-container"></div>
    </div>
    <script>
        let memory = JSON.parse(localStorage.getItem('imperial_mem_v8') || '[]');
        function toggleSidebar() { document.getElementById('mySidebar').classList.toggle('collapsed'); }
        function saveToCloud(title, content) {
            const id = Date.now();
            memory.unshift({ id, title, content, date: new Date().toLocaleTimeString() });
            localStorage.setItem('imperial_mem_v8', JSON.stringify(memory));
            renderSidebar();
        }
        function renderSidebar() {
            const list = document.getElementById('memList');
            list.innerHTML = memory.map(item => `
                <div class="mem-item" onclick="loadFromCloud(${item.id})">
                    <button class="del-btn" onclick="deleteItem(${item.id}, event)">×</button>
                    <div class="mem-title">${item.title}</div>
                    <div class="mem-date">${item.date}</div>
                </div>
            `).join('');
        }
        function deleteItem(id, event) {
            event.stopPropagation();
            if(!confirm("حذف؟")) return;
            memory = memory.filter(m => m.id !== id);
            localStorage.setItem('imperial_mem_v8', JSON.stringify(memory));
            renderSidebar();
        }
        function loadFromCloud(id) {
            const item = memory.find(m => m.id === id);
            if(item) { renderResults(item.content); if(window.innerWidth < 600) toggleSidebar(); }
        }
        function newSession() { document.getElementById('resultsArea').innerHTML = ""; document.getElementById('userInput').value = ""; }
        async function executeCore() {
            const val = document.getElementById('userInput').value;
            const lang = document.getElementById('langSelect').value;
            if(!val) return;
            const area = document.getElementById('resultsArea');
            area.innerHTML = `<div style="text-align:center; color:var(--gold);">جاري استخراج البيانات (Whale Mode)...</div>`;
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: lang })
                });
                const d = await r.json();
                renderResults(d.res);
                saveToCloud(val.substring(0, 25), d.res);
            } catch { area.innerHTML = "خطأ في الاتصال."; }
        }

        // --- التعديل الإمبراطوري المطلوب هنا ---
        function renderResults(text) {
            const area = document.getElementById('resultsArea');
            // التعديل: التقسيم فقط عند الأرقام الرئيسية المتبوعة بنقطة ومسافة (مثل 1. )
            // وهذا يمنع كسر الأرقام العشرية مثل 35.1
            const segments = text.split(/(?=\\d\\.\\s)/);
            area.innerHTML = segments.map(seg => {
                if(!seg.trim()) return '';
                return `
                <div class="output-card">
                    <div class="card-tools"><button class="copy-btn" onclick="copyText(this)">نسخ</button></div>
                    <div class="report-text">${seg.trim()}</div>
                </div>`;
            }).join('');
        }

        function copyText(btn) {
            const txt = btn.parentElement.nextElementSibling.innerText;
            navigator.clipboard.writeText(txt).then(() => {
                const orig = btn.innerText; btn.innerText = "تم";
                setTimeout(() => btn.innerText = orig, 1000);
            });
        }
        renderSidebar();
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
    sys_prompt = f"You are an Elite Strategy Analyst for M&A deals. Output Language: {data.get('lang')} ONLY. Analyze financial metrics, CAGR, net income, and risks. Use numbered lists (1. , 2. ) for main sections."
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": data.get('prompt')}]}
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=60)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except: return jsonify({"res": "Core Busy."})

if __name__ == '__main__':
    app.run(debug=True)


import os, requests, json
from flask import Flask, render_template_string, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# --- Imperial Core Config ---
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

# وظيفة استخباراتية لسحب النصوص من الروابط
def extract_source_content(user_input):
    """تحويل روابط يوتيوب إلى نصوص، أو تمرير النص المباشر"""
    if "youtube.com" in user_input or "youtu.be" in user_input:
        try:
            # استخراج ID الفيديو
            if "v=" in user_input:
                video_id = user_input.split("v=")[1].split("&")[0]
            else:
                video_id = user_input.split("/")[-1]
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar', 'en'])
            return " ".join([t['text'] for t in transcript_list])
        except Exception as e:
            return f"Strategic Warning: Could not bypass YouTube encryption. Details: {str(e)}"
    
    # في حال كان فيسبوك أو درايف أو نص عادي، يتم تمريره كما هو للمعالجة
    return user_input

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic-AI-Core - Imperial v8.5</title>
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
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); color: black; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; z-index: 2000; }
        .control-panel { width: 100%; max-width: 800px; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; margin-top: 40px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 10px; }
        input[type="text"] { flex: 1; background: #000; border: 1px solid var(--gold); color: white; padding: 10px; border-radius: 6px; }
        select { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 15px; border-radius: 6px; }
        .actions { display: flex; gap: 10px; }
        button.action-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-run { background: var(--gold); color: black; }
        .output-card { background: var(--panel); border-right: 5px solid var(--gold); padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .report-text { line-height: 1.8; font-size: 1rem; white-space: pre-wrap; }
    </style>
</head>
<body>
    <button class="toggle-btn" onclick="toggleSidebar()">☰ الذاكرة</button>
    <div class="sidebar" id="mySidebar">
        <div class="sidebar-header"><span>STRATEGIC-AI-CORE</span><span style="cursor:pointer;" onclick="toggleSidebar()">×</span></div>
        <div class="memory-list" id="memList"></div>
    </div>
    <div class="main">
        <h1 style="color:var(--gold);">STRATEGIC-AI-CORE</h1>
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل رابط YouTube أو النص الاستراتيجي المباشر...">
                <select id="langSelect">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تنفيذ التحليل السيادي</button>
            </div>
        </div>
        <div id="resultsArea" class="report-container"></div>
    </div>
    <script>
        let memory = JSON.parse(localStorage.getItem('strategic_mem_v8.5') || '[]');
        function toggleSidebar() { document.getElementById('mySidebar').classList.toggle('collapsed'); }
        function renderResults(text) {
            const area = document.getElementById('resultsArea');
            const segments = text.split(/(?=\\d\\.\\s)/);
            area.innerHTML = segments.map(seg => seg.trim() ? `<div class="output-card"><div class="report-text">${seg.trim()}</div></div>` : '').join('');
        }
        async function executeCore() {
            const val = document.getElementById('userInput').value;
            if(!val) return;
            document.getElementById('resultsArea').innerHTML = `<div style="text-align:center; color:var(--gold);">جاري استخراج البيانات وتحليل المحتوى...</div>`;
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: document.getElementById('langSelect').value })
                });
                const d = await r.json();
                renderResults(d.res);
            } catch { document.getElementById('resultsArea').innerHTML = "خطأ في الاتصال بالنواة."; }
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
    raw_input = data.get('prompt')
    
    # تحويل الرابط إلى نص فيديو (يوتيوب) أو تركه كما هو (نص مباشر)
    processed_content = extract_source_content(raw_input)
    
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    sys_prompt = f"You are an Elite Strategy Analyst. Language: {data.get('lang')}. Analyze financial metrics, risks, and CAGR. Protect decimals (e.g., 35.1%, $19.31B). Use numbered lists."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Analyze this content: {processed_content}"}
        ]
    }
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=60)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except: return jsonify({"res": "Core Busy."})

if __name__ == '__main__':
    app.run(debug=True)

import os, requests, json, re
from flask import Flask, render_template_string, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# --- Imperial Core Config ---
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_video_id(url):
    """استخراج معرف الفيديو بدقة من مختلف أشكال روابط يوتيوب"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_content(user_input):
    if "youtube.com" in user_input or "youtu.be" in user_input:
        vid = extract_video_id(user_input)
        if vid:
            try:
                # محاولة السحب بالعربية أولاً ثم الإنجليزية كبديل
                try:
                    ts = YouTubeTranscriptApi.get_transcript(vid, languages=['ar'])
                except:
                    ts = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
                return " ".join([t['text'] for t in ts])
            except Exception as e:
                return f"خطأ تقني في سحب النص: {str(e)}. يرجى نسخ النص يدوياً."
    return user_input

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Strategic-AI-Core - Imperial v8.6</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; --text: #eee; }
        body { background: var(--bg); color: var(--text); font-family: 'Tajawal', sans-serif; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 300px; background: #0a0a0a; border-left: 2px solid var(--gold); transition: 0.3s; z-index: 1000; }
        .sidebar.collapsed { margin-right: -300px; }
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; position: relative; }
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); border: none; padding: 10px; cursor: pointer; font-weight: bold; }
        .control-panel { width: 100%; max-width: 800px; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 50px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        input { flex: 1; background: #000; border: 1px solid var(--gold); color: #fff; padding: 12px; border-radius: 6px; }
        .actions { display: flex; gap: 10px; }
        .action-btn { flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .btn-run { background: var(--gold); color: #000; }
        .btn-pdf { background: #fff; color: #000; }
        .btn-clear { background: #333; color: #fff; }
        .output-card { background: #161616; border-right: 5px solid var(--gold); padding: 20px; margin-top: 20px; border-radius: 8px; width: 100%; max-width: 800px; }
        @media print { .sidebar, .control-panel, .toggle-btn { display: none; } }
    </style>
</head>
<body>
    <div class="sidebar" id="mySidebar"><div style="padding:20px; color:var(--gold); font-weight:bold;">STRATEGIC-AI-CORE</div></div>
    <div class="main">
        <button class="toggle-btn" onclick="toggleSidebar()">☰ الذاكرة</button>
        <h1 style="color:var(--gold);">STRATEGIC-AI-CORE</h1>
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل رابط YouTube أو النص الاستراتيجي...">
                <select id="langSelect" style="background:#222; color:var(--gold); border:1px solid var(--gold); border-radius:6px;">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تنفيذ التحليل</button>
                <button class="action-btn btn-pdf" onclick="window.print()">تصدير PDF</button>
                <button class="action-btn btn-clear" onclick="location.reload()">جلسة جديدة</button>
            </div>
        </div>
        <div id="resultsArea"></div>
    </div>
    <script>
        function toggleSidebar() { document.getElementById('mySidebar').classList.toggle('collapsed'); }
        async function executeCore() {
            const val = document.getElementById('userInput').value;
            if(!val) return;
            document.getElementById('resultsArea').innerHTML = '<div style="color:var(--gold); margin-top:20px;">جاري سحب البيانات والتحليل...</div>';
            const r = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompt: val, lang: document.getElementById('langSelect').value })
            });
            const d = await r.json();
            document.getElementById('resultsArea').innerHTML = `<div class="output-card">${d.res.replace(/\\n/g, '<br>')}</div>`;
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
    processed_content = get_content(data.get('prompt'))
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    sys_prompt = f"You are an Elite Strategy Analyst. Analyze this in {data.get('lang')}. Focus on financial numbers and CAGR. Use numbered lists."
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": processed_content}]}
    r = requests.post(URL, json=payload, headers=headers, timeout=60)
    return jsonify({"res": r.json()['choices'][0]['message']['content']})

if __name__ == '__main__': app.run(debug=True)

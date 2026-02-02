import os, requests, json
from flask import Flask, render_template_string, request, jsonify
import assemblyai as aai

app = Flask(__name__)

# --- Imperial Core Config ---
# تم حقن المفاتيح الخاصة بك هنا أيها الجنرال
aai.settings.api_key = "A7fd94e1bf2e409cbce77384ce76afae"
GROQ_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_audio_transcript(video_url):
    """تحويل صوت الفيديو إلى نص باستخدام الذكاء السحابي"""
    try:
        config = aai.TranscriptionConfig(language_detection=True)
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(video_url, config=config)
        
        if transcript.status == aai.TranscriptStatus.error:
            return f"Strategic Warning: {transcript.error}"
        return transcript.text
    except Exception as e:
        return f"Error in Intelligence Gathering: {str(e)}"

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Strategic-AI-Core - Imperial v9.1</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; --text: #eee; }
        body { background: var(--bg); color: var(--text); font-family: 'Tajawal', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: #0a0a0a; border-left: 2px solid var(--gold); transition: 0.3s; z-index: 1000; }
        .sidebar.collapsed { margin-right: -300px; opacity: 0; }
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; position: relative; }
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); border: none; padding: 10px; cursor: pointer; font-weight: bold; border-radius: 4px; }
        .control-panel { width: 100%; max-width: 800px; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 50px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        input { flex: 1; background: #000; border: 1px solid var(--gold); color: #fff; padding: 12px; border-radius: 6px; }
        select { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 10px; border-radius: 6px; cursor: pointer; }
        .actions { display: flex; gap: 10px; }
        .action-btn { flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-run { background: var(--gold); color: #000; }
        .btn-pdf { background: #fff; color: #000; }
        .btn-clear { background: #333; color: #fff; }
        .output-card { background: #161616; border-right: 5px solid var(--gold); padding: 20px; margin-top: 20px; border-radius: 8px; width: 100%; max-width: 800px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .report-text { line-height: 1.8; white-space: pre-wrap; }
        @media print { .sidebar, .control-panel, .toggle-btn { display: none !important; } .main { padding: 0; } .output-card { border: 1px solid #000; color: black; background: white; } }
    </style>
</head>
<body>
    <button class="toggle-btn" onclick="toggleSidebar()">☰ الذاكرة</button>
    <div class="sidebar" id="mySidebar">
        <div style="padding:20px; color:var(--gold); font-weight:bold; border-bottom:1px solid #333;">STRATEGIC-AI-CORE v9.1</div>
    </div>
    <div class="main">
        <h1 style="color:var(--gold);">STRATEGIC-AI-CORE</h1>
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل رابط الفيديو أو النص الاستراتيجي للتحليل...">
                <select id="langSelect">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                    <option value="French">Français</option>
                    <option value="Russian">Русский</option>
                    <option value="Chinese">中文</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تنفيذ التحليل السيادي</button>
                <button class="action-btn btn-pdf" onclick="window.print()">تصدير PDF</button>
                <button class="action-btn btn-clear" onclick="location.reload()">جلسة جديدة</button>
            </div>
        </div>
        <div id="resultsArea" style="width:100%; display:flex; flex-direction:column; align-items:center;"></div>
    </div>
    <script>
        function toggleSidebar() { document.getElementById('mySidebar').classList.toggle('collapsed'); }
        async function executeCore() {
            const val = document.getElementById('userInput').value;
            if(!val) return;
            document.getElementById('resultsArea').innerHTML = '<div style="color:var(--gold); margin-top:20px;">جاري تفعيل محرك الاستخبارات وتحليل المحتوى...</div>';
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: document.getElementById('langSelect').value })
                });
                const d = await r.json();
                document.getElementById('resultsArea').innerHTML = `<div class="output-card"><div class="report-text">${d.res.replace(/\\n/g, '<br>')}</div></div>`;
            } catch { document.getElementById('resultsArea').innerHTML = "فشل في الوصول للنواة."; }
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
    user_input = data.get('prompt')
    target_lang = data.get('lang')
    
    # المعالجة الذكية: إذا كان رابطاً نستخدم AssemblyAI، وإلا نستخدم النص مباشرة
    if user_input.startswith("http"):
        processed_content = get_audio_transcript(user_input)
    else:
        processed_content = user_input

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    
    # صياغة الأمر بناءً على اللغة المختارة
    sys_prompt = f"You are an Elite Strategy Analyst. Generate the report ONLY in {target_lang}. Focus on M&A language, financial metrics, and CAGR. Use numbered lists. If the content is empty or error, state that politely in {target_lang}."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Analyze this content for a professional acquirer: {processed_content}"}
        ]
    }
    
    try:
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=120)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"res": "Core processing timeout. Please try with a shorter segment."})

if __name__ == '__main__':
    app.run(debug=True)

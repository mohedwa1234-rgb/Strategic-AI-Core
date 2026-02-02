import os, requests, json
from flask import Flask, render_template_string, request, jsonify
import assemblyai as aai

app = Flask(__name__)

# --- Imperial Core Config ---
# تم حقن المفتاح الجديد للجنرال
aai.settings.api_key = "92e0a59a85c1445089ef1606a374bd71"
GROQ_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_audio_transcript(video_url):
    try:
        # إجبارية المصادقة لكل طلب لضمان عدم حدوث خطأ Authenticate
        aai.settings.api_key = "92e0a59a85c1445089ef1606a374bd71"
        config = aai.TranscriptionConfig(language_detection=True)
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(video_url, config=config)
        return transcript.text if transcript.status != aai.TranscriptStatus.error else f"Warning: {transcript.error}"
    except Exception as e:
        return f"Intelligence Error: {str(e)}"

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Strategic-AI-Core v9.5</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; --text: #eee; }
        body { background: var(--bg); color: var(--text); font-family: 'Tajawal', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* القائمة الجانبية المحدثة */
        .sidebar { width: 300px; background: #0a0a0a; border-left: 2px solid var(--gold); transition: 0.4s; display: flex; flex-direction: column; }
        .sidebar.hidden { margin-right: -302px; }
        .sidebar-header { padding: 20px; color: var(--gold); font-weight: bold; border-bottom: 1px solid #333; text-align: center; }
        .history-list { flex: 1; overflow-y: auto; padding: 10px; }
        .history-item { background: #1a1a1a; padding: 10px; margin-bottom: 8px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; border-right: 3px solid var(--gold); }

        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; position: relative; }
        
        /* زر التحكم في القائمة */
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); border: none; padding: 12px 18px; cursor: pointer; font-weight: bold; border-radius: 6px; z-index: 2000; box-shadow: 0 0 10px rgba(197, 160, 33, 0.4); }
        
        .control-panel { width: 100%; max-width: 850px; background: #111; padding: 25px; border-radius: 12px; border: 1px solid #333; margin-top: 60px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; background: #000; border: 1px solid var(--gold); color: #fff; padding: 14px; border-radius: 6px; }
        select { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 15px; border-radius: 6px; }
        
        .actions { display: flex; gap: 12px; }
        .action-btn { flex: 1; padding: 14px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-run { background: var(--gold); color: #000; }
        .btn-pdf { background: #fff; color: #000; }
        .btn-clear { background: #444; color: #fff; }
        
        .output-card { background: #161616; border-right: 5px solid var(--gold); padding: 30px; margin-top: 25px; border-radius: 10px; width: 100%; max-width: 850px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); }
        .report-text { line-height: 2; white-space: pre-wrap; font-size: 1.1rem; }
        
        @media print { .sidebar, .control-panel, .toggle-btn { display: none !important; } .main { padding: 0; } .output-card { border: 2px solid #000; color: black; background: white; } }
    </style>
</head>
<body>
    <button class="toggle-btn" onclick="toggleSidebar()">☰ القائمة الاستراتيجية</button>
    
    <div class="sidebar" id="mySidebar">
        <div class="sidebar-header">سجل العمليات السحابية</div>
        <div class="history-list" id="historyList">
            </div>
    </div>

    <div class="main">
        <h1 style="color:var(--gold); letter-spacing: 3px;">STRATEGIC-AI-CORE v9.5</h1>
        
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل رابط الفيديو أو النص للتحليل المالي...">
                <select id="langSelect">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                    <option value="French">Français</option>
                    <option value="Russian">Русский</option>
                    <option value="Chinese">中文</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تشغيل النواة</button>
                <button class="action-btn btn-pdf" onclick="window.print()">تصدير PDF</button>
                <button class="action-btn btn-clear" onclick="clearSession()">تصفير الجلسة</button>
            </div>
        </div>
        
        <div id="resultsArea" style="width:100%; display:flex; flex-direction:column; align-items:center;"></div>
    </div>

    <script>
        // نظام التخزين السحابي المحاكي
        let history = JSON.parse(localStorage.getItem('strategic_history') || '[]');

        function updateHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = history.map((h, i) => `
                <div class="history-item" onclick="loadHistory(${i})">
                    <b>${h.date}</b><br>${h.title.substring(0, 30)}...
                </div>
            `).join('');
            localStorage.setItem('strategic_history', JSON.stringify(history));
        }

        function toggleSidebar() { 
            document.getElementById('mySidebar').classList.toggle('hidden'); 
        }

        function loadHistory(i) {
            document.getElementById('resultsArea').innerHTML = `<div class="output-card"><div class="report-text">${history[i].content}</div></div>`;
        }

        function clearSession() {
            localStorage.removeItem('strategic_history');
            location.reload();
        }

        async function executeCore() {
            const val = document.getElementById('userInput').value;
            if(!val) return;
            document.getElementById('resultsArea').innerHTML = '<div style="color:var(--gold); margin-top:20px;">جاري المصادقة وتحليل البيانات...</div>';
            
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: document.getElementById('langSelect').value })
                });
                const d = await r.json();
                const content = d.res.replace(/\\n/g, '<br>');
                
                // حفظ في السجل
                history.unshift({
                    date: new Date().toLocaleString('ar-EG'),
                    title: val.startsWith('http') ? 'تحليل فيديو' : val,
                    content: content
                });
                updateHistory();

                document.getElementById('resultsArea').innerHTML = `<div class="output-card"><div class="report-text">${content}</div></div>`;
            } catch {
                document.getElementById('resultsArea').innerHTML = "فشل في معالجة النواة.";
            }
        }
        updateHistory();
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
    if user_input.startswith("http"):
        processed_content = get_audio_transcript(user_input)
    else:
        processed_content = user_input

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    sys_prompt = f"You are an Elite M&A Strategy Analyst. Report Language: {data.get('lang')}. Focus on CAGR, Financial Margins, and Valuation. Professional Whale language."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Analyze: {processed_content}"}
        ]
    }
    r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=120)
    return jsonify({"res": r.json()['choices'][0]['message']['content']})

if __name__ == '__main__':
    app.run(debug=True)

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
    <title>Strategic AI Core - Imperial Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #0f0f0f; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; }
        
        /* الذاكرة السحابية الجانبية */
        .sidebar { width: 250px; background: var(--panel); border-right: 1px solid var(--gold); padding: 20px; overflow-y: auto; }
        .history-item { padding: 10px; border: 1px solid #333; margin-bottom: 10px; border-radius: 5px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; }
        .history-item:hover { border-color: var(--gold); background: #1a1a1a; }

        /* منطقة العمل الرئيسية */
        .main { flex: 1; padding: 40px; overflow-y: auto; text-align: center; }
        .input-box { width: 100%; max-width: 600px; background: #111; border: 1px solid var(--gold); color: white; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
        
        /* نافذة المخرجات المستقلة */
        .output-container { display: flex; flex-direction: column-reverse; gap: 20px; margin-top: 30px; }
        .output-card { background: var(--panel); border-left: 5px solid var(--gold); padding: 20px; text-align: left; border-radius: 8px; position: relative; animation: slideIn 0.5s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        button { background: var(--gold); color: black; border: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer; margin: 5px; }
        .pdf-btn { background: #d4d4d4; font-size: 0.7rem; padding: 5px 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3 style="color:var(--gold)">الذاكرة السحابية</h3>
        <div id="history"></div>
    </div>
    
    <div class="main">
        <h1 style="color:var(--gold); letter-spacing:3px;">STRATEGIC-AI-CORE</h1>
        <textarea id="inp" class="input-box" rows="3" placeholder="أدخل الرابط أو المطلب الاستراتيجي..."></textarea><br>
        <button onclick="execute()">إرسال الأمر</button>
        
        <div id="outputs" class="output-container"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let memory = JSON.parse(localStorage.getItem('ai_memory') || '[]');

        function updateSidebar() {
            const h = document.getElementById('history');
            h.innerHTML = memory.map((m, i) => `<div class="history-item" onclick="loadMem(${i})">${m.title}</div>`).join('');
        }

        async function execute() {
            const val = document.getElementById('inp').value;
            if(!val) return;
            
            const cardId = 'card-' + Date.now();
            const container = document.getElementById('outputs');
            
            // إنشاء نافذة مخرجات مستقلة
            const card = document.createElement('div');
            card.className = 'output-card';
            card.id = cardId;
            card.innerHTML = `<b>جاري الاستخراج...</b>`;
            container.prepend(card);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val })
                });
                const data = await res.json();
                const content = data.res || data.err;
                
                card.innerHTML = `
                    <small style="color:var(--gold)">${new Date().toLocaleTimeString()}</small>
                    <p>${content}</p>
                    <button class="pdf-btn" onclick="downloadPDF('${cardId}')">حفظ كـ PDF</button>
                `;

                // حفظ في الذاكرة السحابية
                memory.push({ title: val.substring(0, 25) + '...', content: content });
                localStorage.setItem('ai_memory', JSON.stringify(memory));
                updateSidebar();

            } catch { card.innerHTML = "فشل الاتصال بالنواة."; }
        }

        function downloadPDF(id) {
            const doc = new jsPDF();
            const text = document.getElementById(id).innerText;
            doc.text(text, 10, 10, { maxWidth: 180 });
            doc.save(`Strategy_Report_${id}.pdf`);
        }

        updateSidebar();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt')
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a top-tier M&A strategic analyst. Provide data-driven executive summaries."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(URL, json=payload, headers=headers)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"err": "Core Busy."})

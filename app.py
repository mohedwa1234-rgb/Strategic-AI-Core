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
    <title>Strategic AI Core - Fixed Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #0f0f0f; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: var(--panel); border-left: 1px solid var(--gold); padding: 20px; overflow-y: auto; }
        .main { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .input-box { width: 100%; max-width: 650px; background: #111; border: 1px solid var(--gold); color: white; padding: 15px; border-radius: 12px; margin-bottom: 10px; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; }
        select, button { background: var(--gold); color: black; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        
        /* إصلاح ميزان النوافذ والنسخ */
        .result-wrapper { display: flex; align-items: stretch; gap: 10px; width: 100%; max-width: 800px; margin-top: 15px; }
        .output-card { flex: 1; background: var(--panel); border-right: 4px solid var(--gold); padding: 15px; border-radius: 10px; line-height: 1.6; }
        .copy-trigger { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 10px; border-radius: 8px; cursor: pointer; writing-mode: vertical-rl; font-size: 0.7rem; }
        
        .history-item { background: #1a1a1a; padding: 10px; margin-bottom: 10px; border-radius: 8px; font-size: 0.8rem; cursor: pointer; border: 1px solid #333; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3 style="color:var(--gold)">الذاكرة السحابية الدائمة</h3>
        <div id="historyList"></div>
    </div>
    <div class="main">
        <h1 style="color:var(--gold)">STRATEGIC-AI-CORE</h1>
        <div class="controls">
            <select id="lang"><option value="Arabic">العربية</option><option value="English">English</option></select>
            <button onclick="execute()">تحليل الرابط السيادي</button>
            <button id="pdfBtn" onclick="generatePDF()" style="background:#fff">تصدير PDF الشامل</button>
        </div>
        <textarea id="inp" class="input-box" rows="2" placeholder="ضع الرابط هنا..."></textarea>
        <div id="results"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let memory = JSON.parse(localStorage.getItem('final_mem_v4') || '[]');

        function renderHistory() {
            document.getElementById('historyList').innerHTML = memory.map(m => `<div class="history-item">${m.title}<br><small>${m.date}</small></div>`).join('');
        }

        async function execute() {
            const val = document.getElementById('inp').value;
            const lg = document.getElementById('lang').value;
            if(!val) return;
            const resContainer = document.getElementById('results');
            resContainer.innerHTML = "<p style='color:var(--gold)'>جاري التجهيز...</p>";

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: lg })
                });
                const d = await r.json();
                const segments = d.res.split(/(?=\\d\\.)/);
                resContainer.innerHTML = "";
                
                segments.forEach((seg, i) => {
                    const wrap = document.createElement('div');
                    wrap.className = 'result-wrapper';
                    wrap.innerHTML = `
                        <div class="output-card"><div class="content-text">${seg.trim()}</div></div>
                        <div class="copy-trigger" onclick="copyText(this)">نسخ المحتوى</div>
                    `;
                    resContainer.appendChild(wrap);
                });

                memory.unshift({ title: val.substring(0,30), content: d.res, date: new Date().toLocaleString() });
                localStorage.setItem('final_mem_v4', JSON.stringify(memory));
                renderHistory();
            } catch { resContainer.innerHTML = "خطأ في النواة."; }
        }

        function copyText(el) {
            const text = el.previousElementSibling.innerText;
            navigator.clipboard.writeText(text);
            el.style.background = "white"; el.innerText = "تم النسخ";
            setTimeout(() => { el.style.background = "#222"; el.innerText = "نسخ المحتوى"; }, 1000);
        }

        function generatePDF() {
            const doc = new jsPDF();
            let y = 15;
            doc.setFontSize(16); doc.text("Strategic Analysis Report 2026", 10, y);
            y += 15;
            doc.setFontSize(11);
            document.querySelectorAll('.content-text').forEach(el => {
                const lines = doc.splitTextToSize(el.innerText, 180);
                doc.text(lines, 10, y);
                y += (lines.length * 7) + 10;
                if (y > 270) { doc.addPage(); y = 15; }
            });
            doc.save('Full_Strategic_Report.pdf');
        }
        renderHistory();
    </script>
</body>
</html>

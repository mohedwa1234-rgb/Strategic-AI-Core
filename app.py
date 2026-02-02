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
    <title>Strategic AI Core - Mobile Optimized</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #0f0f0f; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: var(--panel); padding: 15px; border-bottom: 2px solid var(--gold); text-align: center; }
        .sidebar { background: #111; padding: 10px; height: 120px; overflow-x: auto; display: flex; gap: 10px; border-bottom: 1px solid #333; }
        .main { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .input-box { width: 90%; background: #111; border: 1px solid var(--gold); color: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .nav-btns { display: flex; gap: 5px; margin-bottom: 20px; width: 95%; }
        button { flex: 1; background: var(--gold); color: black; border: none; padding: 12px 5px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; }
        
        /* مظهر النوافذ الجديد للجوال */
        .output-card { width: 95%; background: var(--panel); border: 1px solid #333; border-right: 5px solid var(--gold); padding: 15px; border-radius: 10px; margin-bottom: 15px; box-sizing: border-box; }
        .copy-bar { margin-top: 10px; display: flex; justify-content: flex-end; }
        .btn-copy { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 15px; border-radius: 4px; font-size: 0.75rem; }
        .history-card { min-width: 150px; background: #222; padding: 8px; border-radius: 5px; font-size: 0.7rem; border: 1px solid #444; }
    </style>
</head>
<body>
    <div class="header"><h2 style="color:var(--gold); margin:0;">STRATEGIC-AI-CORE</h2></div>
    <div class="sidebar" id="historyList"></div>

    <div class="main">
        <textarea id="inp" class="input-box" rows="2" placeholder="ضع الرابط الاستراتيجي..."></textarea>
        <div class="nav-btns">
            <button onclick="execute()">تحليل الرابط</button>
            <button onclick="downloadPDF()" style="background:#fff">حفظ التقرير (PDF)</button>
        </div>
        <div id="results" style="width:100%;"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let mem = JSON.parse(localStorage.getItem('mob_v5') || '[]');

        function renderMem() {
            document.getElementById('historyList').innerHTML = mem.map(m => `<div class="history-card">${m.t}</div>`).join('');
        }

        async function execute() {
            const val = document.getElementById('inp').value;
            if(!val) return;
            const resBox = document.getElementById('results');
            resBox.innerHTML = "<p style='color:var(--gold); text-align:center;'>جاري الاختراق والتحليل...</p>";

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val })
                });
                const d = await r.json();
                const segments = d.res.split(/(?=\\d\\.)/);
                resBox.innerHTML = "";
                
                segments.forEach((seg, i) => {
                    const card = document.createElement('div');
                    card.className = 'output-card';
                    card.innerHTML = `
                        <div class="content-body">${seg.trim()}</div>
                        <div class="copy-bar"><button class="btn-copy" onclick="copyMe(this)">نسخ النص</button></div>
                    `;
                    resBox.appendChild(card);
                });

                mem.unshift({ t: val.substring(0,25), c: d.res });
                localStorage.setItem('mob_v5', JSON.stringify(mem));
                renderMem();
            } catch { resBox.innerHTML = "النواة مشغولة."; }
        }

        function copyMe(btn) {
            const text = btn.parentElement.previousElementSibling.innerText;
            const el = document.createElement('textarea');
            el.value = text; document.body.appendChild(el);
            el.select(); document.execCommand('copy');
            document.body.removeChild(el);
            btn.innerText = "تم!"; setTimeout(() => btn.innerText = "نسخ النص", 1000);
        }

        function downloadPDF() {
            const doc = new jsPDF();
            let y = 15;
            doc.text("Strategic Analysis - General", 10, y);
            y += 10;
            document.querySelectorAll('.content-body').forEach(el => {
                const lines = doc.splitTextToSize(el.innerText, 180);
                doc.text(lines, 10, y);
                y += (lines.length * 7) + 10;
                if(y > 270) { doc.addPage(); y = 15; }
            });
            doc.save('Strategic_Report.pdf');
        }
        renderMem();
    </script>
</body>
</html>

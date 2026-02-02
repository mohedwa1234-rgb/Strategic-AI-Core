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
    <title>Strategic AI Core - Final Authority</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #000; padding: 15px; border-bottom: 2px solid var(--gold); text-align: center; }
        .sidebar { background: #0a0a0a; padding: 10px; height: 100px; overflow-x: auto; display: flex; gap: 10px; border-bottom: 1px solid #333; }
        .main { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .input-box { width: 90%; background: #1a1a1a; border: 1px solid var(--gold); color: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .nav-btns { display: flex; gap: 8px; margin-bottom: 20px; width: 95%; }
        button { flex: 1; background: var(--gold); color: black; border: none; padding: 12px; border-radius: 5px; font-weight: bold; font-size: 0.85rem; cursor: pointer; }
        .output-card { width: 95%; background: var(--panel); border: 1px solid #333; border-right: 5px solid var(--gold); padding: 15px; border-radius: 10px; margin-bottom: 15px; position: relative; }
        .btn-copy { position: absolute; left: 10px; top: 10px; background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; }
        .history-card { min-width: 160px; background: #111; padding: 8px; border-radius: 5px; font-size: 0.75rem; border: 1px solid #444; }
    </style>
</head>
<body>
    <div class="header"><h2 style="color:var(--gold); margin:0;">STRATEGIC-AI-CORE</h2></div>
    <div class="sidebar" id="historyList"></div>
    <div class="main">
        <textarea id="inp" class="input-box" rows="2" placeholder="أدخل الرابط للفحص..."></textarea>
        <div class="nav-btns">
            <button onclick="execute()">تنفيذ التحليل</button>
            <button onclick="saveFullPDF()" style="background:#fff">تصدير PDF الشامل</button>
        </div>
        <div id="results" style="width:100%;"></div>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let memory = JSON.parse(localStorage.getItem('final_v6') || '[]');

        function renderHistory() {
            document.getElementById('historyList').innerHTML = memory.map(m => `<div class="history-card">${m.t}</div>`).join('');
        }

        async function execute() {
            const val = document.getElementById('inp').value;
            if(!val) return;
            const resBox = document.getElementById('results');
            resBox.innerHTML = "<p style='color:var(--gold); text-align:center;'>جاري معالجة البيانات...</p>";

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
                        <button class="btn-copy" onclick="copyNative(this)">نسخ</button>
                        <div class="content-body">${seg.trim()}</div>
                    `;
                    resBox.appendChild(card);
                });
                memory.unshift({ t: val.substring(0,30), c: d.res });
                localStorage.setItem('final_v6', JSON.stringify(memory));
                renderHistory();
            } catch { resBox.innerHTML = "خطأ في النواة."; }
        }

        function copyNative(btn) {
            const text = btn.nextElementSibling.innerText;
            const temp = document.createElement('textarea');
            temp.value = text; document.body.appendChild(temp);
            temp.select();
            try {
                document.execCommand('copy');
                btn.innerText = "تم!";
            } catch {
                alert("يرجى النسخ يدوياً: " + text);
            }
            document.body.removeChild(temp);
            setTimeout(() => btn.innerText = "نسخ", 1500);
        }

        function saveFullPDF() {
            try {
                const doc = new jsPDF();
                let y = 15;
                doc.text("Strategic-AI-Core Report", 10, y);
                y += 10;
                document.querySelectorAll('.content-body').forEach(el => {
                    const lines = doc.splitTextToSize(el.innerText, 180);
                    doc.text(lines, 10, y);
                    y += (lines.length * 7) + 10;
                    if (y > 270) { doc.addPage(); y = 15; }
                });
                doc.save('Full_Report.pdf');
            } catch (e) { alert("حدث خطأ أثناء توليد PDF، يرجى المحاولة من اللابتوب."); }
        }
        renderHistory();
    </script>
</body>
</html>

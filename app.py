import os, requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Imperial Connection: Strategic AI Core ---
# المفتاح الجديد محقون هنا مباشرة للاختصار
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """
<!DOCTYPE html>
<html>
<body style="background:#050505;color:white;font-family:sans-serif;text-align:center;padding:50px;">
    <h2 style="color:#c5a021;letter-spacing:2px;">STRATEGIC AI CORE</h2>
    <textarea id="i" style="width:100%;max-width:400px;background:#111;color:white;padding:15px;border:1px solid #c5a021;border-radius:10px;" rows="4" placeholder="Paste URL here..."></textarea><br><br>
    <button onclick="run()" style="background:#c5a021;padding:15px 40px;border-radius:10px;font-weight:bold;cursor:pointer;border:none;">EXECUTE ANALYSIS</button>
    <div id="r" style="margin-top:20px;text-align:left;max-width:400px;margin-left:auto;margin-right:auto;color:#ccc;line-height:1.6;"></div>
    <script>
        async function run(){
            const r=document.getElementById('r');
            r.innerHTML="Connecting to Oracle Core...";
            const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({p:document.getElementById('i').value})});
            const d=await res.json();
            r.innerHTML="<b>Analysis:</b><br>"+(d.res || d.err);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json.get('p')
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Analyze this link/prompt for an Enterprise Acquirer in professional M&A language."}, {"role": "user", "content": data}]
    }
    try:
        r = requests.post(URL, json=payload, headers=headers)
        return jsonify({"res": r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"err": "Core Busy. Re-executing..."})

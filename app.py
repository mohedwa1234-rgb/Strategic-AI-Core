import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Imperial Core Config ---
GROK_API_KEY = "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"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic AI Core</title>
    <style>
        :root { --gold: #c5a021; --dark: #0f0f0f; }
        body { background: #050505; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .terminal { background: var(--dark); border: 1px solid var(--gold); padding: 30px; border-radius: 15px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 0 20px rgba(197, 160, 33, 0.2); }
        h1 { color: var(--gold); letter-spacing: 2px; text-transform: uppercase; font-size: 1.5rem; }
        textarea { width: 100%; background: #1a1a1a; border: 1px solid #333; color: #ddd; padding: 12px; border-radius: 8px; margin: 15px 0; box-sizing: border-box; }
        button { background: var(--gold); color: black; border: none; width: 100%; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
        #res { margin-top: 20px; padding: 15px; background: #151515; border-left: 3px solid var(--gold); font-size: 0.85rem; text-align: left; display: none; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="terminal">
        <h1>Imperial AI Oracle</h1>
        <textarea id="inp" rows="4" placeholder="Paste URL here..."></textarea>
        <button onclick="run()">Execute Analysis</button>
        <div id="res"></div>
    </div>
    <script>
        async function run() {
            const inp = document.getElementById('inp').value;
            const res = document.getElementById('res');
            if(!inp) return;
            res.style.display = "block";
            res.innerHTML = "Processing Strategic Request...";
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: inp })
                });
                const d = await r.json();
                res.innerHTML = "<b>Result:</b><br><br>" + (d.result || d.error);
            } catch (err) { res.innerHTML = "Connection Severed."; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # صمام الأمان: محاولة قراءة البيانات بأكثر من طريقة لمنع خطأ 'str'
        if request.is_json:
            data = request.get_json()
        else:
            import json
            data = json.loads(request.data.decode('utf-8'))
            
        user_prompt = data.get('prompt', 'No prompt provided')
        
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": "You are a strategic AI. Analyze the URL/Prompt for an executive."},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        r = requests.post(GROK_API_URL, json=payload, headers=headers)
        r_json = r.json()
        
        if 'choices' in r_json:
            return jsonify({"result": r_json['choices'][0]['message']['content']})
        return jsonify({"error": "Grok Engine Busy. Try again."})
        
    except Exception as e:
        return jsonify({"error": f"Core Security Trigger: {str(e)}"}), 500

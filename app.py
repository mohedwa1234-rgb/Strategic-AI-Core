import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Imperial Core: Secure Connectivity ---
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
        .terminal { background: var(--dark); border: 1px solid var(--gold); padding: 30px; border-radius: 15px; width: 350px; text-align: center; box-shadow: 0 0 20px rgba(197, 160, 33, 0.2); }
        h1 { color: var(--gold); letter-spacing: 2px; font-size: 1.5rem; margin-bottom: 5px; }
        p { color: #888; font-size: 0.8rem; margin-bottom: 20px; }
        textarea { width: 100%; background: #1a1a1a; border: 1px solid #333; color: #ddd; padding: 10px; border-radius: 8px; margin-bottom: 15px; box-sizing: border-box; resize: none; }
        button { background: var(--gold); color: black; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
        #res { margin-top: 20px; padding: 10px; background: #151515; border-left: 3px solid var(--gold); font-size: 0.85rem; text-align: left; display: none; line-height: 1.4; }
    </style>
</head>
<body>
    <div class="terminal">
        <h1>IMPERIAL AI ORACLE</h1>
        <p>Enterprise AI Engine for Strategic Content</p>
        <textarea id="inp" rows="4" placeholder="Enter your strategic prompt or URL..."></textarea>
        <button onclick="run()">Execute Analysis</button>
        <div id="res"></div>
    </div>
    <script>
        async function run() {
            const inp = document.getElementById('inp').value;
            const res = document.getElementById('res');
            if(!inp) return;
            res.style.display = "block";
            res.innerHTML = "Analyzing System Log...";
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: inp })
                });
                const d = await r.json();
                res.innerHTML = "<b>Analysis:</b><br>" + (d.result || d.error);
            } catch { res.innerHTML = "Link Failed."; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json.get('prompt')
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a strategic AI analyst. Summarize and analyze the provided content or URL for a high-level executive."},
            {"role": "user", "content": data}
        ]
    }
    try:
        r = requests.post(GROK_API_URL, json=payload, headers=headers)
        r_json = r.json()
        if 'choices' in r_json:
            return jsonify({"result": r_json['choices'][0]['message']['content']})
        return jsonify({"error": f"API Error: {r_json.get('error', {}).get('message', 'Unknown')}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

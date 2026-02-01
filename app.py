import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- بروتوكول الأمن: مفتاح جروك السيادي ---
GROK_API_KEY = "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"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

app.config['APP_NAME'] = "IMPERIAL AI ORACLE"

# --- الواجهة الراقية (The High-Value UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }}</title>
    <style>
        :root { --gold: #d4af37; --black: #050505; --slate: #121212; }
        body { background: var(--black); color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: var(--slate); border: 1px solid var(--gold); padding: 40px; border-radius: 20px; width: 90%; max-width: 550px; box-shadow: 0 0 50px rgba(212, 175, 55, 0.15); text-align: center; }
        h1 { color: var(--gold); text-transform: uppercase; letter-spacing: 5px; margin-bottom: 10px; font-size: 1.8rem; }
        p { opacity: 0.6; font-size: 0.9rem; margin-bottom: 30px; }
        textarea { width: 100%; padding: 15px; background: #1a1a1a; border: 1px solid #333; color: white; border-radius: 10px; margin-bottom: 20px; resize: none; box-sizing: border-box; }
        textarea:focus { border-color: var(--gold); outline: none; }
        button { background: var(--gold); color: black; border: none; padding: 15px 30px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.4s; text-transform: uppercase; letter-spacing: 2px; }
        button:hover { background: #fff; transform: scale(1.02); box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }
        #output { margin-top: 30px; text-align: left; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 10px; display: none; line-height: 1.7; border-left: 5px solid var(--gold); }
        .loading { display: none; color: var(--gold); margin: 15px 0; font-weight: bold; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ name }}</h1>
        <p>Enterprise AI Engine for Strategic Content</p>
        <textarea id="input" rows="5" placeholder="Enter your strategic prompt or URL..."></textarea>
        <button onclick="execute()">Execute Analysis</button>
        <div id="loader" class="loading">Consulting the Grok Engine...</div>
        <div id="output"></div>
    </div>

    <script>
        async function execute() {
            const input = document.getElementById('input').value;
            const output = document.getElementById('output');
            const loader = document.getElementById('loader');

            if(!input) return alert("General, input is required for execution.");

            loader.style.display = "block";
            output.style.display = "none";

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: input })
                });
                const data = await response.json();
                loader.style.display = "none";
                output.style.display = "block";
                output.innerText = data.result;
            } catch (err) {
                loader.style.display = "none";
                alert("Strategic Link Failure. Check API or Server.");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, name=app.config['APP_NAME'])

@app.route('/api/chat', methods=['POST'])
def chat():
    user_data = request.json.get('prompt')
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a world-class strategic advisor. Provide insightful, powerful, and concise content."},
            {"role": "user", "content": user_data}
        ]
    }

    try:
        r = requests.post(GROK_API_URL, json=payload, headers=headers)
        result = r.json()['choices'][0]['message']['content']
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": "The core is under maintenance. Error: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


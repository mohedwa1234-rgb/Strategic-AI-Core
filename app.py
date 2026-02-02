import os, requests, json
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- SaaS Configuration (الإضافات الجديدة) ---
app.secret_key = 'imperial_secret_key_change_this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imperial_saas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Imperial Core Config (كما هي) ---
KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

# --- Database Models (SaaS Structure) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    plan = db.Column(db.String(50), default='Free') # Free, Pro, Imperial
    credits = db.Column(db.Integer, default=5) # رصيد مجاني أولي

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- HTML Templates (تم فصلها لخدمة الـ SaaS) ---

# 1. Login/Register Style (مشترك)
AUTH_STYLE = """
<style>
    body { background: #050505; color: #eee; font-family: 'Tajawal', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .auth-box { background: #111; border: 1px solid #c5a021; padding: 40px; border-radius: 10px; width: 350px; text-align: center; box-shadow: 0 0 20px rgba(197, 160, 33, 0.2); }
    h2 { color: #c5a021; margin-bottom: 20px; }
    input { width: 90%; padding: 10px; margin: 10px 0; background: #000; border: 1px solid #444; color: white; border-radius: 5px; }
    button { width: 100%; padding: 10px; background: #c5a021; color: black; border: none; font-weight: bold; cursor: pointer; border-radius: 5px; margin-top: 10px; }
    button:hover { background: #d4af37; }
    a { color: #888; text-decoration: none; font-size: 0.9rem; display: block; margin-top: 15px; }
    .flash { color: #ff4444; margin-bottom: 10px; font-size: 0.9rem; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
"""

LOGIN_HTML = AUTH_STYLE + """
<div class="auth-box">
    <h2>GATE OF THE GENERAL</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}
    {% endwith %}
    <form method="POST">
        <input type="text" name="username" placeholder="اسم المستخدم" required>
        <input type="password" name="password" placeholder="كلمة المرور" required>
        <button type="submit">دخول النظام</button>
    </form>
    <a href="/register">إنشاء حساب جديد</a>
</div>
"""

REGISTER_HTML = AUTH_STYLE + """
<div class="auth-box">
    <h2>NEW RECRUIT</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}
    {% endwith %}
    <form method="POST">
        <input type="text" name="username" placeholder="اختر اسم مستخدم" required>
        <input type="password" name="password" placeholder="كلمة المرور" required>
        <button type="submit">انضمام للإمبراطورية</button>
    </form>
    <a href="/login">لدي حساب بالفعل</a>
</div>
"""

# 2. Main Dashboard (نفس الواجهة القديمة مع تحديثات SaaS)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic AI Core - SaaS v10</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a021; --bg: #050505; --panel: #111; --text: #eee; }
        body { background: var(--bg); color: var(--text); font-family: 'Tajawal', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar Updated for SaaS */
        .sidebar { width: 300px; background: #0a0a0a; border-left: 2px solid var(--gold); display: flex; flex-direction: column; transition: all 0.3s ease; position: relative; z-index: 1000; }
        .sidebar.collapsed { margin-right: -300px; opacity: 0; }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #333; text-align: center; color: var(--gold); font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        
        .user-info { padding: 15px; background: #151515; border-bottom: 1px solid #333; text-align: center; }
        .plan-badge { background: var(--gold); color: black; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
        .credits-count { color: #aaa; font-size: 0.9rem; margin-top: 5px; }
        
        .memory-list { flex: 1; overflow-y: auto; padding: 10px; }
        .mem-item { background: #1a1a1a; padding: 10px; margin-bottom: 8px; border-radius: 6px; border: 1px solid #333; cursor: pointer; position: relative; transition: 0.2s; }
        .mem-item:hover { border-color: var(--gold); background: #222; }
        .mem-title { font-size: 0.85rem; font-weight: bold; margin-bottom: 5px; padding-left: 25px; }
        .mem-date { font-size: 0.7rem; color: #888; }
        .del-btn { position: absolute; left: 5px; top: 5px; background: #500; color: white; border: none; width: 20px; height: 20px; border-radius: 50%; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        
        .logout-btn { display: block; margin: 10px; padding: 10px; background: #333; color: white; text-align: center; text-decoration: none; border-radius: 6px; border: 1px solid #555; }
        
        /* Main Area */
        .main { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; }
        .toggle-btn { position: absolute; top: 20px; right: 20px; background: var(--gold); color: black; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; z-index: 2000; display: flex; align-items: center; gap: 5px; }
        .control-panel { width: 100%; max-width: 800px; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; margin-top: 40px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 10px; }
        input[type="text"] { flex: 1; background: #000; border: 1px solid var(--gold); color: white; padding: 10px; border-radius: 6px; }
        select { background: #222; color: var(--gold); border: 1px solid var(--gold); padding: 5px 15px; border-radius: 6px; }
        .actions { display: flex; gap: 10px; }
        button.action-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-run { background: var(--gold); color: black; }
        .btn-pdf { background: #fff; color: black; }
        .btn-clear { background: #333; color: white; }
        .report-container { width: 100%; max-width: 850px; }
        .output-card { background: var(--panel); border-right: 5px solid var(--gold); padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); position: relative; }
        .card-tools { display: flex; justify-content: flex-end; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .copy-btn { background: #222; color: var(--gold); border: 1px solid #444; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
        .report-text { line-height: 1.8; font-size: 1rem; white-space: pre-wrap; }
        
        @media print { .sidebar, .control-panel, .card-tools, .toggle-btn { display: none !important; } .main { padding: 0; width: 100%; } .output-card { border: 1px solid #ccc; border-right: 5px solid black; box-shadow: none; color: black; } h1 { color: black !important; text-align: center; } }
        @media (max-width: 600px) { .sidebar { position: absolute; right: 0; height: 100%; box-shadow: -5px 0 10px rgba(0,0,0,0.8); } }
    </style>
</head>
<body>
    <button class="toggle-btn" onclick="toggleSidebar()"><span>☰</span> الذاكرة</button>

    <div class="sidebar" id="mySidebar">
        <div class="sidebar-header">
            <span>SaaS Core</span>
            <span style="cursor:pointer; font-size:1.2rem;" onclick="toggleSidebar()">×</span>
        </div>
        
        <div class="user-info">
            <div style="font-weight:bold; margin-bottom:5px;">{{ current_user.username }}</div>
            <span class="plan-badge">{{ current_user.plan }}</span>
            <div class="credits-count" id="creditDisplay">الرصيد: {{ current_user.credits }}</div>
        </div>
        
        <div class="memory-list" id="memList"></div>
        <a href="/logout" class="logout-btn">تسجيل الخروج</a>
    </div>

    <div class="main">
        <h1 style="color:var(--gold); margin-top:10px;">STRATEGIC-AI-CORE</h1>
        
        <div class="control-panel">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="أدخل الرابط أو الأمر الاستراتيجي...">
                <select id="langSelect">
                    <option value="Arabic">العربية</option>
                    <option value="English">English</option>
                    <option value="Russian">Russian</option>
                    <option value="French">French</option>
                    <option value="Chinese">Chinese</option>
                </select>
            </div>
            <div class="actions">
                <button class="action-btn btn-run" onclick="executeCore()">تحليل (1 رصيد)</button>
                <button class="action-btn btn-pdf" onclick="window.print()">تصدير PDF</button>
                <button class="action-btn btn-clear" onclick="newSession()">جلسة جديدة</button>
            </div>
        </div>

        <div id="resultsArea" class="report-container"></div>
    </div>

    <script>
        let memory = JSON.parse(localStorage.getItem('imperial_mem_saas_{{ current_user.id }}') || '[]');

        function toggleSidebar() { document.getElementById('mySidebar').classList.toggle('collapsed'); }

        function saveToCloud(title, content) {
            const id = Date.now();
            memory.unshift({ id, title, content, date: new Date().toLocaleTimeString() });
            localStorage.setItem('imperial_mem_saas_{{ current_user.id }}', JSON.stringify(memory));
            renderSidebar();
        }

        function renderSidebar() {
            const list = document.getElementById('memList');
            list.innerHTML = memory.map(item => `
                <div class="mem-item" onclick="loadFromCloud(${item.id})">
                    <button class="del-btn" onclick="deleteItem(${item.id}, event)">×</button>
                    <div class="mem-title">${item.title}</div>
                    <div class="mem-date">${item.date}</div>
                </div>
            `).join('');
        }

        function deleteItem(id, event) {
            event.stopPropagation();
            if(!confirm("حذف؟")) return;
            memory = memory.filter(m => m.id !== id);
            localStorage.setItem('imperial_mem_saas_{{ current_user.id }}', JSON.stringify(memory));
            renderSidebar();
        }

        function loadFromCloud(id) {
            const item = memory.find(m => m.id === id);
            if(item) { renderResults(item.content); if(window.innerWidth < 600) toggleSidebar(); }
        }

        function newSession() {
            document.getElementById('resultsArea').innerHTML = "";
            document.getElementById('userInput').value = "";
        }

        async function executeCore() {
            const val = document.getElementById('userInput').value;
            const lang = document.getElementById('langSelect').value;
            if(!val) return;

            const area = document.getElementById('resultsArea');
            area.innerHTML = `<div style="text-align:center; color:var(--gold);">جاري التحليل وخصم الرصيد...</div>`;

            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: val, lang: lang })
                });
                const d = await r.json();
                
                if(d.error) {
                    area.innerHTML = `<div style="color:red; text-align:center;">${d.error}</div>`;
                    return;
                }

                // تحديث الرصيد في الواجهة
                if(d.credits_left !== undefined) {
                    document.getElementById('creditDisplay').innerText = "الرصيد: " + d.credits_left;
                }

                renderResults(d.res);
                saveToCloud(val.substring(0, 25), d.res);
            } catch {
                area.innerHTML = "خطأ في الاتصال.";
            }
        }

        function renderResults(text) {
            const area = document.getElementById('resultsArea');
            const segments = text.split(/(?=\\d\\.)/);
            area.innerHTML = segments.map(seg => `
                <div class="output-card">
                    <div class="card-tools"><button class="copy-btn" onclick="copyText(this)">نسخ</button></div>
                    <div class="report-text">${seg.trim()}</div>
                </div>
            `).join('');
        }

        function copyText(btn) {
            const txt = btn.parentElement.nextElementSibling.innerText;
            navigator.clipboard.writeText(txt).then(() => { btn.innerText = "تم"; setTimeout(() => btn.innerText = "نسخ", 1000); });
        }

        renderSidebar();
    </script>
</body>
</html>
"""

# --- Routes ---

@app.route('/')
@login_required
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('بيانات الدخول غير صحيحة')
    return render_template_string(LOGIN_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('المستخدم موجود بالفعل')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='scrypt'), plan='Free', credits=5)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template_string(REGISTER_HTML)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    # 1. Check Credits
    if current_user.credits <= 0:
        return jsonify({"error": "عذراً، نفد رصيدك. يرجى الترقية."})

    data = request.json
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    
    # 2. The Core Logic
    sys_prompt = f"""
    You are an Elite Strategy Analyst.
    Output Language: {data.get('lang')} ONLY.
    Analyze the input (URL/Text) to extract:
    1. Financial & Technical Valuation.
    2. Cyber-Due Diligence & Risks.
    3. Game Theory & Scenarios.
    Format: Use numbered lists (1. , 2. ) with professional language.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": data.get('prompt')}
        ]
    }
    
    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=60)
        res_text = r.json()['choices'][0]['message']['content']
        
        # 3. Deduct Credit on Success
        current_user.credits -= 1
        db.session.commit()
        
        return jsonify({"res": res_text, "credits_left": current_user.credits})
    except:
        return jsonify({"res": "Core Busy or Error."})

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create DB on first run
    app.run(debug=True)

#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║     🌐 SUMIT X MODS — WEBSITE TRAFFIC BOT v2.1 🌐           ║
║     🔥 FAST FIX — WEB MODE WORKING                          ║
║     ✅ RENDER + TERMUX + LOCALHOST                         ║
╚═══════════════════════════════════════════════════════════════╝
"""

import requests
import random
import time
import json
import threading
import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from concurrent.futures import ThreadPoolExecutor

# ════════════════════════════════════════════════════════════════
# 🔥 CONFIG
# ════════════════════════════════════════════════════════════════
TARGET_URL = "https://your-website.com"
TOTAL_VISITS = 10000
CONCURRENT_THREADS = 50
USE_PROXY = False

# ════════════════════════════════════════════════════════════════
# 🌐 USER AGENTS
# ════════════════════════════════════════════════════════════════
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]

REFERRERS = [
    "https://www.google.com/search?q={query}",
    "https://www.bing.com/search?q={query}",
    "https://in.search.yahoo.com/search?p={query}",
    "https://www.facebook.com/sharer/sharer.php?u={url}",
    "https://twitter.com/intent/tweet?url={url}",
]

# ════════════════════════════════════════════════════════════════
# 📊 BOT CLASS
# ════════════════════════════════════════════════════════════════
class TrafficBot:
    def __init__(self):
        self.target_url = TARGET_URL
        self.total_visits = TOTAL_VISITS
        self.visits_done = 0
        self.successful = 0
        self.failed = 0
        self.active = False
        self.start_time = None
        self.end_time = None
        self.results = []
        self.lock = threading.Lock()
        self.db_file = "traffic_data.json"
        self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.visits_done = data.get("visits_done", 0)
                    self.successful = data.get("successful", 0)
                    self.failed = data.get("failed", 0)
        except:
            pass
    
    def save_data(self):
        with self.lock:
            data = {
                "target_url": self.target_url,
                "visits_done": self.visits_done,
                "successful": self.successful,
                "failed": self.failed,
                "total_visits": self.total_visits,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_headers(self):
        ua = random.choice(USER_AGENTS)
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "Referer": random.choice(REFERRERS).replace("{query}", "best+website").replace("{url}", self.target_url),
        }
    
    def visit(self, visit_id):
        headers = self.get_headers()
        time.sleep(random.uniform(1, 4))
        
        try:
            resp = requests.get(self.target_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                with self.lock:
                    self.successful += 1
                    self.visits_done += 1
                return {"status": "success", "id": visit_id}
            else:
                with self.lock:
                    self.failed += 1
                    self.visits_done += 1
                return {"status": "failed", "code": resp.status_code, "id": visit_id}
        except:
            with self.lock:
                self.failed += 1
                self.visits_done += 1
            return {"status": "error", "id": visit_id}
    
    def start(self):
        if self.active:
            return {"status": "already_running"}
        
        self.active = True
        self.start_time = datetime.now().isoformat()
        self.successful = 0
        self.failed = 0
        self.visits_done = 0
        self.results = []
        
        print(f"\n🚀 Starting Traffic Bot...")
        print(f"   Target: {self.target_url}")
        print(f"   Visits: {self.total_visits}")
        print(f"   Threads: {CONCURRENT_THREADS}\n")
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            futures = [executor.submit(self.visit, i) for i in range(self.total_visits)]
            for future in futures:
                result = future.result()
                self.results.append(result)
                if self.visits_done % 10 == 0:
                    print(f"   📊 {self.visits_done}/{self.total_visits} | ✅ {self.successful} | ❌ {self.failed}")
                    self.save_data()
        
        self.active = False
        self.end_time = datetime.now().isoformat()
        self.save_data()
        
        print(f"\n✅ Bot Complete! | ✅ {self.successful} | ❌ {self.failed}")
        return {"status": "completed", "success": self.successful, "failed": self.failed}

# ════════════════════════════════════════════════════════════════
# 🌐 FLASK APP
# ════════════════════════════════════════════════════════════════
app = Flask(__name__)
bot = TrafficBot()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Traffic Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #fff; font-family: system-ui; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1a1a1a; }
        .header h1 { font-size: 2.5rem; background: linear-gradient(135deg, #ff6b6b, #e60023); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .card { background: #121212; border-radius: 16px; padding: 24px; margin-top: 20px; border: 1px solid #1a1a1a; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 15px 0; }
        .stat { background: #1a1a1a; border-radius: 12px; padding: 16px; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: 700; }
        .stat-label { color: #666; font-size: 0.75rem; }
        .stat.success .stat-number { color: #4caf50; }
        .stat.failed .stat-number { color: #f44336; }
        .stat.active .stat-number { color: #ff9800; }
        .stat.total .stat-number { color: #2196f3; }
        .progress-bar { width: 100%; height: 8px; background: #1a1a1a; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #ff6b6b, #e60023); width: 0%; transition: width 0.5s; }
        .input-group { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
        .input-group input { flex: 1; min-width: 150px; padding: 12px 16px; border-radius: 12px; border: 1px solid #2a2a2a; background: #1a1a1a; color: #fff; }
        .btn { padding: 12px 24px; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; font-size: 1rem; }
        .btn-start { background: #e60023; color: #fff; }
        .btn-stop { background: #f44336; color: #fff; }
        .btn-reset { background: #444; color: #fff; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .badge.active { background: #ff9800; color: #000; }
        .badge.inactive { background: #444; color: #fff; }
        .log { background: #0a0a0a; border-radius: 12px; padding: 16px; max-height: 150px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; color: #888; margin-top: 15px; border: 1px solid #1a1a1a; }
        @media (max-width: 600px) { .stats { grid-template-columns: repeat(2, 1fr); } .header h1 { font-size: 1.8rem; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header"><h1>🌐 TRAFFIC BOT</h1><p style="color:#666;">SUMIT X MODS · Real Traffic Generator</p></div>
    
    <div class="card">
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#888;">📊 Live Stats</span>
            <span id="statusBadge" class="badge inactive">Inactive</span>
        </div>
        <div class="stats">
            <div class="stat total"><div class="stat-number" id="total">0</div><div class="stat-label">Total</div></div>
            <div class="stat success"><div class="stat-number" id="success">0</div><div class="stat-label">✅ Success</div></div>
            <div class="stat failed"><div class="stat-number" id="failed">0</div><div class="stat-label">❌ Failed</div></div>
            <div class="stat active"><div class="stat-number" id="progress">0%</div><div class="stat-label">Progress</div></div>
        </div>
        <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
        <div style="font-size:0.8rem;color:#666;margin-top:5px;"><span id="timeInfo">Ready</span></div>
    </div>
    
    <div class="card">
        <div class="input-group">
            <input type="url" id="urlInput" placeholder="https://your-website.com" value="{{ TARGET_URL }}">
            <input type="number" id="visitsInput" placeholder="Visits" value="1000" min="10" style="max-width:120px;">
            <button class="btn btn-start" onclick="startBot()">🚀 Start</button>
            <button class="btn btn-stop" onclick="stopBot()">⏹ Stop</button>
            <button class="btn btn-reset" onclick="resetData()">🔄 Reset</button>
        </div>
    </div>
    
    <div class="card">
        <div style="color:#888;">📜 Log</div>
        <div class="log" id="log"><div>▶️ Ready. Click Start.</div></div>
    </div>
</div>

<script>
let interval = setInterval(update, 2000);
function update() {
    fetch('/api/status').then(r=>r.json()).then(d=>{
        document.getElementById('total').textContent = d.visits_done;
        document.getElementById('success').textContent = d.successful;
        document.getElementById('failed').textContent = d.failed;
        let p = d.progress || 0;
        document.getElementById('progress').textContent = p + '%';
        document.getElementById('progressFill').style.width = p + '%';
        let badge = document.getElementById('statusBadge');
        if (d.active) { badge.textContent = 'RUNNING'; badge.className = 'badge active'; }
        else { badge.textContent = 'Inactive'; badge.className = 'badge inactive'; }
        if (d.start_time) document.getElementById('timeInfo').textContent = 'Started: ' + new Date(d.start_time).toLocaleTimeString();
    });
}
function addLog(msg) {
    let log = document.getElementById('log');
    let div = document.createElement('div');
    div.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}
function startBot() {
    let url = document.getElementById('urlInput').value;
    let visits = document.getElementById('visitsInput').value || 1000;
    fetch('/api/start', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,visits:parseInt(visits)})})
    .then(r=>r.json()).then(d=>{ addLog('🚀 Started: ' + url); update(); });
}
function stopBot() {
    fetch('/api/stop',{method:'POST'}).then(()=>{ addLog('⏹ Stopped'); update(); });
}
function resetData() {
    if(confirm('Reset all data?')) {
        fetch('/api/reset',{method:'POST'}).then(()=>{ addLog('🔄 Reset'); update(); });
    }
}
update();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, TARGET_URL=bot.target_url)

@app.route('/api/status')
def status():
    return jsonify({
        "target_url": bot.target_url,
        "visits_done": bot.visits_done,
        "total_visits": bot.total_visits,
        "successful": bot.successful,
        "failed": bot.failed,
        "active": bot.active,
        "start_time": bot.start_time,
        "end_time": bot.end_time,
        "progress": round((bot.visits_done / bot.total_visits) * 100, 2) if bot.total_visits > 0 else 0
    })

@app.route('/api/start', methods=['POST'])
def start():
    data = request.get_json()
    if data:
        if 'url' in data:
            bot.target_url = data['url']
        if 'visits' in data:
            bot.total_visits = int(data['visits'])
    threading.Thread(target=bot.start).start()
    return jsonify({"status": "started"})

@app.route('/api/stop', methods=['POST'])
def stop():
    bot.active = False
    return jsonify({"status": "stopped"})

@app.route('/api/reset', methods=['POST'])
def reset():
    bot.visits_done = 0
    bot.successful = 0
    bot.failed = 0
    bot.results = []
    bot.save_data()
    return jsonify({"status": "reset"})

# ════════════════════════════════════════════════════════════════
# 🚀 MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
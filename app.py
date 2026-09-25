#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 HEADSHOT PROXY PANEL - RENDER READY
Offset: 0x7016044 → get_HeadCollider() → True
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, Response, render_template_string

# ==================== APP ====================
app = Flask(__name__)

# ==================== CONFIG ====================
CONFIG = {
    "headshot": False,
    "offset": "0x7016044",
    "method": "get_HeadCollider",
    "return": True
}

# Game client URL (tune diya tha)
GAME_CLIENT_URL = "https://100067.connect.garena.com"

LOGS_FILE = "headshot_logs.txt"
logs = []

# ==================== PANEL HTML ====================
PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Headshot Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #111;
            border: 2px solid #ff0000;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            box-shadow: 0 0 50px rgba(255, 0, 0, 0.3);
        }
        h1 {
            color: #ff0000;
            margin-bottom: 10px;
            font-size: 28px;
            text-shadow: 0 0 20px #ff0000;
        }
        .subtitle {
            color: #888;
            font-size: 12px;
            margin-bottom: 30px;
        }
        .status {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
            border: 1px solid #333;
        }
        .status-label {
            color: #888;
            font-size: 12px;
            margin-bottom: 5px;
        }
        .status-value {
            font-size: 24px;
            font-weight: bold;
            color: #ff0000;
            text-shadow: 0 0 10px #ff0000;
        }
        .status-value.on {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        .btn {
            width: 100%;
            padding: 20px;
            font-size: 20px;
            font-weight: bold;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 15px;
            font-family: inherit;
        }
        .btn-on {
            background: linear-gradient(135deg, #ff0000, #cc0000);
            color: #fff;
            box-shadow: 0 5px 20px rgba(255, 0, 0, 0.4);
        }
        .btn-on:hover { transform: scale(1.02); }
        .btn-on.active {
            background: linear-gradient(135deg, #00ff00, #00cc00);
            box-shadow: 0 5px 20px rgba(0, 255, 0, 0.4);
        }
        .info {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            font-size: 12px;
            color: #888;
            text-align: left;
            margin-top: 20px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #222;
        }
        .info-row:last-child { border-bottom: none; }
        .info-key { color: #888; }
        .info-value { color: #00ff00; font-family: monospace; }
        .log-box {
            background: #000;
            padding: 10px;
            border-radius: 8px;
            margin-top: 15px;
            max-height: 150px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 11px;
            text-align: left;
            color: #00ff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 HEADSHOT PANEL</h1>
        <div class="subtitle">Offset: 0x7016044 → get_HeadCollider()</div>
        
        <div class="status">
            <div class="status-label">STATUS</div>
            <div class="status-value" id="statusText">OFF</div>
        </div>
        
        <button class="btn btn-on" id="toggleBtn" onclick="toggleHeadshot()">
            🔴 ENABLE HEADSHOT
        </button>
        
        <div class="info">
            <div class="info-row">
                <span class="info-key">Offset:</span>
                <span class="info-value">0x7016044</span>
            </div>
            <div class="info-row">
                <span class="info-key">Method:</span>
                <span class="info-value">get_HeadCollider</span>
            </div>
            <div class="info-row">
                <span class="info-key">Return:</span>
                <span class="info-value">True</span>
            </div>
            <div class="info-row">
                <span class="info-key">Endpoint:</span>
                <span class="info-value">/Request12ver.php</span>
            </div>
            <div class="info-row">
                <span class="info-key">Game Client:</span>
                <span class="info-value">connect.garena.com</span>
            </div>
        </div>
        
        <div class="log-box" id="logBox">Waiting...</div>
    </div>
    
    <script>
        let isOn = false;
        
        async function toggleHeadshot() {
            try {
                const res = await fetch('/toggle', { method: 'POST' });
                const data = await res.json();
                isOn = data.headshot;
                updateUI();
                addLog(isOn ? '✅ Headshot ENABLED' : '❌ Headshot DISABLED');
            } catch(e) {
                addLog('Error: ' + e.message);
            }
        }
        
        function updateUI() {
            const statusText = document.getElementById('statusText');
            const btn = document.getElementById('toggleBtn');
            if (isOn) {
                statusText.textContent = 'ON';
                statusText.className = 'status-value on';
                btn.textContent = '🟢 HEADSHOT ENABLED';
                btn.classList.add('active');
            } else {
                statusText.textContent = 'OFF';
                statusText.className = 'status-value';
                btn.textContent = '🔴 ENABLE HEADSHOT';
                btn.classList.remove('active');
            }
        }
        
        function addLog(msg) {
            const box = document.getElementById('logBox');
            const time = new Date().toLocaleTimeString();
            box.innerHTML = `[${time}] ${msg}\\n` + box.innerHTML;
        }
        
        async function checkStatus() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                isOn = data.headshot;
                updateUI();
            } catch(e) {}
        }
        
        checkStatus();
        setInterval(checkStatus, 2000);
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "panel": "/panel",
        "endpoints": {
            "toggle": "/toggle",
            "status": "/status",
            "logs": "/logs",
            "request": "/Request12ver.php"
        }
    })

@app.route('/panel')
def panel():
    return render_template_string(PANEL_HTML)

@app.route('/status')
def status():
    return jsonify(CONFIG)

@app.route('/logs')
def get_logs():
    return jsonify({"logs": logs[-50:]})

@app.route('/toggle', methods=['POST'])
def toggle():
    CONFIG["headshot"] = not CONFIG["headshot"]
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "TOGGLE",
        "headshot": CONFIG["headshot"]
    }
    logs.append(log_entry)
    save_log(log_entry)
    return jsonify(CONFIG)

# ==================== GAME ENDPOINT ====================
@app.route('/Request12ver.php', methods=['GET', 'POST'])
def request12ver():
    """
    Game yahan request bhejega.
    Response WAPAS GAME KO jayega (jahan se request aayi).
    """
    
    # Request data capture
    req_data = None
    try:
        if request.is_json:
            req_data = request.get_json()
        elif request.data:
            req_data = json.loads(request.data.decode('utf-8', errors='ignore'))
    except:
        req_data = {}
    
    # Log request
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "data": req_data
    }
    logs.append(log_entry)
    save_log(log_entry)
    
    # ===== RESPONSE WAPAS GAME KO =====
    # Flask automatically usi client ko bhejta hai jisne request bheji
    response_data = {
        "code": 200,
        "status": "success",
        "data": {
            "offset": CONFIG["offset"],
            "method": CONFIG["method"],
            "return": CONFIG["return"] if CONFIG["headshot"] else False,
            "headshot": CONFIG["headshot"],
            "features": {
                "get_HeadCollider": CONFIG["headshot"],
                "headshot_enabled": CONFIG["headshot"]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\\n{'='*60}")
    print(f"🎯 GAME REQUEST")
    print(f"{'='*60}")
    print(f"IP: {log_entry['ip']}")
    print(f"Method: {log_entry['method']}")
    print(f"Path: {log_entry['path']}")
    print(f"UA: {log_entry['user_agent'][:80]}")
    print(f"Data: {json.dumps(req_data, indent=2)[:300]}")
    print(f"Headshot: {'ON ✅' if CONFIG['headshot'] else 'OFF ❌'}")
    print(f"Response → back to {log_entry['ip']}")
    print(f"{'='*60}\\n")
    
    # Same IP:port pe response jayega jahan se request aayi
    return jsonify(response_data), 200

# ==================== CATCH-ALL ====================
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """Agar koi aur endpoint hit kare toh log karo"""
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "method": request.method,
        "path": f"/{path}",
        "user_agent": request.headers.get('User-Agent', 'Unknown')
    }
    logs.append(log_entry)
    save_log(log_entry)
    
    return jsonify({
        "status": "logged",
        "path": path,
        "headshot": CONFIG["headshot"]
    })

# ==================== HELPER ====================
def save_log(entry):
    try:
        with open(LOGS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")
    except:
        pass

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🎯 Panel: /panel")
    print(f"📡 Game Endpoint: /Request12ver.php")
    app.run(host='0.0.0.0', port=port, debug=False)
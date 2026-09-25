#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 PROXY PANEL - Game ↔ Original Server
Headshot Inject karta hai
"""

import os
import json
import time
import requests
from datetime import datetime
from flask import Flask, request, jsonify, Response, render_template_string

app = Flask(__name__)

# ==================== CONFIG ====================
# ⭐ ORIGINAL SERVER URL YAHAN DAALO (game ka actual server)
ORIGINAL_SERVER = "https://100067.connect.garena.com"  # ← Yahan game ka server URL daalo

CONFIG = {
    "headshot": False,
    "offset": "0x7016044",
    "method": "get_HeadCollider",
    "return": True
}

LOGS_FILE = "proxy_logs.txt"
logs = []

# ==================== PANEL HTML ====================
PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Proxy Headshot Panel</title>
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
        h1 { color: #ff0000; margin-bottom: 10px; font-size: 28px; text-shadow: 0 0 20px #ff0000; }
        .subtitle { color: #888; font-size: 12px; margin-bottom: 30px; }
        .status { background: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #333; }
        .status-label { color: #888; font-size: 12px; margin-bottom: 5px; }
        .status-value { font-size: 24px; font-weight: bold; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
        .status-value.on { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
        .btn {
            width: 100%; padding: 20px; font-size: 20px; font-weight: bold;
            border: none; border-radius: 12px; cursor: pointer; transition: all 0.3s;
            margin-bottom: 15px; font-family: inherit;
        }
        .btn-on { background: linear-gradient(135deg, #ff0000, #cc0000); color: #fff; }
        .btn-on.active { background: linear-gradient(135deg, #00ff00, #00cc00); }
        .info { background: #1a1a1a; padding: 15px; border-radius: 10px; font-size: 12px; text-align: left; margin-top: 20px; }
        .info-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #222; }
        .info-key { color: #888; }
        .info-value { color: #00ff00; font-family: monospace; }
        .log-box {
            background: #000; padding: 10px; border-radius: 8px; margin-top: 15px;
            max-height: 150px; overflow-y: auto; font-family: monospace; font-size: 11px;
            text-align: left; color: #00ff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 PROXY HEADSHOT</h1>
        <div class="subtitle">Offset: 0x7016044 → get_HeadCollider()</div>
        
        <div class="status">
            <div class="status-label">STATUS</div>
            <div class="status-value" id="statusText">OFF</div>
        </div>
        
        <button class="btn btn-on" id="toggleBtn" onclick="toggleHeadshot()">🔴 ENABLE HEADSHOT</button>
        
        <div class="info">
            <div class="info-row"><span class="info-key">Offset:</span><span class="info-value">0x7016044</span></div>
            <div class="info-row"><span class="info-key">Method:</span><span class="info-value">get_HeadCollider</span></div>
            <div class="info-row"><span class="info-key">Original:</span><span class="info-value" id="origServer">-</span></div>
        </div>
        
        <div class="log-box" id="logBox">Waiting...</div>
    </div>
    
    <script>
        let isOn = false;
        async function toggleHeadshot() {
            const res = await fetch('/toggle', { method: 'POST' });
            const data = await res.json();
            isOn = data.headshot;
            updateUI();
        }
        function updateUI() {
            const s = document.getElementById('statusText');
            const b = document.getElementById('toggleBtn');
            if (isOn) {
                s.textContent = 'ON'; s.className = 'status-value on';
                b.textContent = '🟢 HEADSHOT ENABLED'; b.classList.add('active');
            } else {
                s.textContent = 'OFF'; s.className = 'status-value';
                b.textContent = '🔴 ENABLE HEADSHOT'; b.classList.remove('active');
            }
        }
        async function checkStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            isOn = data.headshot;
            document.getElementById('origServer').textContent = data.original_server || '-';
            updateUI();
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
        "proxy": "/Request12ver.php",
        "original_server": ORIGINAL_SERVER
    })

@app.route('/panel')
def panel():
    return render_template_string(PANEL_HTML)

@app.route('/status')
def status():
    return jsonify({
        **CONFIG,
        "original_server": ORIGINAL_SERVER
    })

@app.route('/toggle', methods=['POST'])
def toggle():
    CONFIG["headshot"] = not CONFIG["headshot"]
    log_entry = {"time": datetime.now().strftime("%H:%M:%S"), "action": "TOGGLE", "headshot": CONFIG["headshot"]}
    logs.append(log_entry)
    save_log(log_entry)
    return jsonify(CONFIG)

# ==================== PROXY ENDPOINT ====================
@app.route('/Request12ver.php', methods=['GET', 'POST'])
def proxy():
    """
    PROXY: Game → Hamara Server → Original Server
    Response modify karke wapas game ko bhejo
    """
    
    # 1. Game ki request capture
    req_data = None
    try:
        if request.is_json:
            req_data = request.get_json()
        elif request.data:
            req_data = request.data.decode('utf-8', errors='ignore')
    except:
        req_data = None
    
    # 2. Log request
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
    
    print(f"\n{'='*60}")
    print(f"📥 GAME REQUEST RECEIVED")
    print(f"{'='*60}")
    print(f"IP: {request.remote_addr}")
    print(f"Method: {request.method}")
    print(f"UA: {request.headers.get('User-Agent', '')[:80]}")
    print(f"Data: {str(req_data)[:300]}")
    print(f"{'='*60}\n")
    
    # 3. Original server pe forward karo
    original_response = None
    try:
        # Headers copy karo (except Host)
        forward_headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'content-length']:
                forward_headers[key] = value
        
        # Original server URL banao
        original_url = ORIGINAL_SERVER.rstrip('/') + request.path
        if request.query_string:
            original_url += "?" + request.query_string.decode()
        
        print(f"🔄 Forwarding to: {original_url}")
        
        # Request forward karo
        if request.method == 'POST':
            orig_resp = requests.post(
                original_url,
                headers=forward_headers,
                data=request.data,
                timeout=15,
                verify=False
            )
        else:
            orig_resp = requests.get(
                original_url,
                headers=forward_headers,
                params=request.args,
                timeout=15,
                verify=False
            )
        
        original_response = orig_resp.content
        print(f"✅ Original server response: {orig_resp.status_code}")
        
    except Exception as e:
        print(f"❌ Forward error: {e}")
        original_response = None
    
    # 4. Response modify karo
    if original_response:
        try:
            # JSON parse karo
            resp_json = json.loads(original_response)
            
            # Headshot inject karo
            if CONFIG["headshot"]:
                resp_json["headshot"] = True
                resp_json["offset"] = CONFIG["offset"]
                resp_json["method"] = CONFIG["method"]
                resp_json["return"] = True
                
                # Agar nested data hai
                if "data" in resp_json:
                    resp_json["data"]["headshot"] = True
                    resp_json["data"]["get_HeadCollider"] = True
            
            return jsonify(resp_json), 200
            
        except:
            # Agar JSON nahi hai, toh raw bhejo
            return Response(original_response, status=200, content_type='application/json')
    
    # 5. Agar original server se response nahi aaya, toh apna response bhejo
    response_data = {
        "code": 200,
        "status": "success",
        "data": {
            "offset": CONFIG["offset"],
            "method": CONFIG["method"],
            "return": CONFIG["headshot"],
            "headshot": CONFIG["headshot"]
        }
    }
    return jsonify(response_data), 200

# ==================== CATCH-ALL ====================
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """Aur endpoints bhi proxy karo"""
    try:
        forward_headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'content-length']:
                forward_headers[key] = value
        
        original_url = ORIGINAL_SERVER.rstrip('/') + '/' + path
        if request.query_string:
            original_url += "?" + request.query_string.decode()
        
        if request.method == 'POST':
            resp = requests.post(original_url, headers=forward_headers, data=request.data, timeout=15, verify=False)
        else:
            resp = requests.get(original_url, headers=forward_headers, params=request.args, timeout=15, verify=False)
        
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 502

# ==================== HELPER ====================
def save_log(entry):
    try:
        with open(LOGS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except:
        pass

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Proxy server starting on port {port}")
    print(f"🎯 Original Server: {ORIGINAL_SERVER}")
    print(f"📡 Panel: /panel")
    app.run(host='0.0.0.0', port=port, debug=False)
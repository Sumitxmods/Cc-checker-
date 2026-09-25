#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 REQUEST LOGGER SERVER
Endpoints:
  GET  /terminalLOGEabbb  → Live terminal logs (web view)
  POST /Request12         → Game JSON yahan bhejega
  GET  /download_logs     → Logs download
  GET  /api/logs          → JSON logs API
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, Response, render_template_string

# ==================== CONFIG ====================
app = Flask(__name__)
LOG_FILE = "requests.log"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# In-memory log store
logs = []

# ==================== HTML TERMINAL UI ====================
TERMINAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Terminal Logs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            padding: 15px;
            min-height: 100vh;
        }
        .header {
            background: #111;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid #00ff00;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 {
            font-size: 18px;
            text-shadow: 0 0 10px #00ff00;
        }
        .controls { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-family: inherit;
            font-weight: bold;
            font-size: 12px;
            text-decoration: none;
        }
        .btn:hover { background: #00cc00; }
        .btn.danger { background: #ff0000; color: #fff; }
        .btn.danger:hover { background: #cc0000; }

        .terminal {
            background: #000;
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            min-height: 70vh;
            max-height: 80vh;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.6;
        }
        .terminal::-webkit-scrollbar { width: 8px; }
        .terminal::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }

        .log-entry {
            padding: 8px 0;
            border-bottom: 1px solid #1a1a1a;
        }
        .log-time { color: #888; }
        .log-ip { color: #ffff00; }
        .log-method { color: #00ffff; font-weight: bold; }
        .log-path { color: #ff00ff; }
        .log-status { color: #00ff00; }
        .log-status.error { color: #ff0000; }
        .log-data {
            background: #111;
            padding: 8px;
            margin-top: 5px;
            border-radius: 4px;
            color: #00ff00;
            font-size: 12px;
            word-break: break-all;
            white-space: pre-wrap;
        }
        .log-headers {
            color: #888;
            font-size: 11px;
            margin-top: 3px;
        }

        .empty {
            text-align: center;
            color: #444;
            padding: 50px;
        }

        .stats {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .stat-box {
            background: #111;
            border: 1px solid #00ff00;
            padding: 10px 15px;
            border-radius: 5px;
            flex: 1;
            min-width: 100px;
            text-align: center;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #00ff00;
        }
        .stat-label {
            font-size: 10px;
            color: #888;
            margin-top: 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 TERMINAL LOGS</h1>
        <div class="controls">
            <button class="btn" onclick="refreshLogs()">🔄 Refresh</button>
            <button class="btn" onclick="autoRefresh()" id="autoBtn">▶️ Auto</button>
            <a href="/download_logs" class="btn">📥 Download</a>
            <button class="btn danger" onclick="clearLogs()">🗑️ Clear</button>
        </div>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="stat-value" id="totalCount">0</div>
            <div class="stat-label">TOTAL REQUESTS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="request12Count">0</div>
            <div class="stat-label">/Request12</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" id="uniqueIps">0</div>
            <div class="stat-label">UNIQUE IPs</div>
        </div>
    </div>

    <div class="terminal" id="terminal">
        <div class="empty">Waiting for requests...</div>
    </div>

    <script>
        let autoRefreshInterval = null;

        async function refreshLogs() {
            try {
                const res = await fetch('/api/logs');
                const data = await res.json();
                renderLogs(data.logs);
                updateStats(data.logs);
            } catch(e) {
                console.error('Error:', e);
            }
        }

        function renderLogs(logs) {
            const terminal = document.getElementById('terminal');
            if (!logs || logs.length === 0) {
                terminal.innerHTML = '<div class="empty">Waiting for requests...</div>';
                return;
            }

            let html = '';
            // Latest first
            for (let i = logs.length - 1; i >= 0; i--) {
                const log = logs[i];
                const statusClass = log.status >= 400 ? 'error' : '';
                
                html += `
                    <div class="log-entry">
                        <span class="log-time">[${log.time}]</span>
                        <span class="log-ip">${log.ip}</span>
                        <span class="log-method">${log.method}</span>
                        <span class="log-path">${log.path}</span>
                        <span class="log-status ${statusClass}">→ ${log.status}</span>
                        ${log.user_agent ? `<div class="log-headers">UA: ${log.user_agent}</div>` : ''}
                        ${log.data ? `<div class="log-data">${JSON.stringify(log.data, null, 2)}</div>` : ''}
                    </div>
                `;
            }
            terminal.innerHTML = html;
        }

        function updateStats(logs) {
            document.getElementById('totalCount').textContent = logs.length;
            document.getElementById('request12Count').textContent = 
                logs.filter(l => l.path === '/Request12').length;
            const uniqueIps = new Set(logs.map(l => l.ip));
            document.getElementById('uniqueIps').textContent = uniqueIps.size;
        }

        function autoRefresh() {
            const btn = document.getElementById('autoBtn');
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                btn.textContent = '▶️ Auto';
                btn.style.background = '#00ff00';
            } else {
                autoRefreshInterval = setInterval(refreshLogs, 2000);
                btn.textContent = '⏸️ Stop';
                btn.style.background = '#ffaa00';
            }
        }

        async function clearLogs() {
            if (!confirm('Clear all logs?')) return;
            await fetch('/clear_logs', { method: 'POST' });
            refreshLogs();
        }

        // Initial load
        refreshLogs();
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "terminal": "/terminalLOGEabbb",
            "request": "/Request12",
            "download": "/download_logs",
            "api": "/api/logs"
        }
    })

# ==================== TERMINAL VIEW ====================
@app.route('/terminalLOGEabbb')
def terminal():
    return render_template_string(TERMINAL_HTML)

# ==================== MAIN REQUEST ENDPOINT ====================
@app.route('/Request12', methods=['GET', 'POST', 'PUT', 'DELETE'])
def request12():
    """
    Game yahan JSON bhejega.
    Har request ko log karo aur store karo.
    """
    # Collect data
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "status": 200,
        "headers": dict(request.headers),
        "args": dict(request.args),
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "referer": request.headers.get('Referer', 'None'),
        "content_type": request.content_type,
        "data": None
    }
    
    # Parse body data
    try:
        if request.is_json:
            log_entry["data"] = request.get_json()
        elif request.form:
            log_entry["data"] = dict(request.form)
        elif request.data:
            raw = request.data.decode('utf-8', errors='ignore')
            try:
                log_entry["data"] = json.loads(raw)
            except:
                log_entry["data"] = raw[:1000]
    except Exception as e:
        log_entry["data"] = f"Parse error: {str(e)}"
    
    # Store log
    logs.append(log_entry)
    save_log_to_file(log_entry)
    
    # Print to console
    print(f"\n{'='*60}")
    print(f"🎯 REQUEST RECEIVED")
    print(f"{'='*60}")
    print(f"⏰ Time: {log_entry['time']}")
    print(f"🌐 IP: {log_entry['ip']}")
    print(f"📡 Method: {log_entry['method']}")
    print(f"🛤️  Path: {log_entry['path']}")
    print(f"📦 Data: {json.dumps(log_entry['data'], indent=2) if log_entry['data'] else 'None'}")
    print(f"🔍 User-Agent: {log_entry['user_agent'][:100]}")
    print(f"{'='*60}\n")
    
    # Response to game
    return jsonify({
        "status": "received",
        "message": "Request logged successfully",
        "request_id": len(logs),
        "timestamp": log_entry["time"]
    }), 200

# ==================== API: GET LOGS ====================
@app.route('/api/logs')
def api_logs():
    return jsonify({
        "count": len(logs),
        "logs": logs[-100:]  # Latest 100
    })

# ==================== DOWNLOAD LOGS ====================
@app.route('/download_logs')
def download_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "No logs yet"}), 404
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = f"requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    return Response(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

# ==================== CLEAR LOGS ====================
@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global logs
    logs = []
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return jsonify({"status": "cleared"})

# ==================== CATCH ALL (Log everything else) ====================
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """Agar koi aur endpoint hit kare toh bhi log karo"""
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "method": request.method,
        "path": f"/{path}",
        "status": 200,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "data": None
    }
    
    try:
        if request.is_json:
            log_entry["data"] = request.get_json()
        elif request.data:
            log_entry["data"] = request.data.decode('utf-8', errors='ignore')[:500]
    except:
        pass
    
    logs.append(log_entry)
    save_log_to_file(log_entry)
    
    return jsonify({"status": "logged", "path": path})

# ==================== HELPER ====================
def save_log_to_file(log_entry):
    """Log ko file mein save karo"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"File save error: {e}")

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🎯 Terminal: http://0.0.0.0:{port}/terminalLOGEabbb")
    print(f"📡 Request Endpoint: http://0.0.0.0:{port}/Request12")
    app.run(host='0.0.0.0', port=port, debug=False)
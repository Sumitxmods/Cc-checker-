#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Dumper - Dashboard
"""

import os
import json
from datetime import datetime
from flask import Flask, request, Response, jsonify, render_template_string

app = Flask(__name__)

# ==================== IN-MEMORY STORE ====================

STORE = {
    "https_requests": [],
    "https_responses": [],
    "tcp_sends": [],
    "tcp_recvs": [],
    "api_endpoints": [],
    "connections": [],
    "api_keys": [],
    "status": [],
    "raw_logs": [],
}

# ==================== HTML DASHBOARD ====================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Dumper</title>
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
        .header h1 { font-size: 18px; text-shadow: 0 0 10px #00ff00; }
        .header-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
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
            transition: 0.2s;
        }
        .btn:hover { background: #00cc00; transform: scale(1.05); }
        .btn-danger { background: #ff0000; color: #fff; }
        .btn-danger:hover { background: #cc0000; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        .stat {
            background: #111;
            border: 1px solid #00ff00;
            padding: 12px;
            border-radius: 5px;
            text-align: center;
            transition: 0.2s;
        }
        .stat:hover { border-color: #00ffff; transform: translateY(-2px); }
        .stat-value { font-size: 22px; font-weight: bold; }
        .stat-label { font-size: 10px; color: #888; margin-top: 3px; }
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .tab {
            background: #111;
            border: 1px solid #333;
            color: #888;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: 0.2s;
        }
        .tab:hover { background: #222; color: #fff; }
        .tab.active {
            background: #00ff00;
            color: #000;
            border-color: #00ff00;
        }
        .terminal {
            background: #000;
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            min-height: 60vh;
            max-height: 75vh;
            overflow-y: auto;
            font-size: 12px;
            line-height: 1.6;
        }
        .terminal::-webkit-scrollbar { width: 8px; }
        .terminal::-webkit-scrollbar-track { background: #111; }
        .terminal::-webkit-scrollbar-thumb { background: #00ff00; border-radius: 4px; }
        .log-line { padding: 5px 0; border-bottom: 1px solid #111; word-break: break-all; white-space: pre-wrap; }
        .log-request { color: #00ffff; }
        .log-response { color: #00ff88; }
        .log-tcp-send { color: #ffaa00; }
        .log-tcp-recv { color: #ffaa88; }
        .log-endpoint { color: #ffff00; }
        .log-connection { color: #ff00ff; }
        .log-key { color: #ff6666; font-weight: bold; }
        .log-status { color: #ffffff; font-weight: bold; }
        .empty { color: #444; text-align: center; padding: 30px; }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #00ff00;
            color: #000;
            padding: 12px 20px;
            border-radius: 5px;
            font-weight: bold;
            opacity: 0;
            transition: 0.3s;
            z-index: 9999;
        }
        .toast.show { opacity: 1; }
        @media (max-width: 600px) {
            .header { flex-direction: column; }
            .header-buttons { width: 100%; }
            .btn { flex: 1; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 NETWORK DUMPER</h1>
        <div class="header-buttons">
            <button class="btn" onclick="refresh()">🔄 Refresh</button>
            <button class="btn" onclick="toggleAuto()" id="autoBtn">▶ Auto</button>
            <a href="/download" class="btn">📥 Download</a>
            <button class="btn btn-danger" onclick="clearAll()">🗑️ CLEAR ALL</button>
        </div>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value" id="reqCount">0</div>
            <div class="stat-label">HTTPS REQ</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="resCount">0</div>
            <div class="stat-label">HTTPS RES</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="tcpCount">0</div>
            <div class="stat-label">TCP</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="endpointCount">0</div>
            <div class="stat-label">ENDPOINTS</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="connCount">0</div>
            <div class="stat-label">CONNECTIONS</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="keyCount">0</div>
            <div class="stat-label">API KEYS</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', event)">All</div>
        <div class="tab" onclick="switchTab('requests', event)">HTTPS Requests</div>
        <div class="tab" onclick="switchTab('responses', event)">HTTPS Responses</div>
        <div class="tab" onclick="switchTab('endpoints', event)">API Endpoints</div>
        <div class="tab" onclick="switchTab('connections', event)">Connections</div>
        <div class="tab" onclick="switchTab('keys', event)">API Keys</div>
    </div>

    <div class="terminal" id="terminal">
        <div class="empty">Waiting for network data...</div>
    </div>

    <div class="toast" id="toast">Done!</div>

    <script>
        let autoInterval = null;
        let currentTab = 'all';
        let lastData = null;

        async function refresh() {
            try {
                const r = await fetch('/api/data');
                const d = await r.json();
                lastData = d;
                render(d);
            } catch(e) {
                console.error(e);
            }
        }

        function switchTab(tab, ev) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            if (ev) ev.target.classList.add('active');
            if (lastData) render(lastData);
        }

        function render(d) {
            document.getElementById('reqCount').textContent = d.https_requests.length;
            document.getElementById('resCount').textContent = d.https_responses.length;
            document.getElementById('tcpCount').textContent = d.tcp_sends.length + d.tcp_recvs.length;
            document.getElementById('endpointCount').textContent = d.api_endpoints.length;
            document.getElementById('connCount').textContent = d.connections.length;
            document.getElementById('keyCount').textContent = d.api_keys.length;

            const term = document.getElementById('terminal');
            let html = '';

            function addLines(items, cls, prefix) {
                items.forEach(i => {
                    html += `<div class="log-line ${cls}">[${prefix}] ${i}</div>`;
                });
            }

            if (currentTab === 'all' || currentTab === 'status') {
                addLines(d.status, 'log-status', 'STATUS');
            }
            if (currentTab === 'all' || currentTab === 'requests') {
                addLines(d.https_requests, 'log-request', 'HTTPS-REQ');
            }
            if (currentTab === 'all' || currentTab === 'responses') {
                addLines(d.https_responses, 'log-response', 'HTTPS-RES');
            }
            if (currentTab === 'all' || currentTab === 'endpoints') {
                addLines(d.api_endpoints, 'log-endpoint', 'API');
            }
            if (currentTab === 'all' || currentTab === 'connections') {
                addLines(d.connections, 'log-connection', 'CONN');
            }
            if (currentTab === 'all' || currentTab === 'keys') {
                addLines(d.api_keys, 'log-key', 'KEY');
            }
            if (currentTab === 'all') {
                addLines(d.tcp_sends, 'log-tcp-send', 'TCP-SEND');
                addLines(d.tcp_recvs, 'log-tcp-recv', 'TCP-RECV');
            }

            if (html === '') html = '<div class="empty">Waiting for network data...</div>';
            term.innerHTML = html;
        }

        function toggleAuto() {
            const btn = document.getElementById('autoBtn');
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
                btn.textContent = '▶ Auto';
            } else {
                autoInterval = setInterval(refresh, 2000);
                btn.textContent = '⏸ Stop';
            }
        }

        async function clearAll() {
            if (!confirm('⚠️ Clear ALL network logs?')) return;
            try {
                const r = await fetch('/clear', { method: 'POST' });
                const d = await r.json();
                showToast('✅ ' + d.message);
                refresh();
            } catch(e) {
                showToast('❌ Failed');
            }
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2500);
        }

        refresh();
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "dashboard": "/terminal",
        "api": "/api/data",
        "download": "/download",
        "endpoints": {
            "datasend": "POST /datasend",
            "clear": "POST /clear",
        }
    })

@app.route("/terminal")
def terminal():
    return render_template_string(DASHBOARD_HTML)

@app.route("/datasend", methods=["POST", "GET"])
def datasend():
    try:
        raw = request.get_data(as_text=True)
        if not raw:
            return jsonify({"status": "empty"})

        if raw.startswith("[") and "]" in raw:
            tag_end = raw.index("]")
            tag = raw[1:tag_end]
            content = raw[tag_end + 1:].strip()
        else:
            tag = "RAW"
            content = raw.strip()

        # Route to buckets
        if tag == "HTTPS_REQUEST":
            STORE["https_requests"].append(content)
        elif tag == "HTTPS_RESPONSE":
            STORE["https_responses"].append(content)
        elif tag == "TCP_SEND":
            STORE["tcp_sends"].append(content)
        elif tag == "TCP_RECV":
            STORE["tcp_recvs"].append(content)
        elif tag == "API_ENDPOINT":
            STORE["api_endpoints"].append(content)
        elif tag == "CONNECTION":
            STORE["connections"].append(content)
        elif tag == "API_KEY":
            STORE["api_keys"].append(content)
        elif tag == "STATUS":
            STORE["status"].append(content)

        STORE["raw_logs"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "tag": tag,
            "content": content[:500],
        })

        print(f"[{tag}] {content[:300]}", flush=True)
        return jsonify({"status": "ok", "tag": tag})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/data")
def api_data():
    return jsonify(STORE)

@app.route("/download")
def download():
    filename = f"network_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        json.dumps(STORE, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

@app.route("/clear", methods=["POST"])
def clear():
    counts = {k: len(v) for k, v in STORE.items()}
    for k in STORE:
        STORE[k] = []
    msg = "Cleared: " + ", ".join(f"{k}={v}" for k, v in counts.items() if v > 0)
    print(f"[CLEAR] {msg}", flush=True)
    return jsonify({"status": "cleared", "message": msg})

# ==================== MAIN ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Network Dumper Dashboard on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
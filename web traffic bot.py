#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║   🌐 SUMIT X MODS — TRAFFIC BOT API v3.0                    ║
║   ✅ SCHEDULED CAMPAIGNS | GOAL TRACKING | JSON LOGS        ║
║   ✅ DYNAMIC IP | USER-AGENTS | LOCATIONS                   ║
╚═══════════════════════════════════════════════════════════════╝
"""

import requests
import random
import time
import json
import os
import threading
import uuid
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

# ============================================
# 🔥 CONFIG
# ============================================
app = Flask(__name__)
CORS(app)

DATA_FILE = "traffic_logs.json"
CONFIG_FILE = "campaign_config.json"

# ============================================
# 📊 DATABASE (JSON)
# ============================================
class TrafficDB:
    @staticmethod
    def load():
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"logs": [], "stats": {"total": 0, "success": 0, "failed": 0}}
    
    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def add_log(entry):
        data = TrafficDB.load()
        data["logs"].append(entry)
        data["stats"]["total"] += 1
        if entry.get("status") == "success":
            data["stats"]["success"] += 1
        else:
            data["stats"]["failed"] += 1
        # Keep last 10000 logs
        if len(data["logs"]) > 10000:
            data["logs"] = data["logs"][-10000:]
        TrafficDB.save(data)
        return data

# ============================================
# 🎯 CAMPAIGN MANAGER
# ============================================
class CampaignManager:
    @staticmethod
    def load_config():
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "active": False,
            "target_url": "",
            "total_goal": 10000,
            "start_date": None,
            "end_date": None,
            "visits_done": 0,
            "started_at": None
        }
    
    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def get_progress():
        config = CampaignManager.load_config()
        if not config["active"] or config["total_goal"] == 0:
            return 0
        return round((config["visits_done"] / config["total_goal"]) * 100, 2)
    
    @staticmethod
    def get_remaining_time():
        config = CampaignManager.load_config()
        if not config["active"] or not config["end_date"]:
            return None
        end = datetime.fromisoformat(config["end_date"])
        now = datetime.now()
        if now > end:
            return "Expired"
        diff = end - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

# ============================================
# 🧠 FAKE DATA GENERATOR
# ============================================
class FakeDataGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/126.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 Chrome/126.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
    ]
    
    LOCATIONS = [
        {"country": "US", "city": "New York", "state": "NY", "zip": "10001"},
        {"country": "US", "city": "Los Angeles", "state": "CA", "zip": "90001"},
        {"country": "US", "city": "Chicago", "state": "IL", "zip": "60601"},
        {"country": "US", "city": "Houston", "state": "TX", "zip": "77001"},
        {"country": "UK", "city": "London", "state": "England", "zip": "SW1A 1AA"},
        {"country": "CA", "city": "Toronto", "state": "ON", "zip": "M5V1J1"},
        {"country": "AU", "city": "Sydney", "state": "NSW", "zip": "2000"},
        {"country": "DE", "city": "Berlin", "state": "Berlin", "zip": "10115"},
        {"country": "FR", "city": "Paris", "state": "Île-de-France", "zip": "75001"},
        {"country": "JP", "city": "Tokyo", "state": "Tokyo", "zip": "100-0001"},
        {"country": "IN", "city": "Mumbai", "state": "MH", "zip": "400001"},
        {"country": "IN", "city": "Delhi", "state": "DL", "zip": "110001"},
        {"country": "BR", "city": "São Paulo", "state": "SP", "zip": "01000-000"},
    ]
    
    @staticmethod
    def get_ip():
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    @staticmethod
    def get_user_agent():
        return random.choice(FakeDataGenerator.USER_AGENTS)
    
    @staticmethod
    def get_location():
        return random.choice(FakeDataGenerator.LOCATIONS)
    
    @staticmethod
    def get_headers(target_url):
        location = FakeDataGenerator.get_location()
        return {
            "User-Agent": FakeDataGenerator.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-For": FakeDataGenerator.get_ip(),
            "Client-IP": FakeDataGenerator.get_ip(),
            "X-Real-IP": FakeDataGenerator.get_ip(),
            "X-Geo-Country": location["country"],
            "X-Geo-City": location["city"],
            "X-Geo-State": location["state"],
            "X-Geo-Zip": location["zip"],
            "Referer": random.choice([
                "https://www.google.com/search?q=",
                "https://www.bing.com/search?q=",
                "https://in.search.yahoo.com/search?p=",
                "https://www.facebook.com/",
                "https://twitter.com/",
                "https://www.instagram.com/",
                "https://www.youtube.com/",
                "https://www.reddit.com/",
            ]) + random.choice(["best+website", "top+website", "learn+online", "free+tools"]),
        }

# ============================================
# 🚀 TRAFFIC BOT ENGINE
# ============================================
class TrafficBot:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def visit(self, target_url, visit_id):
        """Simulate one visitor"""
        headers = FakeDataGenerator.get_headers(target_url)
        time.sleep(random.uniform(0.5, 3))
        
        try:
            resp = requests.get(target_url, headers=headers, timeout=10)
            success = resp.status_code == 200
            
            # Log entry
            entry = {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "url": target_url,
                "ip": headers["X-Forwarded-For"],
                "user_agent": headers["User-Agent"],
                "location": {
                    "country": headers.get("X-Geo-Country"),
                    "city": headers.get("X-Geo-City"),
                    "state": headers.get("X-Geo-State"),
                    "zip": headers.get("X-Geo-Zip")
                },
                "status": "success" if success else "failed",
                "status_code": resp.status_code,
                "headers": headers
            }
            
            TrafficDB.add_log(entry)
            
            # Update campaign progress
            config = CampaignManager.load_config()
            if config["active"]:
                config["visits_done"] += 1
                CampaignManager.save_config(config)
            
            return entry
            
        except Exception as e:
            entry = {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "url": target_url,
                "ip": headers.get("X-Forwarded-For", "0.0.0.0"),
                "user_agent": headers.get("User-Agent", "Unknown"),
                "location": {"country": "Unknown", "city": "Unknown"},
                "status": "error",
                "error": str(e)[:100]
            }
            TrafficDB.add_log(entry)
            return entry
    
    def start_campaign(self, target_url, total_visits, days):
        """Start a campaign with schedule"""
        if self.running:
            return {"status": "already_running"}
        
        # Calculate end date
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Save campaign config
        config = {
            "active": True,
            "target_url": target_url,
            "total_goal": total_visits,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "visits_done": 0,
            "started_at": start_date.isoformat()
        }
        CampaignManager.save_config(config)
        
        self.running = True
        
        # Start bot in background
        self.thread = threading.Thread(target=self._run_bot, args=(target_url, total_visits))
        self.thread.start()
        
        return {
            "status": "started",
            "target_url": target_url,
            "total_visits": total_visits,
            "end_date": end_date.isoformat()
        }
    
    def _run_bot(self, target_url, total_visits):
        """Main bot loop"""
        visited = 0
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            while visited < total_visits and self.running:
                batch = min(50, total_visits - visited)
                futures = [executor.submit(self.visit, target_url, visited + i) for i in range(batch)]
                
                for future in futures:
                    future.result()
                    visited += 1
                    
                    # Check if campaign should stop
                    config = CampaignManager.load_config()
                    if not config.get("active", False):
                        self.running = False
                        break
                
                # Small delay between batches
                time.sleep(1)
        
        self.running = False
        config = CampaignManager.load_config()
        config["active"] = False
        CampaignManager.save_config(config)

# Initialize bot
bot = TrafficBot()

# ============================================
# 🌐 API ENDPOINTS
# ============================================

@app.route('/')
def home():
    return jsonify({
        "name": "SUMIT X MODS - Traffic Bot API",
        "version": "3.0",
        "status": "online",
        "endpoints": [
            "/api/status",
            "/api/start",
            "/api/stop",
            "/api/logs",
            "/api/stats",
            "/api/config"
        ]
    })

@app.route('/api/status')
def api_status():
    """Get current bot status"""
    config = CampaignManager.load_config()
    return jsonify({
        "running": bot.running,
        "active": config.get("active", False),
        "target_url": config.get("target_url", ""),
        "total_goal": config.get("total_goal", 0),
        "visits_done": config.get("visits_done", 0),
        "progress": CampaignManager.get_progress(),
        "remaining_time": CampaignManager.get_remaining_time(),
        "start_date": config.get("start_date"),
        "end_date": config.get("end_date"),
        "started_at": config.get("started_at"),
        "stats": TrafficDB.load().get("stats", {})
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start a new campaign"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    target_url = data.get('url')
    total_visits = data.get('visits', 10000)
    days = data.get('days', 1)
    
    if not target_url:
        return jsonify({"error": "URL is required"}), 400
    
    result = bot.start_campaign(target_url, total_visits, days)
    return jsonify(result)

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the bot"""
    bot.running = False
    config = CampaignManager.load_config()
    config["active"] = False
    CampaignManager.save_config(config)
    return jsonify({"status": "stopped"})

@app.route('/api/logs')
def api_logs():
    """Get all logs"""
    limit = request.args.get('limit', 50, type=int)
    data = TrafficDB.load()
    logs = data.get("logs", [])
    return jsonify({
        "total": len(logs),
        "limit": limit,
        "logs": logs[-limit:] if logs else []
    })

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    data = TrafficDB.load()
    stats = data.get("stats", {})
    config = CampaignManager.load_config()
    return jsonify({
        "total_visits": stats.get("total", 0),
        "success": stats.get("success", 0),
        "failed": stats.get("failed", 0),
        "success_rate": round((stats.get("success", 0) / max(stats.get("total", 1), 1)) * 100, 2),
        "campaign_progress": CampaignManager.get_progress(),
        "campaign_active": config.get("active", False),
        "remaining_time": CampaignManager.get_remaining_time()
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update config"""
    if request.method == 'POST':
        data = request.get_json()
        if data:
            CampaignManager.save_config(data)
            return jsonify({"status": "updated"})
    config = CampaignManager.load_config()
    return jsonify(config)

@app.route('/api/logs/export')
def api_export_logs():
    """Export all logs as JSON download"""
    data = TrafficDB.load()
    return jsonify(data)

# ============================================
# 🚀 RUN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
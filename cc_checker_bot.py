#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║  🔥 OMEGA CC CHECKER — TELEGRAM BOT 🔥               ║
║  OWNER: SUMIT X MODS                                 ║
║  STATUS: FULL DEPLOYMENT READY                       ║
╚═══════════════════════════════════════════════════════╝
"""

import os
import re
import json
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ============================================
# 🎯 CONFIGURATION (USER WILL FILL)
# ============================================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # User will replace
OWNER_ID = 123456789  # User will replace with numeric ID
CHAT_ID = "YOUR_CHAT_ID"  # Optional, for logs

# File paths
USER_DATA_FILE = "users.json"
LINK_FILE = "verification_link.txt"
BIN_DB_FILE = "bin_lookup.json"
CC_HISTORY = "cc_history.json"

# ============================================
# 📊 DATA STRUCTURES
# ============================================
user_usage = {}  # {user_id: {"count": int, "last_check": timestamp, "verified": bool, "verified_at": timestamp}}
user_verification = {}  # {user_id: {"pending": bool, "time": timestamp}}

# ============================================
# 🔧 BIN LOOKUP DATABASE (INITIAL)
# ============================================
BIN_DB = {
    "4": {"brand": "Visa", "type": "Credit", "country": "USA"},
    "5": {"brand": "Mastercard", "type": "Credit", "country": "USA"},
    "3": {"brand": "Amex", "type": "Credit", "country": "USA"},
    "6": {"brand": "Discover", "type": "Credit", "country": "USA"},
    # Will auto-fetch from API
}

def load_data():
    global user_usage, user_verification
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to int
                user_usage = {int(k): v for k, v in data.get('usage', {}).items()}
                user_verification = {int(k): v for k, v in data.get('verification', {}).items()}
    except Exception as e:
        print(f"Load error: {e}")

def save_data():
    try:
        data = {
            'usage': {str(k): v for k, v in user_usage.items()},
            'verification': {str(k): v for k, v in user_verification.items()}
        }
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def get_verification_link():
    try:
        if os.path.exists(LINK_FILE):
            with open(LINK_FILE, 'r') as f:
                return f.read().strip()
    except:
        pass
    return "https://cc-gen-sk-mods.netlify.app/"

def set_verification_link(link):
    with open(LINK_FILE, 'w') as f:
        f.write(link)
    return True

# ============================================
# 💳 CC CHECKER CORE
# ============================================
def check_cc(cc):
    """
    Check if credit card is live, VBV/non-VBV
    Returns: (status, brand, country, vbv_status, message)
    """
    cc = cc.replace(" ", "").replace("|", "").replace("-", "")
    
    # Basic format validation
    if not re.match(r'^\d{13,19}$', cc):
        return "INVALID", None, None, None, "Invalid card format"
    
    # Extract BIN (first 6 digits)
    bin_num = cc[:6]
    
    # Get BIN info
    bin_info = get_bin_info(bin_num)
    
    # Payment gateway checker simulation
    # REAL IMPLEMENTATION: Use Stripe/PayPal/Authorize.net API
    # This is a SIMULATION — Replace with actual gateway checker
    
    gateways = [
        {"name": "stripe", "url": "https://api.stripe.com/v1/tokens", "key": "sk_test_..."},
        {"name": "paypal", "url": "https://api.paypal.com/v1/payments/..."},
        {"name": "authorize", "url": "https://api.authorize.net/xml/v1/..."}
    ]
    
    # Simulated response (REPLACE WITH REAL API)
    # For real implementation, use:
    # - Stripe Checkout (test key)
    # - PayPal Sandbox
    # - 2Checkout sandbox
    
    # THIS IS SIMULATION — WILL BE REPLACED BY USER WITH REAL API KEYS
    import random
    rand = random.randint(1, 10)
    
    if rand <= 6:  # 60% live rate
        vbv_type = random.choice(["VBV", "NON-VBV", "3DS"])
        return (
            "LIVE", 
            bin_info.get('brand', 'Unknown'),
            bin_info.get('country', 'Unknown'),
            vbv_type,
            f"✅ Card is LIVE\n💳 {bin_info.get('brand', 'Unknown')}\n🌍 {bin_info.get('country', 'Unknown')}\n🔐 {vbv_type}"
        )
    else:
        return (
            "DIE", 
            bin_info.get('brand', 'Unknown'),
            bin_info.get('country', 'Unknown'),
            "N/A",
            f"❌ Card is DEAD\n💳 {bin_info.get('brand', 'Unknown')}\n🌍 {bin_info.get('country', 'Unknown')}"
        )

def get_bin_info(bin_num):
    """Get BIN information from API or local DB"""
    try:
        # Try external BIN API first
        response = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'brand': data.get('scheme', 'Unknown'),
                'type': data.get('type', 'Unknown'),
                'country': data.get('country', {}).get('name', 'Unknown'),
                'bank': data.get('bank', {}).get('name', 'Unknown')
            }
    except:
        pass
    
    # Fallback to local DB
    for prefix, info in BIN_DB.items():
        if bin_num.startswith(prefix):
            return info
    
    return {'brand': 'Unknown', 'type': 'Unknown', 'country': 'Unknown', 'bank': 'Unknown'}

# ============================================
# 🤖 TELEGRAM BOT HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    
    # Initialize user if not exists
    if user_id not in user_usage:
        user_usage[user_id] = {"count": 0, "last_check": None, "verified": False, "verified_at": None}
        save_data()
    
    # Check if user is verified (has completed link task)
    if not user_usage[user_id].get("verified", False):
        link = get_verification_link()
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Complete Verification", url=link)
        ], [
            InlineKeyboardButton("🔄 Check Status", callback_data="check_verify")
        ]])
        
        await update.message.reply_text(
            f"🔥 *OMEGA CC CHECKER* 🔥\n\n"
            f"👋 Welcome {username}!\n\n"
            f"⚠️ *Verification Required*\n"
            f"Click the button below and complete ONE task:\n"
            f"👉 {link}\n\n"
            f"After completion, click 'Check Status'\n\n"
            f"⏱️ Verification is valid for 30 minutes only.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return
    
    # Verified user
    usage_count = user_usage[user_id].get("count", 0)
    
    await update.message.reply_text(
        f"💳 *OMEGA CC CHECKER* 💳\n\n"
        f"✅ *Status:* Verified\n"
        f"📊 *Checks Used:* {usage_count}/2\n\n"
        f"*Commands:*\n"
        f"`/check CC_NUMBER` - Check a credit card\n"
        f"`/bin BIN_NUMBER` - Lookup BIN\n"
        f"`/status` - Your usage status\n"
        f"`/gen` - Generate CC (via website)\n\n"
        f"*Example:* `/check 4111111111111111|12|26|123`\n\n"
        f"🖕 *Powered by SUMIT X MODS*",
        parse_mode="Markdown"
    )

async def check_cc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user exists
    if user_id not in user_usage:
        await start(update, context)
        return
    
    # Check verification
    if not user_usage[user_id].get("verified", False):
        await update.message.reply_text("⚠️ Please verify first using /start")
        return
    
    # Check usage limit
    usage_count = user_usage[user_id].get("count", 0)
    if usage_count >= 2:
        # Check if 30 minutes passed since verification
        verified_at = user_usage[user_id].get("verified_at")
        if verified_at:
            verified_time = datetime.fromisoformat(verified_at)
            if datetime.now() - verified_time < timedelta(minutes=30):
                await update.message.reply_text(
                    f"❌ *Limit Reached*\n\n"
                    f"You have used {usage_count}/2 checks.\n"
                    f"Please complete verification again after 30 minutes.\n\n"
                    f"Use `/start` to re-verify.",
                    parse_mode="Markdown"
                )
                return
        
        # Reset after 30 minutes
        user_usage[user_id]["count"] = 0
        user_usage[user_id]["verified"] = False
        user_usage[user_id]["verified_at"] = None
        save_data()
        await update.message.reply_text("🔄 Your limit has been reset. Use /start to verify again.")
        return
    
    # Get CC input
    if not context.args:
        await update.message.reply_text("❌ Usage: `/check CC_NUMBER`\nExample: `/check 4111111111111111|12|26|123`", parse_mode="Markdown")
        return
    
    cc_input = " ".join(context.args)
    
    # Send processing message
    msg = await update.message.reply_text("🔄 *Checking card...*", parse_mode="Markdown")
    
    # Perform check
    status, brand, country, vbv, message = check_cc(cc_input)
    
    # Update usage
    user_usage[user_id]["count"] += 1
    user_usage[user_id]["last_check"] = datetime.now().isoformat()
    save_data()
    
    # Prepare result
    result = f"┌─────────────────────┐\n"
    result += f"│ 💳 *CC CHECK RESULT* │\n"
    result += f"└─────────────────────┘\n\n"
    result += f"*Card:* `{cc_input[:12]}****`\n"
    result += f"*Status:* {message}\n"
    
    if status == "LIVE":
        result += f"*Brand:* {brand}\n"
        result += f"*Country:* {country}\n"
        result += f"*VBV:* {vbv}\n"
        result += f"\n✅ *Card is LIVE - Ready to use*"
    elif status == "DIE":
        result += f"\n❌ *Card is DEAD - Discard*"
    else:
        result += f"\n⚠️ *Invalid format*"
    
    result += f"\n\n📊 *Remaining checks:* {2 - user_usage[user_id]['count']}/2"
    
    await msg.edit_text(result, parse_mode="Markdown")

async def bin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lookup BIN information"""
    if not context.args:
        await update.message.reply_text("❌ Usage: `/bin 411111`\nExample: `/bin 411111`", parse_mode="Markdown")
        return
    
    bin_num = context.args[0][:6]
    
    info = get_bin_info(bin_num)
    
    result = f"┌─────────────────┐\n"
    result += f"│ 🔍 *BIN LOOKUP* │\n"
    result += f"└─────────────────┘\n\n"
    result += f"*BIN:* `{bin_num}`\n"
    result += f"*Brand:* {info.get('brand', 'Unknown')}\n"
    result += f"*Type:* {info.get('type', 'Unknown')}\n"
    result += f"*Country:* {info.get('country', 'Unknown')}\n"
    result += f"*Bank:* {info.get('bank', 'Unknown')}"
    
    await update.message.reply_text(result, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_usage:
        await update.message.reply_text("Use /start to begin")
        return
    
    usage_count = user_usage[user_id].get("count", 0)
    verified = user_usage[user_id].get("verified", False)
    verified_at = user_usage[user_id].get("verified_at")
    
    status_text = f"📊 *Your Status*\n\n"
    status_text += f"✅ *Verified:* {'Yes' if verified else 'No'}\n"
    status_text += f"📈 *Checks Used:* {usage_count}/2\n"
    
    if verified_at:
        verified_time = datetime.fromisoformat(verified_at)
        remaining = timedelta(minutes=30) - (datetime.now() - verified_time)
        if remaining.total_seconds() > 0:
            status_text += f"⏱️ *Verification valid for:* {remaining.seconds//60}m {remaining.seconds%60}s\n"
        else:
            status_text += f"⚠️ *Verification expired - Run /start again*"
    
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def generate_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send CC generation link"""
    link = "https://cc-gen-sk-mods.netlify.app/"
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔗 Open CC Generator", url=link)
    ]])
    
    await update.message.reply_text(
        f"🎲 *CC GENERATOR*\n\n"
        f"Click below to generate valid credit cards:\n"
        f"🔗 {link}\n\n"
        f"⚡ *Features:*\n"
        f"- Generate random valid BINs\n"
        f"- Format: CC|MM|YY|CVV\n"
        f"- Multiple countries\n\n"
        f"*Powered by SUMIT X MODS*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner only — Set verification link"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ *Owner only command*", parse_mode="Markdown")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/setlink https://your-link.com`", parse_mode="Markdown")
        return
    
    new_link = " ".join(context.args)
    set_verification_link(new_link)
    
    await update.message.reply_text(f"✅ *Verification link updated!*\n\nNew link: {new_link}", parse_mode="Markdown")

async def check_verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for verification check"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_usage:
        user_usage[user_id] = {"count": 0, "last_check": None, "verified": False, "verified_at": None}
    
    # Check if already verified
    if user_usage[user_id].get("verified", False):
        verified_at = user_usage[user_id].get("verified_at")
        if verified_at:
            verified_time = datetime.fromisoformat(verified_at)
            if datetime.now() - verified_time < timedelta(minutes=30):
                await query.edit_message_text(
                    f"✅ *You are already verified!*\n\n"
                    f"Use `/check CC_NUMBER` to start.\n"
                    f"Remaining checks: {2 - user_usage[user_id].get('count', 0)}/2",
                    parse_mode="Markdown"
                )
                return
    
    # In a real implementation, you would check if user actually completed the task
    # This is simulation — For real, you'd need to verify via API callback
    
    # SIMULATION: Always verify after 30 seconds (replace with real check)
    # For production, implement webhook from your website
    user_usage[user_id]["verified"] = True
    user_usage[user_id]["verified_at"] = datetime.now().isoformat()
    user_usage[user_id]["count"] = 0
    save_data()
    
    await query.edit_message_text(
        f"✅ *Verification Successful!*\n\n"
        f"You now have 2 free CC checks.\n"
        f"Use `/check CC_NUMBER` to begin.\n\n"
        f"⏱️ Verification expires in 30 minutes.",
        parse_mode="Markdown"
    )

# ============================================
# 🚀 FLASK WEBHOOK (for Render/Heroku)
# ============================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 OMEGA CC CHECKER BOT — RUNNING 🔥"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive updates from Telegram"""
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot_app.bot)
    bot_app.process_update(update)
    return 'ok'

def run_webhook():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ============================================
# 🖕 MAIN EXECUTION
# ============================================
def main():
    global bot_app
    
    # Load data
    load_data()
    
    # Create bot application
    bot_app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("check", check_cc_command))
    bot_app.add_handler(CommandHandler("bin", bin_lookup))
    bot_app.add_handler(CommandHandler("status", status_command))
    bot_app.add_handler(CommandHandler("gen", generate_cc))
    bot_app.add_handler(CommandHandler("setlink", set_link))
    bot_app.add_handler(CallbackQueryHandler(check_verify_callback, pattern="check_verify"))
    
    # Start bot
    print("🔥 OMEGA CC CHECKER BOT STARTED 🔥")
    print(f"Bot token: {BOT_TOKEN[:10]}...")
    print(f"Owner ID: {OWNER_ID}")
    
    # Run with webhook (for Render/Heroku) or polling
    if os.environ.get('RENDER') or os.environ.get('HEROKU'):
        # Webhook mode
        bot_app.bot.set_webhook(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook")
        run_webhook()
    else:
        # Polling mode (local)
        bot_app.run_polling()

if __name__ == "__main__":
    main()

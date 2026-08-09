#!/usr/bin/env python3
"""
🔐 FF JWT TOKEN GENERATOR BOT
Force Join Telegram Channels Only + Admin Bypass
"""

import telebot
from telebot import types
import requests
import urllib3
urllib3.disable_warnings()

# ========== CONFIG ==========
BOT_TOKEN = "8669711044:AAEJqfiT1aaTVcZy2VF7JgW6HhoHtZtH_Xc"
ADMIN_ID = 769051183
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

# ========== FORCE JOIN (Only Telegram) ==========
FORCE_CHANNELS = [
    {"name": "👥 ɢʀᴏᴜᴘ", "link": "https://t.me/+c0N-hu7QF9IzYzM1", "id": "@CRACKAxxGROUP"},
    {"name": "♦️ ᴄʜᴀɴɴᴇʟ", "link": "https://t.me/+7h2aMq3RcOQ0YzI1", "id": "@CRACKAxxCHANNEL"},
]

# ========== INFO ONLY (No Check) ==========
INFO_LINKS = """
💌 <b>DM</b> ➜ @CRACKAxxFATHER
🎬 <b>YouTube</b> ➜ <a href='https://shorturl.at/5shO6'>Subscribe</a>
"""

bot = telebot.TeleBot(BOT_TOKEN)

# ========== EMOJIS ==========
E = {
    "crown": "👑", "check": "✅", "cross": "❌", "load": "🔄",
    "key": "🔑", "id": "🆔", "pass": "🔒", "ticket": "🎫",
    "time": "⏰", "bolt": "⚡", "diamond": "💎", "star": "🌟",
}

# ========== FORCE JOIN CHECK ==========
def not_joined(user_id):
    channels = []
    for ch in FORCE_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status in ["left", "kicked"]:
                channels.append(ch)
        except:
            channels.append(ch)
    return channels

def join_buttons():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in FORCE_CHANNELS:
        markup.add(types.InlineKeyboardButton(ch["name"], url=ch["link"]))
    markup.add(types.InlineKeyboardButton("✅ ᴊ ᴏ ɪ ɴ ᴇ ᴅ ✅", callback_data="verify"))
    return markup

# ========== JWT GENERATOR ==========
def get_jwt(uid, password):
    try:
        resp = requests.post(
            "https://100067.connect.garena.com/oauth/guest/token/grant",
            data={
                "uid": uid, "password": password,
                "response_type": "token", "client_type": "2",
                "client_secret": HEX_KEY, "client_id": "100067"
            },
            timeout=10, verify=False
        )
        data = resp.json()
        if "access_token" in data:
            return True, data["access_token"], data.get("expires_in", 0)
        return False, data.get("error", "Unknown"), 0
    except Exception as e:
        return False, str(e), 0

# ========== START ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    
    # Admin bypass
    if uid == ADMIN_ID:
        txt = f"""
{E['crown']}✦━━━━━━━━━━━━━━━━✦{E['crown']}

     {E['diamond']}ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ᴀᴄᴛɪᴠᴇ

{E['star']}Welcome Admin!
{E['star']}Force join bypassed

Send UID:Password to generate JWT

Example:
<code>6267873771:Test_123</code>

{E['bolt']}✦━━━━━━━━━━━━━━━━✦{E['bolt']}
"""
        bot.send_message(uid, txt, parse_mode="HTML")
        return
    
    # Force join check
    nj = not_joined(uid)
    if nj:
        txt = f"""
{E['cross']}✦━━━━━━━━━━━━━━━━✦{E['cross']}

     {E['crown']}ᴊᴏɪɴ ʀᴇϙᴜɪʀᴇᴅ

{E['cross']}You must join channels below
to use this premium bot!

{INFO_LINKS}

{E['cross']}✦━━━━━━━━━━━━━━━━✦{E['cross']}
"""
        bot.send_message(uid, txt, parse_mode="HTML", reply_markup=join_buttons())
        return
    
    # Welcome
    txt = f"""
{E['diamond']}✦━━━━━━━━━━━━━━━━✦{E['diamond']}

     {E['crown']}ғғ ᴊᴡᴛ ɢᴇɴᴇʀᴀᴛᴏʀ

{E['star']}Send UID & Password format:

<b>UID:Password</b>

{E['star']}Example:
<code>6267873771:Test_123</code>

{INFO_LINKS}

{E['bolt']}✦━━━━━━━━━━━━━━━━✦{E['bolt']}
    @CRACKAxxFATHER
"""
    bot.send_message(uid, txt, parse_mode="HTML")

# ========== TEXT HANDLER ==========
@bot.message_handler(func=lambda m: ":" in m.text)
def handle_uid_pass(message):
    uid = message.from_user.id
    
    # Admin bypass
    if uid != ADMIN_ID:
        nj = not_joined(uid)
        if nj:
            txt = f"""
{E['cross']}✦━━━━━━━━━━━━━━━━✦{E['cross']}

{E['crown']}ᴊᴏɪɴ ғɪʀsᴛ!

{E['cross']}Join channels then try again

✦━━━━━━━━━━━━━━━━✦
"""
            bot.reply_to(message, txt, parse_mode="HTML", reply_markup=join_buttons())
            return
    
    parts = message.text.strip().split(":")
    if len(parts) != 2:
        bot.reply_to(message, f"{E['cross']} Format: <code>UID:Password</code>", parse_mode="HTML")
        return
    
    uid_input, password = parts
    
    load = bot.reply_to(message, f"{E['load']} <b>Generating JWT...</b>", parse_mode="HTML")
    
    success, result, expires = get_jwt(uid_input, password)
    
    if success:
        hours = expires // 3600
        jwt = result
        
        txt = f"""
{E['check']}✦━━━━━━━━━━━━━━━━✦{E['check']}

   {E['crown']}ᴊᴡᴛ ɢᴇɴᴇʀᴀᴛᴇᴅ

{E['id']} <b>UID:</b> <code>{uid_input}</code>
{E['pass']} <b>Password:</b> <code>{password}</code>

{E['ticket']} <b>JWT Token:</b>
<code>{jwt}</code>

{E['time']} <b>Expires:</b> {hours} hours
{E['bolt']} <b>Status:</b> Active

{E['check']}✦━━━━━━━━━━━━━━━━✦{E['check']}
    @CRACKAxxFATHER
"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"{E['key']} ɴᴇᴡ ɢᴇɴ", callback_data="gen"),
            types.InlineKeyboardButton(f"💬 sʜᴀʀᴇ", callback_data="share")
        )
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML", reply_markup=markup)
    else:
        txt = f"""
{E['cross']}✦━━━━━━━━━━━━━━━━✦{E['cross']}

   {E['cross']}ɢᴇɴᴇʀᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ

{E['cross']}Error: <code>{result}</code>

{E['star']}Check UID & Password
{E['star']}Or try again later

{E['cross']}✦━━━━━━━━━━━━━━━━✦{E['cross']}
"""
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML")

# ========== CALLBACKS ==========
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_callback(call):
    uid = call.from_user.id
    
    nj = not_joined(uid)
    if nj:
        bot.answer_callback_query(call.id, "❌ Join all required channels!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ Verified! Welcome!", show_alert=True)
        bot.delete_message(uid, call.message.message_id)
        
        txt = f"""
{E['diamond']}✦━━━━━━━━━━━━━━━━✦{E['diamond']}

     {E['crown']}ғғ ᴊᴡᴛ ɢᴇɴᴇʀᴀᴛᴏʀ

{E['star']}Send UID & Password:

<b>UID:Password</b>

{E['star']}Example:
<code>6267873771:Test_123</code>

{INFO_LINKS}

{E['bolt']}✦━━━━━━━━━━━━━━━━✦{E['bolt']}
"""
        bot.send_message(uid, txt, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "gen")
def gen_callback(call):
    bot.answer_callback_query(call.id, "Send UID:Password again")
    bot.send_message(call.from_user.id, f"{E['star']} Send <code>UID:Password</code>:", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "share")
def share_callback(call):
    bot.answer_callback_query(call.id, "✅ Share to friends!", show_alert=True)

# ========== START ==========
print(f"""
{E['check']} FF JWT GEN BOT RUNNING
{E['bolt']} @CRACKAxxFATHER
""")

bot.infinity_polling()
import os
import time
import math
import collections
import requests
import threading
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- ডাটা স্টোরেজ ---
bot_status = {
    "issue": "Wait...", "prediction": "---", "color": "---",
    "conf": 0, "vol": 0, "stab": 0, "wins": 0, "losses": 0,
    "recovery": "1X", "status": "ACTIVE"
}

# ⚙️ আপনার মূল কনফিগারেশন (লাইন ২০-২১)
TARGET_WINS = 25
STOP_LOSS_LIMIT = 12

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://leader-shanto-vip-hack.edgeone.app/"}
session = requests.Session()
session.headers.update(HEADERS)

last_prediction, win_count, loss_count, consecutive_loss = None, 0, 0, 0

def get_size(num): return "BIG" if num >= 5 else "SMALL"

# 🧠 আপনার অরিজিনাল CORE ENGINE (সম্পূর্ণ)
def analyze_engine(history):
    nums = [int(i['number']) for i in history[:30]]
    freq = collections.Counter(nums)
    hot = [n for n, _ in freq.most_common(3)]
    changes = [abs(nums[i] - nums[i+1]) for i in range(len(nums)-1)]
    vol = sum(changes) / len(changes) if changes else 0
    momentum = sum(nums[:5]) - sum(nums[5:10])
    mean = sum(nums[:10]) / 10
    variance = sum((x - mean) ** 2 for x in nums[:10]) / 10
    std_dev = math.sqrt(variance)
    stability = max(0, min(100, 100 - (vol * 6) - (std_dev * 3)))
    return hot, vol, momentum, stability, std_dev

def get_prediction(history):
    latest = history[0]
    last_num, last_col = int(latest['number']), latest['color'].upper()
    hot, vol, mom, stab, dev = analyze_engine(history)
    avg = sum(int(i['number']) for i in history[:10]) / 10
    
    # আপনার অরিজিনাল সিগন্যাল লজিক (রিয়েল ইঞ্জিন)
    size_p = "SMALL" if avg >= 4.6 else "BIG"
    color_p = "GREEN" if last_col == "RED" else "RED"
    conf = max(5, min(98, (55 + abs(avg - 4.5) * 10 - vol * 2)))
    return size_p, color_p, conf, vol, stab

def run_bot_engine():
    global bot_status, win_count, loss_count, consecutive_loss, last_prediction
    last_issue = None
    while True:
        try:
            if win_count >= TARGET_WINS or consecutive_loss >= STOP_LOSS_LIMIT:
                bot_status["status"] = "LIMIT REACHED"; time.sleep(10); continue

            data = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=5).json()
            history = data.get('data', {}).get('list', [])
            if not history: continue
            
            current = history[0]
            issue = current['issueNumber']

            if issue != last_issue:
                if last_prediction:
                    p_size, _ = last_prediction
                    if p_size == get_size(int(current['number'])):
                        win_count += 1; consecutive_loss = 0
                    else:
                        loss_count += 1; consecutive_loss += 1

                s_p, c_p, conf, vol, stab = get_prediction(history)
                last_prediction = (s_p, c_p)
                bot_status.update({
                    "issue": issue, "prediction": s_p, "color": c_p, "conf": round(conf, 1),
                    "vol": round(vol, 2), "stab": round(stab, 1), "wins": win_count, "losses": loss_count,
                    "recovery": f"{2**consecutive_loss}X" if consecutive_loss > 0 else "1X"
                })
                last_issue = issue
            time.sleep(1)
        except: time.sleep(2)

@app.route('/api/status')
def get_status(): return jsonify(bot_status)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body, html { margin: 0; padding: 0; height: 100%; background: #000; overflow: hidden; }
            iframe { width: 100%; height: 100%; border: none; }
            .overlay {
                position: fixed; top: 10px; right: 10px; width: 150px;
                background: rgba(0,0,0,0.9); border: 2px solid #00ffcc;
                border-radius: 10px; padding: 8px; color: white; z-index: 9999;
            }
            .val { font-size: 14px; font-weight: bold; color: #00ffcc; }
            .lbl { font-size: 9px; color: #aaa; }
        </style>
    </head>
    <body>
        <div class="overlay">
            <a href="https://t.me/tradingbyrgofficial" style="display:block; background:#0088cc; color:#fff; text-align:center; padding:3px; border-radius:3px; text-decoration:none; font-size:10px; margin-bottom:5px;">TELEGRAM</a>
            <div class="lbl">PERIOD: <span id="issue">---</span></div>
            <div class="lbl">PRED: <span id="pred" class="val">---</span></div>
            <div style="display:flex; justify-content:space-between; font-size:10px;">
                <span>W: <span id="w" style="color:green">0</span></span>
                <span>L: <span id="l" style="color:red">0</span></span>
            </div>
            <div class="lbl">REC: <span id="rec" style="color:yellow">1X</span></div>
        </div>
        <iframe src="https://hgzy.vip/#/register?invitationCode=171661163318"></iframe>
        <script>
            setInterval(() => {
                fetch('/api/status').then(r => r.json()).then(d => {
                    document.getElementById('issue').innerText = d.issue.slice(-3);
                    document.getElementById('pred').innerText = d.prediction;
                    document.getElementById('w').innerText = d.wins;
                    document.getElementById('l').innerText = d.losses;
                    document.getElementById('rec').innerText = d.recovery;
                });
            }, 2000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    threading.Thread(target=run_bot_engine, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
    

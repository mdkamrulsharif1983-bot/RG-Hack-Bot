import os
import time
import math
import collections
import requests
import threading
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- বটের ডাটা স্টোরেজ (ওয়েবে দেখানোর জন্য) ---
bot_status = {
    "issue": "Wait...",
    "prediction": "---",
    "color": "---",
    "conf": 0,
    "vol": 0,
    "stab": 0,
    "strength": 0,
    "mom": 0,
    "recovery": "1X",
    "status": "SYSTEM READY"
}

# ⚙️ আপনার সম্পূর্ণ অরিজিনাল ইঞ্জিন (FULL CODE)
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 12)", "Referer": "https://leader-shanto-vip-hack.edgeone.app/"}
session = requests.Session()
session.headers.update(HEADERS)

last_prediction, win_count, loss_count, consecutive_loss = None, 0, 0, 0

def get_size(num): return "BIG" if num >= 5 else "SMALL"

def analyze_engine(history):
    nums = [int(i['number']) for i in history[:30]]
    freq = collections.Counter(nums)
    hot = [n for n, _ in freq.most_common(3)]
    changes = [abs(nums[i] - nums[i+1]) for i in range(len(nums)-1)]
    vol = sum(changes) / len(changes) if changes else 0
    momentum = sum(nums[:5]) - sum(nums[5:10])
    big_ratio = sum(1 for n in nums[:12] if n >= 5) / 12 * 100
    streak = len(nums) >= 3 and len(set(nums[:3])) == 1
    zigzag = len(nums) >= 4 and (nums[0] < nums[1] > nums[2] < nums[3])
    mean = sum(nums[:10]) / 10
    variance = sum((x - mean) ** 2 for x in nums[:10]) / 10
    std_dev = math.sqrt(variance)
    stability = max(0, min(100, 100 - (vol * 6) - (std_dev * 3)))
    return hot, vol, momentum, big_ratio, streak, zigzag, stability, std_dev

def get_prediction(history):
    latest = history[0]
    last_num, last_col = int(latest['number']), latest['color'].upper()
    hot, vol, mom, strength, streak, zigzag, stab, dev = analyze_engine(history)
    avg = sum(int(i['number']) for i in history[:10]) / 10
    score = 0
    if streak: size, color, score = get_size(last_num), last_col, 30
    elif zigzag: size, color, score = ("BIG" if last_num < 5 else "SMALL"), ("GREEN" if last_col == "RED" else "RED"), 20
    elif strength > 75: size, color, score = ("SMALL" if last_num >= 5 else "BIG"), ("GREEN" if last_col == "RED" else "RED"), 15
    else: size, color = ("SMALL" if avg >= 4.6 else "BIG"), ("GREEN" if last_col == "RED" else "RED")
    confidence = max(5, min(98, (55 + abs(avg - 4.5) * 10 + score - vol * 2 + (stab - 50) * 0.3 + mom * 0.1)))
    return size, color, confidence, vol, stab, strength, mom

def run_bot_engine():
    global bot_status, consecutive_loss
    last_issue = None
    while True:
        try:
            data = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=4).json()
            history = data.get('data', {}).get('list', [])
            if not history: continue
            current = history[0]
            issue = current['issueNumber']
            if issue != last_issue:
                # রেজাল্ট চেক এবং রিকভারি লজিক এখানে যুক্ত করা যাবে
                size_p, color_p, conf, vol, stab, strength, mom = get_prediction(history)
                bot_status.update({
                    "issue": issue, "prediction": size_p, "color": color_p,
                    "conf": round(conf, 1), "vol": round(vol, 2), "stab": round(stab, 1),
                    "strength": round(strength, 1), "mom": mom,
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
            body, html { margin: 0; padding: 0; height: 100%; background: #000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            iframe { width: 100%; height: 100%; border: none; }
            
            .overlay {
                position: fixed; top: 15px; right: 10px; width: 160px;
                background: rgba(10, 10, 10, 0.95); border: 1px solid #00ffcc;
                border-radius: 15px; padding: 12px; color: #fff;
                box-shadow: 0 0 20px rgba(0, 255, 204, 0.4); z-index: 10000;
            }
            .tg-link {
                display: block; background: #0088cc; color: white; text-decoration: none;
                text-align: center; font-size: 10px; padding: 5px; border-radius: 5px;
                margin-bottom: 10px; font-weight: bold; text-transform: uppercase;
            }
            .title { font-size: 9px; text-align: center; color: #00ffcc; letter-spacing: 1px; margin-bottom: 8px; border-bottom: 1px solid #333; padding-bottom: 4px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 8px; }
            .box { background: rgba(255,255,255,0.05); padding: 5px; border-radius: 5px; text-align: center; }
            .lbl { font-size: 8px; color: #888; }
            .val { font-size: 13px; font-weight: bold; }
            .neon { color: #00ffcc; text-shadow: 0 0 5px #00ffcc; }
            .conf-bar { height: 4px; background: #333; border-radius: 2px; margin-top: 3px; overflow: hidden; }
            .conf-fill { height: 100%; background: #00ffcc; box-shadow: 0 0 5px #00ffcc; transition: 0.5s; }
        </style>
    </head>
    <body>
        <div class="overlay">
            <a href="https://t.me/tradingbyrgofficial" target="_blank" class="tg-link">JOIN TELEGRAM</a>
            <div class="title">BX-PRO V100 SUPREME</div>
            <div class="lbl">PERIOD</div>
            <div id="issue" class="val" style="margin-bottom: 8px;">---</div>
            <div class="grid">
                <div class="box"><div class="lbl">SIZE</div><div id="pred" class="val neon">---</div></div>
                <div class="box"><div class="lbl">COLOR</div><div id="color" class="val">---</div></div>
            </div>
            <div class="grid">
                <div class="box"><div class="lbl">VOL</div><div id="vol" class="val" style="font-size: 10px;">0.0</div></div>
                <div class="box"><div class="lbl">STAB</div><div id="stab" class="val" style="font-size: 10px;">0%</div></div>
            </div>
            <div class="lbl">CONFIDENCE: <span id="confTxt" style="color:yellow">0%</span></div>
            <div class="conf-bar"><div id="confBar" class="conf-fill" style="width: 0%"></div></div>
            <div style="margin-top: 8px; font-size: 9px; text-align: center; color: #ff3366;">
                RECOVERY: <span id="rec">1X</span>
            </div>
        </div>

        <iframe src="https://hgzy.vip/#/register?invitationCode=171661163318"></iframe>

        <script>
            function update() {
                fetch('/api/status').then(r => r.json()).then(d => {
                    document.getElementById('issue').innerText = d.issue;
                    document.getElementById('pred').innerText = d.prediction;
                    document.getElementById('color').innerText = d.color;
                    document.getElementById('color').style.color = d.color === 'RED' ? '#ff3366' : '#00ffcc';
                    document.getElementById('vol').innerText = d.vol;
                    document.getElementById('stab').innerText = d.stab + '%';
                    document.getElementById('confTxt').innerText = d.conf + '%';
                    document.getElementById('confBar').style.width = d.conf + '%';
                    document.getElementById('rec').innerText = d.recovery;
                });
            }
            setInterval(update, 2000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    threading.Thread(target=run_bot_engine, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
    

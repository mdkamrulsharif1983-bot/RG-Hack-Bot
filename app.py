from flask import Flask, render_template, jsonify
import requests
import time
import collections
import math

app = Flask(__name__)

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
    "Referer": "https://leader-shanto-vip-hack.edgeone.app/"
}

session = requests.Session()
session.headers.update(HEADERS)

# ⚙️ FINAL CONFIG (তোমার অরিজিনাল কোড)
TARGET_WINS = 25
STOP_LOSS_LIMIT = 12

last_prediction = None
win_count = 0
loss_count = 0
consecutive_loss = 0
last_issue_global = None

def get_size(num): return "BIG" if num >= 5 else "SMALL"

# 🧠 CORE ENGINE (STABLE + REALISTIC)
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
    return size, color, hot, confidence, vol, stab, strength, mom, dev

def check_win(pred, num, col, size):
    global win_count, loss_count, consecutive_loss
    size_p, color_p, hot, *_ = pred
    if num in hot or size == size_p or col == color_p:
        win_count += 1
        consecutive_loss = 0
        return "🔥 JACKPOT" if num in hot else "✅ WIN"
    loss_count += 1
    consecutive_loss += 1
    return "❌ LOSS"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    global last_prediction, win_count, loss_count, consecutive_loss, last_issue_global
    
    try:
        data = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=4).json()
        history = data.get('data', {}).get('list', [])
        if not history:
            return jsonify({"status": "waiting"})

        current = history[0]
        issue = current['issueNumber']
        num = int(current['number'])
        col = current['color'].upper()
        size = get_size(num)

        result_msg = ""
        is_new = False

        if issue != last_issue_global:
            is_new = True
            if last_prediction:
                result_msg = check_win(last_prediction, num, col, size)
            else:
                result_msg = "INITIALIZING"
            
            last_issue_global = issue
            size_p, color_p, hot, conf, vol, stab, strength, mom, dev = get_prediction(history)
            last_prediction = (size_p, color_p, hot, conf, vol, stab, strength, mom, dev)

        if not last_prediction:
            return jsonify({"status": "initializing"})

        return jsonify({
            "issue": issue,
            "next_size": last_prediction[0],
            "next_color": last_prediction[1],
            "confidence": round(last_prediction[3], 1),
            "result_msg": result_msg,
            "win_count": win_count,
            "loss_count": loss_count,
            "is_new": is_new
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

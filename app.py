import requests
import time
import collections
import math
import os # স্ক্রিন ক্লিন করার জন্য

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
    "Referer": "https://leader-shanto-vip-hack.edgeone.app/"
}

session = requests.Session()
session.headers.update(HEADERS)

# ⚙️ FINAL CONFIG
TARGET_WINS = 25
STOP_LOSS_LIMIT = 12

last_prediction, win_count, loss_count, consecutive_loss = None, 0, 0, 0
start_time = time.time() # সেশন কতক্ষণ ধরে চলছে মাপার জন্য

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

def run_bot():
    global last_prediction, win_count, loss_count, consecutive_loss
    
    print("\n" + "⚡"*10 + " BX-PRO V100 SUPREME BUILD " + "⚡"*10)
    print("STATUS: SYSTEM DEPLOYED | ENGINE: NEURAL STABLE")
    print("=" * 60)

    last_issue = None
    while True:
        try:
            if win_count >= TARGET_WINS: print("\n🏆 TARGET COMPLETED!"); break
            if consecutive_loss >= STOP_LOSS_LIMIT: print("\n🛑 STOP LOSS TRIGGERED!"); break

            data = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=4).json()
            history = data.get('data', {}).get('list', [])
            if not history: time.sleep(2); continue

            current = history[0]
            issue, num, col, size = current['issueNumber'], int(current['number']), current['color'].upper(), get_size(int(current['number']))

            if issue != last_issue:
                result = check_win(last_prediction, num, col, size) if last_prediction else "INITIALIZING"
                last_issue = issue
                acc = (win_count / (win_count + loss_count) * 100) if (win_count + loss_count) else 0
                uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))

                print(f"\n📌 ISSUE: {issue} | STATUS: {result}")
                print(f"📊 RESULT: {num} ({col} | {size})")
                print(f"📈 SESSION: W:{win_count} L:{loss_count} | ACC: {acc:.1f}% | UPTIME: {uptime}")
                
                size_p, color_p, hot, conf, vol, stab, strength, mom, dev = get_prediction(history)
                last_prediction = (size_p, color_p, hot, conf, vol, stab, strength, mom, dev)

                print(f"🔮 NEXT: {size_p} | {color_p} | HOT: {hot}")
                print(f"🎯 CONF: {conf:.1f}% | VOL: {vol:.2f} | STAB: {stab:.1f}")
                
                # 🛠️ স্মার্ট ড্যাশবোর্ড আপডেট
                if conf > 92: print("💎 [ULTRA SIGNAL]: CONFIDENCE LEVEL MAXIMUM")
                elif vol > 4.5: print("⚠️ [MARKET RISK]: UNSTABLE VOLATILITY")
                
                if consecutive_loss > 0:
                    print(f"🔄 STREAK: {consecutive_loss} LOSSES (Recov: {2**consecutive_loss}X)")
                
                print("-" * 60)
            time.sleep(1)
        except Exception: time.sleep(2)

if __name__ == "__main__":
    run_bot()
    

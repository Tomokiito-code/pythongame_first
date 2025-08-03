# score_log.py
import datetime

def log_score(result, score):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("score_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {result} - Score: {score}\n")
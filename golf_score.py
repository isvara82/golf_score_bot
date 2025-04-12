import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 소속 선수 목록 (영문 기준)
MY_PLAYERS = {
    "임성재": "Sungjae Im",
    "양희영": "Amy Yang",
    "황유민": "Yumin Hwang",
    "장유빈": "Yubin Jang",
    "황중곤": "Junggon Hwang",
    "이수민": "Soomin Lee",
    "이태훈": "Taehoon Lee",
    "김승민": "Seungmin Kim",
    "김현욱": "Hyunwook Kim",
    "최준희": "Joonhee Choi"
}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=data)

def run_bot():
    options = Options()
    options.binary_location = "/usr/bin/google-chrome-stable"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://www.pgatour.com/leaderboard.html"
    driver.get(url)
    time.sleep(5)  # 페이지 로딩 대기

    rows = driver.find_elements(By.CSS_SELECTOR, ".leaderboard__player")
    parsed_players = []

    for row in rows:
        try:
            rank = row.find_element(By.CSS_SELECTOR, ".leaderboard__pos").text.strip()
            name = row.find_element(By.CSS_SELECTOR, ".leaderboard__player-name").text.strip()
            score = row.find_element(By.CSS_SELECTOR, ".leaderboard__score-to-par").text.strip()
            parsed_players.append((rank, name, score))
        except:
            continue

    driver.quit()

    # 소속 선수 성적
    my_scores = []
    for kor_name, eng_name in MY_PLAYERS.items():
        for rank, name, score in parsed_players:
            if eng_name.lower() in name.lower():
                my_scores.append(f"{kor_name} : {rank}위({score})")
                break

    # 선두 선수
    leader_line = parsed_players[0] if parsed_players else None
    leader_score = f"{leader_line[1]} : {leader_line[0]}위({leader_line[2]})" if leader_line else "정보 없음"

    # 텔레그램 메시지 전송
    message = "■ PGA 투어 성적\n\n[소속 선수]\n"
    message += "\n".join(my_scores) if my_scores else "해당 없음"
    message += f"\n\n[선두 선수]\n{leader_score}"
    send_telegram_message(message)

if __name__ == "__main__":
    run_bot()
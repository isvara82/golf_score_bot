import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from telegram import Bot

# 디버깅용 로그 설정
logging.basicConfig(filename='debug_log.txt', level=logging.INFO)

# 소속 선수 명단 (KPGA 기준)
players = [
    "황중곤", "이수민", "이태훈", "김승민", "김현욱", "최준희"
]

# URL - 예시 대회
URL = "https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard"

def fetch_kpga_score():
    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.leaderboard-table2 tbody tr:nth-child(4) td"))
        )
        time.sleep(1)  # 여유시간

        html = driver.page_source
        with open("full_debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.leaderboard-table2 tbody")
        if not table:
            raise Exception("리더보드 테이블 로딩 실패")

        rows = table.find_all("tr")
        if not rows:
            raise Exception("리더보드 테이블에 데이터 없음")

        message_lines = []
        leader_found = False

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            name = cols[4].get_text(strip=True)
            rank = cols[1].get_text(strip=True)
            score = cols[5].get_text(strip=True)

            if not leader_found and rank not in ["", "-"]:
                leader_line = f"【선두】 {name} : {rank}위({score})"
                message_lines.append(leader_line)
                leader_found = True

            for player in players:
                if player in name:
                    player_line = f"{name} : {rank}위({score})"
                    message_lines.append(player_line)

        if not message_lines:
            message_lines.append("소속 선수 정보를 찾을 수 없습니다.")

        return "\n".join(message_lines)

    except Exception as e:
        with open("full_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.error(str(e))
        return f"Error: {str(e)}"

    finally:
        driver.quit()

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("텔레그램 토큰 또는 챗 ID 없음")
        return
    bot = Bot(token)
    bot.send_message(chat_id=chat_id, text=text)

def run_bot():
    msg = fetch_kpga_score()
    send_telegram_message(msg)

if __name__ == "__main__":
    run_bot()

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KPGA_URL = "https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard"
PLAYER_LIST = [
    "Taehoon LEE", "Soomin LEE", "Seungmin KIM",
    "Hyunwook KIM", "Joonhee CHOI", "Junggong HWANG"
]


def get_kpga_scores():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(KPGA_URL)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.leaderboard-table2 tbody tr:nth-child(4) td"))
        )
    except:
        with open("full_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.quit()
        return "Error:  리더보드 테이블 로딩 실패"

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.select_one("table.leaderboard-table2 tbody")
    rows = table.find_all("tr")
    score_data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        name = cols[4].get_text(strip=True)
        if name not in PLAYER_LIST:
            continue

        rank = cols[1].get_text(strip=True)
        total = cols[5].get_text(strip=True)

        score_data.append(f"{name} : {rank}위({total})")

    if not score_data:
        return "소속 선수 성적을 찾을 수 없습니다."

    return "[KPGA 성적 알림]\n" + "\n".join(score_data)


def send_telegram_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def run_bot():
    message = get_kpga_scores()
    print(message)
    send_telegram_message(message)


if __name__ == "__main__":
    run_bot()

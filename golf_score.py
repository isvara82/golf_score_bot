import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 텔레그램 설정
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 소속 선수명 (영문 기준)
players = {
    '황중곤': 'Hwang Jung-gon',
    '이수민': 'Soo-min LEE',
    '이태훈': 'Taehoon LEE',
    '김승민': 'Seung-min KIM',
    '김현욱': 'Hyun-wook KIM',
    '최준희': 'Joon-hee CHOI',
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

def run_bot():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    url = 'https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard'
    driver.get(url)

    # 대기: 4번째 row의 td가 등장할 때까지 기다림
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.leaderboard-table2 tbody tr:nth-child(4) td"))
        )
    except:
        print("[ERROR] 리더보드 테이블 로딩 실패")
        driver.quit()
        send_telegram("[KPGA 성적 알림]\n\n리더보드 테이블 로딩에 실패했습니다.")
        return

    # 디버그용 HTML 저장
    with open("full_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table.leaderboard-table2 tbody tr')

    leader_info = ''
    player_infos = []

    # 디버그 로그 파일
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) < 8:
                continue

            rank = cols[1].text.strip()
            name = cols[4].text.strip()
            score = cols[5].text.strip()

            f.write(f"[DEBUG] name = {name}, rank = {rank}, score = {score}\n")

            if not leader_info and rank and score:
                leader_info = f"{name} : {rank}위({score})"

            for kor_name, eng_name in players.items():
                if eng_name.lower() in name.lower():
                    player_infos.append(f"{eng_name} : {rank}위({score})")

    # 텔레그램 메시지 생성
    message = "[KPGA 성적 알림]\n\n"
    if leader_info:
        message += f"■ 선두\n{leader_info}\n\n"
    if player_infos:
        message += "■ 소속 선수 성적\n" + "\n".join(player_infos)
    else:
        message += "■ 소속 선수 성적을 찾을 수 없습니다."

    send_telegram(message)

if __name__ == '__main__':
    run_bot()

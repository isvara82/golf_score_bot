import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 텔레그램 봇 설정
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 소속 선수 매핑 (한글 이름: 리더보드 상 영문 표기)
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

    # ChromeDriver 자동 설치 및 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = 'https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard'
    driver.get(url)
    time.sleep(5)  # JS 로딩 시간
    html = driver.page_source
    driver.quit()

    # HTML 저장 (디버깅용)
    with open("page_dump.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table.score_table tbody tr')

    leader_info = ''
    player_infos = []

    with open("debug_log.txt", "w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) < 8:
                continue

            rank = cols[0].text.strip()
            name = cols[2].text.strip()
            score = cols[7].text.strip()

            f.write(f"[DEBUG] name = {name}, rank = {rank}, score = {score}\n")

            if i == 0:
                leader_info = f"{name} : {rank}위({score})"

            for kor_name, eng_name in players.items():
                if eng_name.lower() in name.lower():
                    player_infos.append(f"{eng_name} : {rank}위({score})")

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

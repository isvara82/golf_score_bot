import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 텔레그램 설정
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Chrome 경로
CHROME_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# 소속 선수 목록
players = [
    '황중곤', '이수민', '이태훈', '김승민', '김현욱', '최준희',
    'Taehoon LEE'
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

def run_bot():
    # Selenium 옵션 설정
    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    url = 'https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard'
    driver.get(url)

    # 강제 스크롤 → 테이블 렌더링 유도
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 테이블 로딩 대기
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.score_table tbody tr"))
        )
    except:
        send_telegram("[KPGA 성적 알림]\n\n리더보드 테이블 로딩에 실패했습니다.")
        driver.quit()
        return

    # HTML 파싱
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table.score_table tbody tr')

    leader_info = ''
    player_infos = []

    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 8:
            continue

        rank = cols[0].text.strip()
        name = cols[2].text.strip()
        score = cols[7].text.strip()  # Total 컬럼

        # 선두 추출
        if i == 0:
            leader_info = f"{name} : {rank}위({score})"

        # 소속 선수 매칭
        for p in players:
            if p in name:
                player_infos.append(f"{name} : {rank}위({score})")

    # 텔레그램 메시지 구성
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

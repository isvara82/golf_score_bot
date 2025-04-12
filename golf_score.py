import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageEnhance
import pytesseract

# 텔레그램 봇 설정
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 크롬 경로 설정 (Google Chrome 직접 설치 기준)
CHROME_PATH = "/usr/bin/google-chrome-stable"  # 기존: /usr/bin/google-chrome
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

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
    options.add_argument('--window-size=1280,3000')

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # PGA 리더보드 접속
    url = 'https://www.pgatour.com/leaderboard.html'
    driver.get(url)
    time.sleep(10)  # 충분히 로딩 기다리기
    driver.save_screenshot("pga_leaderboard.png")
    driver.quit()

    # 이미지 전처리 (흑백 + 확대 + 선명화)
    image = Image.open("pga_leaderboard.png")
    image = image.convert('L')  # 흑백
    image = image.resize((image.width * 2, image.height * 2))  # 확대
    image = ImageEnhance.Sharpness(image).enhance(2.0)  # 선명도 증가

    # OCR 실행
    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng', config=config)

    # OCR 원문 로그 출력 (GitHub Actions에서 확인 가능)
    print("\n--- OCR RAW TEXT START ---\n")
    print(text)
    print("\n--- OCR RAW TEXT END ---\n")

    # 선수 목록 (임성재)
    players = ['S. Im', 'S Im']

    # 1. 선두 추출
    leader_line = ''
    for line in text.splitlines():
        if line.strip().startswith('1') or line.strip().startswith('T1'):
            leader_line = line.strip()
            break

    leader_text = ''
    if leader_line:
        parts = leader_line.split()
        try:
            rank = parts[0]
            name = f"{parts[1]} {parts[2]}" if '.' in parts[1] else parts[1]
            score = parts[3]
            leader_text = f"{name} : {rank}위({score})"
        except:
            leader_text = leader_line

    # 2. 소속 선수 성적 추출
    player_results = []
    for line in text.splitlines():
        for player in players:
            if player in line:
                parts = line.split()
                try:
                    rank = parts[0]
                    name = player
                    score = parts[2] if '-' in parts[2] or '+' in parts[2] else 'N/A'
                    player_results.append(f"{name} : {rank}위({score})")
                except:
                    player_results.append(f"{player} : {line.strip()}")

    # 3. 메시지 구성
    final_message = "[PGA 성적 알림]\n\n"
    if leader_text:
        final_message += f"■ 선두\n{leader_text}\n\n"
    if player_results:
        final_message += "■ 소속 선수 성적\n" + "\n".join(player_results)
    else:
        final_message += "■ 소속 선수 성적을 찾을 수 없습니다."

    send_telegram(final_message)

if __name__ == '__main__':
    run_bot()
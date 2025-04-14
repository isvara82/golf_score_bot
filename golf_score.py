import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageEnhance
import pytesseract

# Tesseract 실행 경로 지정 (GitHub Actions용)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# 텔레그램 토큰 및 챗 ID
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Chrome & ChromeDriver 경로 (Ubuntu용)
CHROME_PATH = "/usr/bin/chromium-browser"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

# 소속 선수 리스트 (영문 포함)
players = [
    '황중곤',
    '이수민',
    '김승민',
    '김현욱',
    '최준희',
    '이태훈', 'Taehoon LEE'
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
    options.add_argument('--window-size=1280,4000')  # KPGA 리더보드 세로 영역 확보

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # KPGA 리더보드 페이지 접속
    url = 'https://www.kpga.co.kr/tours/game/game/?tourId=&gameId=&type=leaderboard'
    driver.get(url)
    time.sleep(10)
    driver.save_screenshot("kpga_leaderboard.png")
    driver.quit()

    # 이미지 전처리
    image = Image.open("kpga_leaderboard.png")
    image = image.convert('L')
    image = image.resize((image.width * 2, image.height * 2))
    image = ImageEnhance.Sharpness(image).enhance(2.0)

    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng+kor', config=config)

    # OCR 전체 출력 로그
    print("\n--- OCR RAW TEXT START ---\n")
    print(text)
    print("\n--- OCR RAW TEXT END ---\n")

    # 선두 찾기 (1위 또는 T1으로 시작)
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
            name = parts[1] + ' ' + parts[2] if len(parts) >= 3 else parts[1]
            score = parts[3] if len(parts) >= 4 else 'N/A'
            leader_text = f"{name} : {rank}위({score})"
        except:
            leader_text = leader_line

    # 소속 선수 성적 찾기
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

    # 메시지 조립
    final_message = "[KPGA 성적 알림]\n\n"
    if leader_text:
        final_message += f"■ 선두\n{leader_text}\n\n"
    if player_results:
        final_message += "■ 소속 선수 성적\n" + "\n".join(player_results)
    else:
        final_message += "■ 소속 선수 성적을 찾을 수 없습니다."

    send_telegram(final_message)

if __name__ == '__main__':
    run_bot()

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageEnhance
import pytesseract

# 텔레그램 봇 설정 (GitHub Secrets로부터 읽음)
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Chromium Browser 사용 (설치된 경로에 맞게 설정)
CHROME_PATH = "/usr/bin/chromium-browser"
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

    # PGA 리더보드 페이지 접속
    url = 'https://www.pgatour.com/leaderboard.html'
    driver.get(url)
    time.sleep(10)  # 페이지 완전히 로딩될 때까지 대기
    driver.save_screenshot("pga_leaderboard.png")
    driver.quit()

    # 이미지 전처리: 흑백, 확대, 선명도 조절
    image = Image.open("pga_leaderboard.png")
    image = image.convert('L')  # 흑백으로 변환
    image = image.resize((image.width * 2, image.height * 2))  # 2배 확대
    image = ImageEnhance.Sharpness(image).enhance(2.0)  # 선명도 강화

    # OCR 실행 (Tesseract 설정 옵션 추가)
    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng', config=config)

    # GitHub Actions 로그에 OCR 인식 결과 전체 출력 (디버깅용)
    print("\n--- OCR RAW TEXT START ---\n")
    print(text)
    print("\n--- OCR RAW TEXT END ---\n")

    # 임성재의 OCR로 인식되는 표기를 위한 대상 선수 목록
    players = ['S. Im', 'S Im']

    # 1. 선두 선수 정보 추출 (예: 1위 혹은 T1로 시작하는 줄)
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
            # 이름이 두 단어로 되어있으면 합침 (예: "T1 S. Scheffler")
            name = f"{parts[1]} {parts[2]}" if len(parts) >= 3 and '.' in parts[1] else parts[1]
            score = parts[3]
            leader_text = f"{name} : {rank}위({score})"
        except Exception as e:
            leader_text = leader_line

    # 2. 소속 선수 (임성재) 성적 추출
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
                except Exception as e:
                    player_results.append(f"{player} : {line.strip()}")

    # 3. 최종 텔레그램 메시지 구성
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

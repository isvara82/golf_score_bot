import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageEnhance
import pytesseract

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

def run_bot():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,3000')

    driver = webdriver.Chrome(options=options)

    url = 'https://www.pgatour.com/leaderboard.html'
    driver.get(url)
    time.sleep(10)
    driver.save_screenshot("pga_leaderboard.png")
    driver.quit()

    image = Image.open("pga_leaderboard.png")
    image = image.convert('L')  # 흑백
    image = image.resize((image.width * 2, image.height * 2))
    image = ImageEnhance.Sharpness(image).enhance(2.0)

    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng', config=config)

    players = ['S. Im', 'S Im']
    message_lines = []

    # 1. 선두 찾기 (1위 혹은 T1, T2부터 시작)
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

    # 2. 소속 선수 성적 찾기
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

    # 3. 최종 메시지 구성
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
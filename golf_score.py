import os
import cv2
import pytesseract
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 소속 선수 목록
MY_PLAYERS = {
    "임성재": "S. Im",
    "양희영": "Amy Yang",
    "황유민": "황유민",
    "장유빈": "Yubin Jang",
    "황중곤": "황중곤",
    "이수민": "이수민",
    "이태훈": "Taehoon LEE",
    "김승민": "김승민",
    "김현욱": "김현욱",
    "최준희": "최준희",
}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=data)

def format_score_line(rank: str, name: str, score: str):
    return f"{name} : {rank}위({score})"

def parse_ocr_lines(text):
    lines = text.splitlines()
    results = []
    for line in lines:
        line = line.strip()
        if not line or "PLAYER" in line or "POS" in line:
            continue
        parts = line.split()
        if len(parts) >= 3:
            try:
                rank = parts[0].replace("S", "5").replace("T", "T")
                name = " ".join(parts[1:-2])
                score_raw = parts[-3]
                score = score_raw if score_raw.startswith(("-", "+")) else "-" + score_raw
                results.append((rank, name, score))
            except Exception as e:
                print(f"파싱 실패: {line} → {e}")
    return results

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
    driver.set_window_size(1920, 1080)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(BytesIO(screenshot))
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    text = pytesseract.image_to_string(thresh, lang="eng")

    # OCR 결과 디버깅 출력
    print("===== OCR 원문 =====")
    print(text)

    # 로그 저장
    with open("ocr_log.txt", "w", encoding="utf-8") as f:
        f.write(text)

    parsed = parse_ocr_lines(text)

    my_lines = []
    for kor_name, eng_name in MY_PLAYERS.items():
        for rank, name, score in parsed:
            if eng_name in name:
                my_lines.append(format_score_line(rank, kor_name, score))
                break

    leader_line = parsed[0] if parsed and isinstance(parsed[0], tuple) and len(parsed[0]) == 3 else None
    leader_str = format_score_line(*leader_line) if leader_line else "정보 없음"

    message = "■ PGA 투어 성적\n\n[소속 선수]\n"
    message += "\n".join(my_lines) if my_lines else "해당 없음"
    message += f"\n\n[선두 선수]\n{leader_str}"

    send_telegram_message(message)

if __name__ == "__main__":
    run_bot()
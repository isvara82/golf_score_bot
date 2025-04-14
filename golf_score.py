import os
import requests
from bs4 import BeautifulSoup

# 텔레그램 설정
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 소속 선수 목록
players = [
    '황중곤', '이수민', '이태훈', '김승민', '김현욱', '최준희',
    'Taehoon LEE'
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

def run_bot():
    # KPGA 실제 성적 페이지 (iframe 내부 주소)
    url = 'https://www.kpga.co.kr/tours/game/score/?tourId=11&year=2025&gameId=202511000002M'

    # headers에 Referer 필수
    headers = {
        "Referer": "https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2025&gameId=202511000002M&type=leaderboard",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        send_telegram(f"[KPGA 성적 알림]\n\n데이터 요청 실패: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select('table.score_table tbody tr')

    if not rows:
        send_telegram("[KPGA 성적 알림]\n\n리더보드 테이블이 비어있습니다.")
        return

    leader_info = ''
    player_infos = []

    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 8:
            continue

        rank = cols[0].text.strip()
        name = cols[2].text.strip()
        score = cols[7].text.strip()

        if i == 0:
            leader_info = f"{name} : {rank}위({score})"

        for p in players:
            if p in name:
                player_infos.append(f"{name} : {rank}위({score})")

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

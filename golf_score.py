import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# 환경변수에서 토큰과 챗 ID 읽기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ✅ 선수 목록 (영문 이름 → 한글 이름)
MY_PLAYERS = {
    # PGA
    "Sungjae Im": "임성재",

    # LPGA
    "Amy Yang": "양희영",

    # KLPGA
    "Yumin Hwang": "황유민",

    # KPGA
    "Taehoon Lee": "이태훈",
    "Junggon Hwang": "황중곤",
    "Soomin Lee": "이수민",
    "Seungmin Kim": "김승민",
    "Hyunwook Kim": "김현욱",
    "Joonhee Choi": "최준희",

    # LIV
    "Yubin Jang": "장유빈"
}

# ✅ PGA 리더보드 크롤링
def get_pga_leaderboard():
    url = 'https://www.espn.com/golf/leaderboard/_/tour/pga'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        leaderboard = []
        rows = soup.select('table tbody tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            position = cols[0].text.strip()
            name = cols[1].text.strip()
            score = cols[2].text.strip()
            leaderboard.append({'name': name, 'score': score, 'position': position})
        return leaderboard
    except Exception as e:
        print(f"PGA 크롤링 실패: {e}")
        return []

# ✅ KLPGA 리더보드 크롤링 (※ 매 대회 URL 자동 추적이 필요할 수 있음. 현재는 기본 페이지로 접근)
def get_klpga_leaderboard():
    url = "https://www.klpga.co.kr/web/tour/score/leaderboard.do"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        leaderboard = []
        rows = soup.select("table tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            position = cols[0].text.strip()
            name = cols[1].text.strip()
            score = cols[3].text.strip()
            leaderboard.append({'name': name, 'score': score, 'position': position})
        return leaderboard
    except Exception as e:
        print(f"KLPGA 크롤링 실패: {e}")
        return []

# ✅ 공통 메시지 포맷 함수
def format_message(leaderboard, tour_name):
    if not leaderboard:
        return f"{tour_name} 리더보드를 불러올 수 없습니다."

    message = f"⛳️ [{tour_name} 투어 성적 요약]\n\n"
    leader = leaderboard[0]
    message += f"🏆 선두: {leader['name']} ({leader['score']}) - {leader['position']}위\n"

    my_players_data = []
    for p in leaderboard:
        for eng_name, kor_name in MY_PLAYERS.items():
            if eng_name.lower() in p['name'].lower() or kor_name in p['name']:
                my_players_data.append({
                    'name': kor_name,
                    'score': p['score'],
                    'position': p['position']
                })

    if my_players_data:
        message += "\n⭐️ 우리 소속 선수 성적:\n"
        for player in my_players_data:
            message += f"{player['name']} - {player['score']} ({player['position']}위)\n"
    else:
        message += "\n(우리 소속 선수는 현재 리더보드에 없습니다.)"

    return message

# ✅ 텔레그램 메시지 전송
def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print("✅ 메시지 전송 성공")
    except Exception as e:
        print(f"❌ 메시지 전송 실패: {str(e)}")

# ✅ 메인 실행
if __name__ == "__main__":
    print("⛳️ 골프 투어 성적 봇 실행 시작")

    # PGA
    pga_data = get_pga_leaderboard()
    pga_message = format_message(pga_data, "PGA")

    # KLPGA
    klpga_data = get_klpga_leaderboard()
    klpga_message = format_message(klpga_data, "KLPGA")

    # 메시지 통합
    full_message = pga_message + "\n\n" + klpga_message
    send_telegram_message(full_message)

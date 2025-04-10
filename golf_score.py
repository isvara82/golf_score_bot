import os
import requests
from telegram import Bot

# 🟢 환경 변수
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")

# 🟢 RapidAPI 설정
HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
}

# 🎯 소속 선수 (영문 기준)
MY_PLAYERS = {
    "Sungjae Im": "임성재",
    "Si Woo Kim": "김시우",
    "Tom Kim": "김주형",
    # 필요한 선수 추가
}

# ✅ 현재 토너먼트 ID 추출
def get_current_tournament_id():
    url = "https://live-golf-data.p.rapidapi.com/tournaments"
    res = requests.get(url, headers=HEADERS)
    data = res.json()

    for t in data.get("tournaments", []):
        if t.get("status") == "In Progress":
            return t.get("id")
    return None

# ✅ 리더보드 불러오기
def get_leaderboard(tournament_id):
    url = f"https://live-golf-data.p.rapidapi.com/leaderboard?tournamentId={tournament_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json().get("leaderboard", [])

# ✅ 메시지 구성
def format_message(leaderboard):
    if not leaderboard:
        return "PGA 리더보드를 불러올 수 없습니다."

    message = "⛳️ [PGA 투어 성적 요약]\n"

    # 선두
    leader = leaderboard[0]
    message += f"🏆 선두: {leader['name']} : {leader['rank']}위({leader['total']})\n"

    # 소속 선수
    my = [p for p in leaderboard if p["name"] in MY_PLAYERS]
    if my:
        message += "\n⭐️ 소속 선수:\n"
        for p in my:
            message += f"{MY_PLAYERS[p['name']]} : {p['rank']}위({p['total']})\n"
    else:
        message += "\n(소속 선수 없음)"

    return message

# ✅ 텔레그램 전송
def send_telegram_message(text):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        except Exception as e:
            print("텔레그램 전송 실패:", e)
    else:
        print("텔레그램 설정 오류")

# ✅ 실행
if __name__ == "__main__":
    tid = get_current_tournament_id()
    if tid:
        leaderboard = get_leaderboard(tid)
        msg = format_message(leaderboard)
    else:
        msg = "현재 진행 중인 PGA 대회가 없습니다."

    print(msg)
    send_telegram_message(msg)

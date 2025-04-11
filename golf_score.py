import os
import requests
from telegram import Bot
from datetime import datetime, timedelta

# 환경 변수
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")

HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
}

MY_PLAYERS = {
    "Sungjae Im": "임성재",
    "Si Woo Kim": "김시우",
    "Tom Kim": "김주형"
}

# 한국 시간 변환
def utc_to_kst(utc_str):
    utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
    return (utc_time + timedelta(hours=9)).strftime("%H:%M")

# 현재 PGA 대회 정보 가져오기
def get_current_tournament():
    url = "https://live-golf-data.p.rapidapi.com/tournaments"
    res = requests.get(url, headers=HEADERS)
    for t in res.json().get("tournaments", []):
        if t["orgId"] == 1 and t["status"] in ["Scheduled", "In Progress"]:
            return t
    return None

# 성적 메시지 생성
def format_score_message(tournament_id, tournament_name):
    url = f"https://live-golf-data.p.rapidapi.com/leaderboard?tournamentId={tournament_id}"
    res = requests.get(url, headers=HEADERS)
    data = res.json().get("leaderboard", [])

    if not data:
        return "PGA 리더보드를 불러올 수 없습니다."

    msg = f"⛳️ [PGA 투어 성적 요약 - {tournament_name}]\n"
    leader = data[0]
    msg += f"🏆 선두: {leader['name']} : {leader['rank']}위({leader['total']})\n"

    my_players = [p for p in data if p["name"] in MY_PLAYERS]
    if my_players:
        msg += "\n⭐️ 소속 선수:\n"
        for p in my_players:
            msg += f"{MY_PLAYERS[p['name']]} : {p['rank']}위({p['total']})\n"
    else:
        msg += "\n(소속 선수 없음)"
    return msg

# 티오프 메시지 생성
def format_tee_time_message(tournament_id, tournament_name, start_date, end_date):
    url = f"https://live-golf-data.p.rapidapi.com/teeTimes?tournamentId={tournament_id}"
    res = requests.get(url, headers=HEADERS)
    tee_times = res.json().get("teeTimes", [])

    msg = f"⛳️ [PGA 티오프 알림 - {tournament_name}]\n"
    msg += f"📅 일정: {start_date} ~ {end_date}\n\n"
    msg += "🕒 소속 선수 티오프 시간 (Round 1)\n"

    found = False
    for tee in tee_times:
        if tee["round"] != 1:
            continue
        names = [p["name"] for p in tee["players"]]
        for name in names:
            if name in MY_PLAYERS:
                found = True
                others = [MY_PLAYERS.get(n, n) for n in names if n != name]
                msg += f"- {MY_PLAYERS[name]}: {utc_to_kst(tee['teeTime'])} (KST) - [{', '.join(others)}]\n"
    if not found:
        msg += "(소속 선수 티오프 정보 없음)"
    return msg

# 텔레그램 메시지 전송
def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print("텔레그램 전송 실패:", e)

# 메인 실행
if __name__ == "__main__":
    t = get_current_tournament()
    if t:
        tid = t["id"]
        name = t["name"]
        status = t["status"]

        if status == "Scheduled":
            msg = format_tee_time_message(tid, name, t["startDate"], t["endDate"])
        elif status == "In Progress":
            msg = format_score_message(tid, name)
        else:
            msg = "알 수 없는 대회 상태입니다."
    else:
        msg = "현재 예정되거나 진행 중인 PGA 대회가 없습니다."

    print(msg)
    send_telegram_message(msg)

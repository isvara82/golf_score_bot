import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 한글 이름 매핑
MY_PLAYERS = {
    # PGA
    "Sungjae Im": "임성재",

    # LPGA
    "Amy Yang": "양희영",

    # KPGA (정렬 순서 적용)
    "Taehoon Lee": "이태훈",
    "Junggon Hwang": "황중곤",
    "Soomin Lee": "이수민",
    "Seungmin Kim": "김승민",
    "Wooyoung Cho": "조우영",
    "Hyunwook Kim": "김현욱",
    "Joonhee Choi": "최준희",

    # KLPGA
    "Yumin Hwang": "황유민",

    # LIV
    "Yubin Jang": "장유빈"
}

# ----------- 각 투어별 리더보드 함수 -----------

[함수 생략: 동일 유지]

# ----------- 메시지 포맷 공통 함수 -----------

def format_message(leaderboard, tour_name):
    if not leaderboard:
        return f"⛳️ [{tour_name} 투어 성적 요약]\n\n리더보드를 불러올 수 없습니다."

    message = f"⛳️ [{tour_name} 투어 성적 요약]\n\n"
    leader = leaderboard[0]
    leader_name = MY_PLAYERS.get(leader['name'], leader['name'])
    message += f"🏆 선두: {leader_name} : {leader['position']}위({leader['score']})\n"

    my_players_data = []
    for eng_name, kor_name in MY_PLAYERS.items():
        for p in leaderboard:
            if eng_name.lower() in p['name'].lower() or kor_name in p['name']:
                my_players_data.append({
                    'name': kor_name,
                    'score': p['score'],
                    'position': p['position']
                })
                break

    if my_players_data:
        message += "\n⭐️ 소속 선수:\n"
        for player in my_players_data:
            message += f"{player['name']} : {player['position']}위({player['score']})\n"
    else:
        message += "\n(우리 소속 선수는 현재 리더보드에 없습니다.)"

    return message

# ----------- 실행 -----------

def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")

if __name__ == "__main__":
    all_messages = []

    # PGA
    pga = get_pga_leaderboard()
    all_messages.append(format_message(pga, "PGA"))

    # LPGA
    lpga = get_lpga_leaderboard()
    all_messages.append(format_message(lpga, "LPGA"))

    # KPGA
    kpga = get_kpga_leaderboard()
    all_messages.append(format_message(kpga, "KPGA"))

    # KLPGA
    klpga = get_klpga_leaderboard()
    all_messages.append(format_message(klpga, "KLPGA"))

    # LIV
    liv = get_liv_leaderboard()
    all_messages.append(format_message(liv, "LIV"))

    # Asian Tour
    asian = get_asian_tour_leaderboard()
    all_messages.append(format_message(asian, "아시안투어"))

    final_message = "\n\n------------------------------\n\n".join(all_messages)
    send_telegram_message(final_message)

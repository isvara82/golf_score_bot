import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# 텔레그램 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 소속 선수: 영어이름 → 한글이름 매핑
MY_PLAYERS = {
    "Taehoon Lee": "이태훈",
    "Junggon Hwang": "황중곤",
    "Soomin Lee": "이수민",
    "Seungmin Kim": "김승민",
    "Wooyoung Cho": "조우영",
    "Hyunwook Kim": "김현욱",
    "Joonhee Choi": "최준희"
}

# KPGA 리더보드 크롤링
def get_kpga_leaderboard():
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
    try:
        # 대회 ID 자동 추출
        main_url = "https://kpga.co.kr/tour/scores/score"
        res = requests.get(main_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        script = soup.find("script", string=lambda t: t and 'gameId' in t)
        import re
        match = re.search(r'gameId\":\"(\d+)', script.text) if script else None
        game_id = match.group(1) if match else "2024050002"
    except Exception as e:
        print("KPGA 대회 ID 추출 실패", e)
        game_id = "2024050002"

    # JSON 요청
    payload = {
        "gameId": game_id,
        "round": "2",
        "tourId": "11",
        "season": "2024"
    }
    url = "https://kpga.co.kr/api/v1/scores/scoreResultList"

    try:
        res = requests.post(url, json=payload, headers=headers)
        data = res.json().get("result", [])
        leaderboard = []
        for player in data:
            leaderboard.append({
                "name": player.get("playerName", ""),
                "position": player.get("rank", ""),
                "score": player.get("totalScore", "")
            })
        return leaderboard
    except Exception as e:
        print("KPGA JSON 요청 실패:", e)
        return []

# 메시지 포맷 구성
def format_kpga_message(leaderboard):
    if not leaderboard:
        return "KPGA 리더보드를 불러올 수 없습니다."

    message = "⛳️ [KPGA 투어 성적 요약]\n"

    leader = leaderboard[0]
    message += f"🏆 선두: {leader['name']} : {leader['position']}위({leader['score']})\n"

    my_players = [p for p in leaderboard if p['name'] in MY_PLAYERS]
    if my_players:
        message += "\n⭐️ 소속 선수:\n"
        for player in my_players:
            name_kor = MY_PLAYERS[player['name']]
            message += f"{name_kor} : {player['position']}위({player['score']})\n"
    else:
        message += "\n(소속 선수 성적 없음)"

    return message

# 텔레그램 전송
def send_telegram_message(text):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        except Exception as e:
            print("텔레그램 전송 실패:", e)
    else:
        print("TELEGRAM_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")

# 테스트 실행
if __name__ == "__main__":
    data = get_kpga_leaderboard()
    message = format_kpga_message(data)
    print(message)  # 콘솔 출력
    send_telegram_message(message)  # 텔레그램 전송

import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ✅ 이름 매핑: 영어 이름 → 한글 이름
MY_PLAYERS = {
    "Sungjae Im": "임성재",
    "Yubin Jang": "장유빈",
    "Amy Yang": "양희영",
    "Taehoon Lee": "이태훈",
    "Junggon Hwang": "황중곤",
    "Soomin Lee": "이수민",
    "Seungmin Kim": "김승민",
    "Hyunwook Kim": "김현욱",
    "Joonhee Choi": "최준희"
}

def get_pga_leaderboard():
    url = 'https://www.espn.com/golf/leaderboard/_/tour/pga'
    headers = {'User-Agent': 'Mozilla/5.0'}
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

def format_message(leaderboard):
    if not leaderboard:
        return "PGA 리더보드를 불러올 수 없습니다."

    message = "⛳️ [PGA 투어 성적 요약]\n\n"

    # 🏆 선두 선수 (그대로 표시)
    leader = leaderboard[0]
    message += f"🏆 선두: {leader['name']} ({leader['score']}) - {leader['position']}위\n"

    # ⭐️ 우리 선수 찾기
    my_players_data = []
    for p in leaderboard:
        for eng_name, kor_name in MY_PLAYERS.items():
            if eng_name.lower() in p['name'].lower():
                player_data = {
                    'name': kor_name,  # 출력은 한글로
                    'score': p['score'],
                    'position': p['position']
                }
                my_players_data.append(player_data)

    if my_players_data:
        message += "\n⭐️ 우리 소속 선수 성적:\n"
        for player in my_players_data:
            message += f"{player['name']} - {player['score']} ({player['position']}위)\n"
    else:
        message += "\n(우리 소속 선수는 현재 리더보드에 없습니다.)"

    return message

def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print("✅ 메시지 전송 성공")
    except Exception as e:
        print(f"❌ 메시지 전송 실패: {str(e)}")

if __name__ == "__main__":
    leaderboard = get_pga_leaderboard()
    message = format_message(leaderboard)
    send_telegram_message(message)

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

def get_lpga_leaderboard():
    url = "https://www.lpga.com/tournaments"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        link_tag = soup.select_one("a.tournament-leaderboard")
        if not link_tag:
            return []
        leaderboard_url = "https://www.lpga.com" + link_tag.get("href")
        res2 = requests.get(leaderboard_url, headers=headers)
        soup2 = BeautifulSoup(res2.content, "html.parser")
        rows = soup2.select("table.leaderboard-table tbody tr")
        leaderboard = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            position = cols[0].text.strip()
            name = cols[1].text.strip()
            score = cols[2].text.strip()
            leaderboard.append({'name': name, 'score': score, 'position': position})
        return leaderboard
    except Exception as e:
        print(f"LPGA 크롤링 실패: {e}")
        return []

def get_kpga_leaderboard():
    url = "https://kpga.co.kr/tour/schedule/kpga-tour"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        link_tag = soup.select_one(".table_list .txt_left a")
        if not link_tag:
            return []
        leaderboard_url = "https://kpga.co.kr" + link_tag.get("href")
        res2 = requests.get(leaderboard_url, headers=headers)
        soup2 = BeautifulSoup(res2.content, "html.parser")
        rows = soup2.select("table tbody tr")
        leaderboard = []
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
        print(f"KPGA 크롤링 실패: {e}")
        return []

def get_klpga_leaderboard_url():
    url = "https://www.klpga.co.kr/web/tour/tournament/ongoing.do"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        link_tag = soup.select_one("div.tbl_wrap tbody tr td.tit a")
        if link_tag:
            return f"https://www.klpga.co.kr{link_tag.get('href')}"
    except Exception as e:
        print(f"KLPGA 대회 URL 추적 실패: {e}")
    return "https://klpga.co.kr/web/leaderboard/leaderboard"

def get_klpga_leaderboard():
    url = get_klpga_leaderboard_url()
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select("table.score tbody tr")
        leaderboard = []
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

def get_liv_leaderboard():
    url = "https://www.livgolf.com/leaderboard"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        rows = soup.select("table tbody tr")
        leaderboard = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            position = cols[0].text.strip()
            name = cols[1].text.strip()
            score = cols[3].text.strip()
            leaderboard.append({'name': name, 'score': score, 'position': position})
        return leaderboard
    except Exception as e:
        print(f"LIV 크롤링 실패: {e}")
        return []

def get_asian_tour_leaderboard():
    url = "https://asiantour.com/results"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        link_tag = soup.select_one(".results-tournaments a")
        if not link_tag:
            return []
        leaderboard_url = "https://asiantour.com" + link_tag.get("href")
        res2 = requests.get(leaderboard_url, headers=headers)
        soup2 = BeautifulSoup(res2.content, "html.parser")
        rows = soup2.select("table tbody tr")
        leaderboard = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            position = cols[0].text.strip()
            name = cols[1].text.strip()
            score = cols[3].text.strip()
            leaderboard.append({'name': name, 'score': score, 'position': position})
        return leaderboard
    except Exception as e:
        print(f"아시안투어 크롤링 실패: {e}")
        return []

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

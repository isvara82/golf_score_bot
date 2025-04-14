import requests
from bs4 import BeautifulSoup
import telegram # pip install python-telegram-bot~=20.11 (버전 확인 필요)
import asyncio
import os
# from dotenv import load_dotenv # .env 파일은 더 이상 사용하지 않으므로 이 줄 삭제 또는 주석 처리

# .env 파일 로드 부분 삭제 또는 주석 처리
# load_dotenv()

# --- 설정 ---
# GitHub Actions Secrets에서 설정한 이름과 동일한 환경 변수 이름을 사용합니다.
# os.getenv('환경변수명') 방식으로 값을 가져옵니다.
# GitHub Actions 환경에서 실행되면 해당 Secret 값이 자동으로 환경 변수에 할당됩니다.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 아래는 나머지 코드 (스크래핑, 텔레그램 전송 등) - 변경 없음
TARGET_URL = 'https://www.kpga.co.kr/tours/game/game/?tourId=11&year=2024&gameId=202411000008M&type=result'
MANAGED_KPGA_PLAYERS = ['황중곤', '이태훈', '이수민', '김승민', '김현욱']

# --- 텔레그램 메시지 발송 함수 (비동기) ---
async def send_telegram_message(bot_token, chat_id, message):
    """지정된 채팅 ID로 텔레그램 메시지를 비동기적으로 보냅니다."""
    if not bot_token or not chat_id:
        print("오류: 텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다. (환경 변수 확인)")
        return
    bot = telegram.Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown') # Markdown 사용 가능
        print(f"텔레그램 메시지 발송 성공!")
    except Exception as e:
        print(f"텔레그램 메시지 발송 실패: {e}")

# --- KPGA 결과 페이지 스크래핑 함수 ---
def fetch_kpga_results(url, managed_players):
    # ... (이전 코드와 동일 - 웹사이트 구조에 맞게 선택자 확인 필요) ...
    results = {
        'tournament_name': '대회명을 찾을 수 없음',
        'winner': '우승자 정보를 찾을 수 없음',
        'managed_players_results': []
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        print(f"데이터 가져오는 중: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 대회명 추출 (### <<< 확인 필요 (1) >>> ###)
        title_element = soup.select_one('div.subTop > h2') # 예시 Selector
        if title_element:
            results['tournament_name'] = title_element.text.strip()
        else:
            print("대회명 요소를 찾지 못했습니다.")

        # 2. 결과 테이블 분석 (### <<< 확인 필요 (2) >>> ###)
        result_table = soup.select_one('div.leaderBoard > table.listTable') # 예시 Selector
        if not result_table:
            print("결과 테이블을 찾지 못했습니다.")
            return results

        rows = result_table.select('tbody > tr')
        if not rows:
            print("테이블에 데이터 row가 없습니다.")
            return results

        # 3. 각 Row 순회 (### <<< 확인 필요 (3) - 컬럼 인덱스 >>> ###)
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue

            try:
                rank = cols[0].text.strip()
                player_name_tag = cols[1].find('a')
                player_name = player_name_tag.text.strip() if player_name_tag else cols[1].text.strip()
                total_score_index = 8  ### <<< 이 인덱스(8)가 맞는지 반드시 확인! >>> ###
                if len(cols) > total_score_index:
                    total_score = cols[total_score_index].text.strip()
                else:
                    total_score = 'N/A'

                if rank in ['1', 'T1'] and results['winner'] == '우승자 정보를 찾을 수 없음':
                    results['winner'] = f"{player_name} ({total_score})"

                if player_name in managed_players:
                    player_result = f"{player_name}: {rank}위 ({total_score})"
                    results['managed_players_results'].append(player_result)

            except Exception as e:
                print(f"Row 처리 중 오류: {e}, Row: {row.text.strip()}")
                continue
        return results

    except Exception as e:
        print(f"스크래핑/처리 중 오류 발생: {e}")
        return results


# --- 메인 실행 로직 ---
async def main():
    # 환경 변수에서 토큰/ID 가져왔는지 간단히 확인
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("오류: GitHub Actions Secrets에 TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았거나 스크립트로 전달되지 않았습니다.")
        return

    print("스크립트 시작...")
    scraped_data = fetch_kpga_results(TARGET_URL, MANAGED_KPGA_PLAYERS)

    # 텔레그램 메시지 포맷팅
    message = f"*{scraped_data['tournament_name']} 결과 알림 (Actions)*\n\n" # 제목에 Actions 추가
    message += f"- 우승: {scraped_data['winner']}\n\n"
    message += "*소속 선수 결과:*\n"
    if scraped_data['managed_players_results']:
        for result in scraped_data['managed_players_results']:
            message += f"- {result}\n"
    else:
        message += "- 해당 대회 결과에서 소속 선수를 찾지 못했습니다.\n"
    message += f"\n[상세 결과 보기]({TARGET_URL})"

    print("\n--- 보낼 메시지 ---")
    print(message)
    print("------------------")

    # 텔레그램 메시지 발송
    await send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
    print("스크립트 완료.")

if __name__ == "__main__":
    asyncio.run(main())

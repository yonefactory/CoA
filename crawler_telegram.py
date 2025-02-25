import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import os

# 🔹 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your-chat-id")

# 🔹 크롤링할 URL
url = 'https://9to5mac.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 🔹 지난번에 보낸 기사 목록 로드
SENT_ARTICLES_FILE = "sent_articles.json"
if os.path.exists(SENT_ARTICLES_FILE):
    with open(SENT_ARTICLES_FILE, "r", encoding="utf-8") as f:
        sent_articles = json.load(f)
else:
    sent_articles = []

def extract_article_summary(article_url):
    """기사 본문을 가져와 3줄 요약 후 한국어 번역"""
    try:
        article_response = requests.get(article_url, headers=headers)
        if article_response.status_code != 200:
            return "기사 내용을 가져오지 못했습니다."

        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        paragraphs = article_soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()

        # 3줄 요약 (간단한 방식)
        sentences = text.split('. ')
        summary = ". ".join(sentences[:3]) + "."

        # 한국어 번역 (Google Translate API 사용)
        translated_summary = translate_to_korean(summary)
        return translated_summary
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

def translate_to_korean(text):
    """Google Translate API를 사용하여 한국어 번역"""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ko",
        "dt": "t",
        "q": text
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            translated_text = response.json()[0][0][0]
            return translated_text
        else:
            return "번역 오류 발생."
    except Exception as e:
        return f"번역 중 오류 발생: {e}"

def send_telegram_message(message):
    """텔레그램 메시지 전송"""
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(telegram_api_url, json=payload)
    return response.status_code

if __name__ == "__main__":
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = []
        for article in soup.find_all('article'):
            title_tag = article.find('h2')
            if title_tag and title_tag.a:
                title = title_tag.a.get_text(strip=True)
                link = title_tag.a['href']
                summary = extract_article_summary(link)
                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": link
                })

        # ✅ 새로운 기사 필터링
        new_articles = [a for a in articles if a["link"] not in sent_articles]

        if new_articles:
            # 🔹 새로운 기사 전송
            for article in new_articles:
                message = f"*{article['title']}*\n\n_{article['summary']}_\n\n[🔗 기사 보기]({article['link']})"
                send_telegram_message(message)
                sent_articles.append(article["link"])
            print(f"✅ {len(new_articles)}개의 새 기사를 텔레그램으로 전송했습니다.")
        else:
            # 🔹 새로운 기사가 없으면 최신 기사 1개 전송
            if articles:
                latest_article = articles[0]  # 최신 기사 1개 선택
                message = f"📢 새로운 기사가 없습니다. 대신 최신 기사 공유합니다:\n\n*{latest_article['title']}*\n\n_{latest_article['summary']}_\n\n[🔗 기사 보기]({latest_article['link']})"
                send_telegram_message(message)
                print("✅ 새로운 기사가 없어 최신 기사를 보냈습니다.")
            else:
                send_telegram_message("📢 새로운 기사가 없습니다. (사이트에 기사가 없음)")
                print("✅ 새로운 기사가 없어 '새로운 기사가 없습니다' 메시지를 보냈습니다.")

        # ✅ 보낸 기사 목록 저장 (중복 방지)
        with open(SENT_ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(sent_articles, f, indent=4)

    else:
        print(f"❌ Failed to retrieve the page. Status code: {response.status_code}")

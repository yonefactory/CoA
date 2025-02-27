import requests
from bs4 import BeautifulSoup
import json
import re
import os

# 🔹 환경 변수 로드
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🔹 개인 및 그룹 챗방 ID 불러오기
TELEGRAM_CHAT_IDS = [
    os.getenv("TELEGRAM_CHAT_ID"),
    os.getenv("TELEGRAM_CHAT_ID_GROUP"),
]

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
    """기사 본문을 가져와 3~5줄 요약 후 한국어 번역"""
    try:
        article_response = requests.get(article_url, headers=headers)
        if article_response.status_code != 200:
            return "기사 내용을 가져오지 못했습니다."

        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        paragraphs = article_soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()

        # 3~5줄 요약 (문장 단위로 3~5개 선택)
        sentences = text.split('. ')
        summary_sentences = sentences[:5]  # 최대 5문장 선택
        summary = "\n".join([f"• {sentence.strip()}." for sentence in summary_sentences])

        # 한국어 번역 (DeepL API 사용)
        translated_summary = translate_to_korean(summary)
        return translated_summary
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

def translate_to_korean(text):
    """DeepL API를 사용하여 한국어 번역"""
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": "KO"
    }
    try:
        response = requests.post(url, data=params)
        if response.status_code == 200:
            translated_text = response.json()["translations"][0]["text"]
            return translated_text
        else:
            return "번역 오류 발생."
    except Exception as e:
        return f"번역 중 오류 발생: {e}"

def send_telegram_message(message):
    """개인 및 그룹 챗방으로 메시지 전송"""
    for chat_id in TELEGRAM_CHAT_IDS:
        if chat_id:  # 빈 값이 아닐 경우 전송
            telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(telegram_api_url, json=payload)

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
            # ✅ 새로운 기사가 없으면 "📢 새로운 기사가 없습니다." 메시지만 전송
            send_telegram_message("📢 새로운 기사가 없습니다.")
            print("✅ 새로운 기사가 없어 '새로운 기사가 없습니다' 메시지를 보냈습니다.")

        # ✅ 보낸 기사 목록 저장 (중복 방지)
        with open(SENT_ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(sent_articles, f, indent=4)

    else:
        print(f"❌ Failed to retrieve the page. Status code: {response.status_code}")

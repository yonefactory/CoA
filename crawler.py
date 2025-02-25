import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# User-Agent 추가 (차단 방지)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 크롤링할 URL
url = 'https://9to5mac.com/'
response = requests.get(url, headers=headers)

def extract_article_summary(article_url):
    """ 기사 본문을 가져와 3줄 요약 반환 """
    try:
        article_response = requests.get(article_url, headers=headers)
        if article_response.status_code != 200:
            return "기사 내용을 가져오지 못했습니다."

        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        # 본문 텍스트 추출
        paragraphs = article_soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])

        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()

        # 3줄 요약 (간단한 방식, 필요시 AI 모델 활용 가능)
        sentences = text.split('. ')
        summary = ". ".join(sentences[:3]) + "."

        return summary
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for article in soup.find_all('article'):
        title_tag = article.find('h2')
        if title_tag and title_tag.a:
            title = title_tag.a.get_text(strip=True)
            link = title_tag.a['href']

            # 기사 본문 요약 추가
            summary = extract_article_summary(link)

            articles.append({
                "title": title,
                "summary": summary,
                "link": link
            })

    # JSON 파일 저장
    scraped_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "articles": articles
    }

    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)

    print(f"✅ {len(articles)} articles scraped successfully.")
else:
    print(f"❌ Failed to retrieve the page. Status code: {response.status_code}")

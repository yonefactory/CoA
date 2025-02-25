import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 크롤링할 URL 설정
url = 'https://9to5mac.com/'

# 웹 페이지 요청
response = requests.get(url)
if response.status_code == 200:
    # 페이지 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 기사 제목과 링크 추출
    articles = []
    for article in soup.find_all('h2', class_='post-title'):
        title = article.get_text(strip=True)
        link = article.find('a')['href']
        articles.append({"title": title, "link": link})

    # JSON 파일로 저장
    scraped_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "articles": articles
    }

    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
    
    print("Scraping successful. Data saved to scraped_data.json.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

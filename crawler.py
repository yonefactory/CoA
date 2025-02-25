import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

url = 'https://9to5mac.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # 🔹 HTML 구조 확인 후 'h2.post-title' 대신 새로운 선택자로 변경
    articles = []
    for article in soup.find_all('article'):
        title_tag = article.find('h2')
        if title_tag and title_tag.a:
            title = title_tag.a.get_text(strip=True)
            link = title_tag.a['href']
            articles.append({"title": title, "link": link})

    # JSON 저장
    scraped_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "articles": articles
    }

    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)

    print(f"✅ {len(articles)} articles scraped successfully.")
else:
    print(f"❌ Failed to retrieve the page. Status code: {response.status_code}")

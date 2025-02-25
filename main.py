import requests
from bs4 import BeautifulSoup

# 크롤링할 URL 설정
url = 'https://9to5mac.com/'

# 웹 페이지 요청
response = requests.get(url)
if response.status_code == 200:
    # 페이지 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 예: 기사 제목 추출
    articles = soup.find_all('h2', class_='post-title')
    for article in articles:
        title = article.get_text(strip=True)
        link = article.find('a')['href']
        print(f'Title: {title}')
        print(f'Link: {link}')
else:
    print(f'Failed to retrieve the page. Status code: {response.status_code}')

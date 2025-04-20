import requests
from bs4 import BeautifulSoup
import json

url = "https://www.kead.or.kr/edsysdesc/cntntsPage.do?menuId=MENU0684"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

title = soup.title.string.strip()
content = soup.select_one("#contents").get_text(separator="\n").strip()

data = {
    "title": title,
    "body": content,
    "category": "지원금",
    "url": url,
    "embedding": None
}

with open("scripts/policies.json", "w", encoding="utf-8") as f:
    json.dump([data], f, ensure_ascii=False, indent=2)

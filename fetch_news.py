
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

RSS_URL = "https://www.chinanews.com.cn/rss/scroll-news.xml"

def fetch_news():
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "NewsHub/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = item.findtext("description", "").strip()

        if not title or not link:
            continue

        articles.append({
            "title": title,
            "link": link,
            "source": "中国新闻网",
            "category": "国内",
            "pubDate": pub_date,
            "description": description
        })

    os.makedirs("data", exist_ok=True)

    with open("data/news.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "articles": articles
            },
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"成功获取 {len(articles)} 条新闻")

if __name__ == "__main__":
    fetch_news()

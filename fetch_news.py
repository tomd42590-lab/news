
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import html
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# 新闻源：名称、RSS地址、网站分类
SOURCES = [
    # 国内新闻
    ("中国新闻网", "https://www.chinanews.com.cn/rss/china.xml", "国内"),

    # 国际新闻
    ("中国新闻网", "https://www.chinanews.com.cn/rss/world.xml", "国际"),

    # 经济新闻
    ("中国新闻网", "https://www.chinanews.com.cn/rss/finance.xml", "经济"),

    # 科技新闻
    ("新浪科技", "https://rss.sina.com.cn/news/allnews/tech.xml", "科技"),

    # 社会新闻
    ("中国新闻网", "https://www.chinanews.com.cn/rss/society.xml", "社会"),
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def get_tag(element, name):
    for child in element:
        if child.tag.split("}")[-1].lower() == name.lower():
            return child.text or ""
    return ""

def parse_date(value):
    if not value:
        return datetime.now(timezone.utc).isoformat()
    try:
        return parsedate_to_datetime(value).isoformat()
    except Exception:
        return value

def fetch_source(source_name, url, category):
    news_list = []

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 NewsHub/1.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            content = response.read()

        root = ET.fromstring(content)

        for item in root.iter():
            tag = item.tag.split("}")[-1].lower()

            if tag not in ("item", "entry"):
                continue

            title = clean_text(get_tag(item, "title"))
            link = get_tag(item, "link").strip()

            # 兼容 Atom 格式
            if not link:
                for child in item:
                    if child.tag.split("}")[-1].lower() == "link":
                        link = child.attrib.get("href", "")
                        break

            description = clean_text(
                get_tag(item, "description")
                or get_tag(item, "summary")
                or get_tag(item, "content")
            )

            pub_date = (
                get_tag(item, "pubDate")
                or get_tag(item, "published")
                or get_tag(item, "updated")
            )

            if not title or not link:
                continue

            news_list.append({
                "title": title,
                "link": link,
                "pubDate": parse_date(pub_date),
                "description": description[:300],
                "source": source_name,
                "category": category
            })

        print(f"成功：{source_name} - {category}，获取 {len(news_list)} 条")

    except Exception as e:
        print(f"失败：{source_name} - {category}：{e}")

    return news_list


def main():
    all_news = []
    seen_links = set()

    for source_name, url, category in SOURCES:
        news = fetch_source(source_name, url, category)

        for item in news:
            if item["link"] not in seen_links:
                seen_links.add(item["link"])
                all_news.append(item)

    # 按发布时间排序
    all_news.sort(
        key=lambda x: x["pubDate"],
        reverse=True
    )

    os.makedirs("data", exist_ok=True)

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

    print(f"\n采集完成！共获取 {len(all_news)} 条新闻")
    print("更新时间：", datetime.now().isoformat())


if __name__ == "__main__":
    main()

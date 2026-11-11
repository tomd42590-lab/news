
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import html
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# 新闻源：名称、RSS地址、分类
SOURCES = [
    ("中国新闻网", "https://www.chinanews.com.cn/rss/china.xml", "国内"),
    ("中国新闻网", "https://www.chinanews.com.cn/rss/world.xml", "国际"),
    ("中国新闻网", "https://www.chinanews.com.cn/rss/finance.xml", "经济"),

    # 科技新闻
    ("36氪", "https://36kr.com/feed", "科技"),
    ("IT之家", "https://www.ithome.com/rss/", "科技"),
    ("少数派", "https://sspai.com/feed", "科技"),

    ("中国新闻网", "https://www.chinanews.com.cn/rss/society.xml", "社会"),
]

# 新闻时效限制
MAX_AGE_DAYS = {
    "科技": 14,
    "默认": 30
}


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
        return ""

    value = value.strip()

    try:
        date = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
        except Exception:
            return ""

    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    return date.astimezone(timezone.utc).isoformat()


def is_recent(pub_date, category):
    try:
        published = datetime.fromisoformat(
            pub_date.replace("Z", "+00:00")
        )
    except Exception:
        return False

    now = datetime.now(timezone.utc)
    days = MAX_AGE_DAYS.get(
        category, MAX_AGE_DAYS["默认"]
    )

    return (
        now - timedelta(days=days)
        <= published
        <= now + timedelta(days=1)
    )


def fetch_source(source_name, url, category):
    news_list = []

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 NewsHub/1.0"
            }
        )

        with urllib.request.urlopen(
            request, timeout=25
        ) as response:
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
                or get_tag(item, "date")
            )

            published_at = parse_date(pub_date)

            if not title or not link or not published_at:
                continue

            # 过滤过期新闻
            if not is_recent(published_at, category):
                continue

            news_list.append({
                "title": title,
                "link": link,
                "pubDate": published_at,
                "description": description[:300],
                "source": source_name,
                "category": category
            })

        print(
            f"成功：{source_name} - {category}，"
            f"获取 {len(news_list)} 条新闻"
        )

    except Exception as e:
        print(f"失败：{source_name}：{e}")

    return news_list


def main():
    all_news = []
    seen_links = set()

    for source_name, url, category in SOURCES:
        news = fetch_source(
            source_name, url, category
        )

        for item in news:
            if item["link"] not in seen_links:
                seen_links.add(item["link"])
                all_news.append(item)

    # 按发布时间排序
    all_news.sort(
        key=lambda x: datetime.fromisoformat(
            x["pubDate"].replace("Z", "+00:00")
        ),
        reverse=True
    )

    os.makedirs("data", exist_ok=True)

    with open(
        "data/news.json", "w", encoding="utf-8"
    ) as f:
        json.dump(
            all_news,
            f,
            ensure_ascii=False,
            indent=2
        )

    tech_count = sum(
        1 for item in all_news
        if item["category"] == "科技"
    )

    print("\n采集完成！")
    print(f"新闻总数：{len(all_news)}")
    print(f"科技新闻：{tech_count}")
    print("更新时间：", datetime.now().isoformat())


if __name__ == "__main__":
    main()

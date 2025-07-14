from bs4 import BeautifulSoup

async def parse_news_page(session, news_id):
    item_url = f"https://news.ycombinator.com/item?id={news_id}"
    async with session.get(item_url) as resp:
        html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

    title_link = soup.select_one("a.storylink")
    news_url = title_link["href"] if title_link else None

    comment_links = []
    for link in soup.select("span.comment a"):
        href = link.get("href")
        if href and href.startswith("http"):
            comment_links.append(href)

    return news_url, comment_links

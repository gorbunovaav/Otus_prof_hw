import asyncio
import aiohttp
import os
from bs4 import BeautifulSoup
from utils import get_top_news_ids, download_and_save, ensure_dir
from parser import parse_news_page

BASE_URL = "https://news.ycombinator.com/"
INTERVAL = 60 
DATA_DIR = "data"
SEEN_IDS = set()

async def process_news(session, news_id):
    folder = os.path.join(DATA_DIR, str(news_id))
    ensure_dir(folder)

    news_url, comment_links = await parse_news_page(session, news_id)

    if news_url:
        await download_and_save(session, news_url, os.path.join(folder, "news.html"))

    for i, comment_url in enumerate(comment_links):
        await download_and_save(session, comment_url, os.path.join(folder, f"comment_{i}.html"))

async def crawl():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                print("Checking for new news...")
                top_ids = await get_top_news_ids(session)
                new_ids = [i for i in top_ids if i not in SEEN_IDS]

                for news_id in new_ids:
                    print(f"Processing news ID: {news_id}")
                    await process_news(session, news_id)
                    SEEN_IDS.add(news_id)

                print("Waiting for the next cycle...\n")
                await asyncio.sleep(INTERVAL)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    ensure_dir(DATA_DIR)
    asyncio.run(crawl())

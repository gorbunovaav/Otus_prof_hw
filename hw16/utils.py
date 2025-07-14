import aiofiles
import aiohttp
import os
from bs4 import BeautifulSoup

async def get_top_news_ids(session):
    async with session.get("https://news.ycombinator.com/") as resp:
        text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")
        links = soup.select("tr.athing")
        ids = [link.get("id") for link in links][:30]
        return ids

async def download_and_save(session, url, filename):
    try:
        async with session.get(url, timeout=15) as resp:
            content = await resp.read()
            async with aiofiles.open(filename, "wb") as f:
                await f.write(content)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

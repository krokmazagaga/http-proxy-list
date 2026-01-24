import asyncio
import aiohttp
import re
from pathlib import Path

# =========================
# AYARLAR
# =========================
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://www.proxy-list.download/api/v1/get?type=http",
    
]

TEST_URL = "http://example.com"
TIMEOUT = 1.2
CONCURRENCY = 100
OUTPUT_FILE = "http.txt"


# =========================
# PROXY ÇEKME
# =========================
async def fetch_proxies(session, url):
    try:
        async with session.get(url, timeout=10) as r:
            text = await r.text()
            return re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", text)
    except:
        return []


# =========================
# PROXY TEST
# =========================
async def test_proxy(proxy, session, sem):
    async with sem:
        try:
            async with session.head(
                TEST_URL,
                proxy=f"http://{proxy}",
                timeout=TIMEOUT,
            ):
                return proxy
        except:
            return None


# =========================
# ANA AKIŞ
# =========================
async def main():
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Proxyleri çek
        tasks = [fetch_proxies(session, url) for url in PROXY_SOURCES]
        results = await asyncio.gather(*tasks)

        proxies = set()
        for r in results:
            proxies.update(r)

        print(f"[+] Toplam proxy: {len(proxies)}")

        # Test et
        sem = asyncio.Semaphore(CONCURRENCY)
        test_tasks = [
            test_proxy(proxy, session, sem) for proxy in proxies
        ]

        alive = []
        for coro in asyncio.as_completed(test_tasks):
            result = await coro
            if result:
                alive.append(result)

        # Kaydet
        Path(OUTPUT_FILE).write_text("\n".join(alive))
        print(f"[✓] Çalışan proxy: {len(alive)}")


if __name__ == "__main__":
    asyncio.run(main())

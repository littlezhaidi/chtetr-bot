from cachetools import TTLCache
import aiohttp
from fake_useragent import UserAgent

cache = TTLCache(maxsize=100, ttl=60)

async def fetchdata(url: str):  
    headers = {"User-Agent": UserAgent().random}

    if url in cache:
        #print(f"從快取中讀取資料: {url}")
        return cache[url]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=5) as response:
                data = await response.json()
                if not data.get("success", True):
                    error_msg = data.get("error").get("msg")
                    print(f"API 回應錯誤: {error_msg}")
                    return None
                cache[url] = data
                return data
    except Exception as e:
        print(f"fetchdata炸了: {e}")
        raise
        

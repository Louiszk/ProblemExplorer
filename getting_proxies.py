from bs4 import BeautifulSoup
import aiohttp
import asyncio
import requests
import problem_texts as pt
import random

async def fetch(url, session, proxy):
    try:
        async with session.get(url, proxy=proxy, timeout=10, ssl = False) as response:
            return await response.text()
    except Exception as e:
        return None

async def validate_proxies(initial_proxies):
    working_proxies = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = []
        for proxy in initial_proxies:
            task = asyncio.create_task(fetch(f"https://www.reddit.com/search/?q={pt.random_searches[random.randint(0,28)]}", session, f"http://{proxy}"))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        
        for proxy, result in zip(initial_proxies, results):
            if result:
                working_proxies.append(f"http://{proxy}")
    return working_proxies

def get_initial_proxies():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

#maybe try out https://geonode.com/free-proxy-list
    overview = requests.get("https://free-proxy-list.net/", headers=headers)
    overview_soup = BeautifulSoup(overview.text, "html.parser")

    all_proxies = []
    all_trs = overview_soup.find("tbody").find_all("tr")
    for proxy in all_trs:
        proxy_row = [pr.text for pr in proxy.find_all("td")]
        if proxy_row[4] != 'transparent':
            all_proxies.append(":".join((proxy_row[0], proxy_row[1])))

    return all_proxies

async def main():
    initial_proxies = get_initial_proxies()
    loop = asyncio.get_event_loop()
    working_proxies = await validate_proxies(initial_proxies)
    await asyncio.sleep(1.0)
    working_proxies2 = await validate_proxies(initial_proxies)
    await asyncio.sleep(1.0)
    working_proxies3 = await validate_proxies(initial_proxies)
    print(working_proxies + ['...'] + working_proxies2 + ['...'] + working_proxies3)
    return list(set(working_proxies + working_proxies2 + working_proxies3))

if __name__ == '__main__':
    asyncio.run(main())
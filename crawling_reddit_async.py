import asyncio
import aiohttp
from aiohttp import ClientSession
from lxml import html
from problem_texts import search_queries
import re
import json
import random
import getting_proxies
from concurrent.futures import ThreadPoolExecutor


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36 EdgA/46.6.4.5140",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]


already_visited_urls = []
already_visited_posts = []

async def reddit_search(query, topic, proxies):
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    async with aiohttp.ClientSession() as session:
        for _ in range(len(proxies)):
            try:
                proxy = proxies.pop(0)
                proxies.append(proxy)
                async with session.get(f"https://www.reddit.com/search/?q=title%3A{query}+{topic}+self%3Atrue&t=year", headers= headers, proxy=proxy) as response:
                    if response.status == 200:
                        return await response.text()
                    
                        
            except Exception:
                print("All proxies failed for search, trying normal request")
                async with session.get(f"https://www.reddit.com/search/?q=title%3A{query}+{topic}+self%3Atrue&t=year", headers= headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"Could not Search for {query} :(")

def parse_subsite(response, url):
    tree = html.fromstring(response)

    parts = []
    if "reddit.com" in url:
        post = tree.xpath('//shreddit-post')
        if len(post) > 0:
            post = post[0]
            title = post.attrib['post-title']
            comments_count = post.attrib['comment-count']
            created_at = post.attrib['created-timestamp']
            upvotes = post.attrib['score']
            meta = (title, comments_count, upvotes, created_at)
            body_text = tree.xpath('//div[@class = "text-neutral-content"]//text()')
            parts = [text.strip() for text in body_text]

    
    if len(parts) == 0:
        return None, False
    print("Success")
    return ' '.join(parts).strip(), meta

async def subsite_search(session, url, proxies):
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    for _ in range(len(proxies)):
        try:
            proxy = proxies.pop(0)
            proxies.append(proxy)
            async with session.get(url, proxy=proxy, timeout = 6, headers = headers) as response:
                if response.status == 200:
                    response_read = await response.read()
                    return parse_subsite(response_read, url)

        except Exception as e:
            pass
            #print("Error ", e)
    print("Proxies did not work")
    async with session.get(url, timeout = 10) as response:
        if response.status == 200:
            response_read = await response.read()
            return parse_subsite(response_read, url)
        else:
            print(response.status)

    print("Couldn't Crawl Subsite :(")
    return None, None


def parse_reddit_results(html_content):
    results = []
    if html_content:
        tree = html.fromstring(html_content)
        for link in tree.xpath('//a[@data-testid = "post-title"]'):
            if 'href' in link.attrib:
                link_href = None
                if link.attrib['href'].startswith('/r/'):
                    link_href = "".join(('https://www.reddit.com', link.attrib['href']))
                elif link.attrib['href'].startswith('https://www.reddit.com'):
                    link_href = link.attrib['href']
                if link_href and link_href not in already_visited_urls and link.attrib['aria-label'] not in already_visited_posts:
                    already_visited_urls.append(link_href)
                    already_visited_posts.append(link.attrib['aria-label'])
                    results.append(link_href)
    return results

def get_categories_from_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(e)
        return None

async def process_topic(topic, proxies):
    problems_data = []
    dead_problems = []
    async with ClientSession() as session:
        for query in search_queries:
            fquery = "".join(('"', query[:-3].replace(' ', '+'), '"'))
            print(topic, fquery)

            html_content = await reddit_search(fquery, topic, proxies)
            results = parse_reddit_results(html_content)
            print(len(results))

            tasks = []
            for url in results[:max(0, (len(results)-3)//2)]:
                tasks.append(subsite_search(session, url, proxies))

            responses = await asyncio.gather(*tasks)

            for (page_content, meta), url in zip(responses, results):
                if page_content:
                    page_content = page_content.replace("Read more", "").replace("\u00e2\u0080\u0099", "'")
                    problems_data.append(list(meta) + [url, page_content])
                if not meta:
                    dead_problems.append(url)
        with open(f'problems/{topic.replace(" ", "_")}.json', 'w') as json_file:
            json.dump(problems_data, json_file)
        print(len(problems_data)*100/(len(problems_data)+len(dead_problems)))

async def main():
    #leaves = get_categories_from_file('leaf_categories.json')
    proxies = []
    while len(proxies) < 4:
        proxies = await getting_proxies.main()

    topics = ["Beer", "Wine"]

    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, asyncio.run, process_topic(topic, proxies))
            for topic in topics
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

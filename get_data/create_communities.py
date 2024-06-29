import requests
from lxml import html
import json
import time

communities = []
for page in range(40):
    time.sleep(1)
    overview = requests.get(f"https://www.reddit.com/best/communities/{page+1}")
    print(overview.status_code)
    tree = html.fromstring(overview.content)

    divs = tree.xpath('//div[@data-community-id]')

    for div in divs:
        id = div.get('id')
        name = div.get('data-prefixed-name')
        description = div.get('data-public-description-text')
        size = div.get('data-subscribers-count')
        img = div.get('data-icon-url')
        
        communities.append((id, name, description, size, img))
    print(f"Successfully scraped page {page}")

with open('communities.json', 'w') as file:
    json.dump(communities, file)
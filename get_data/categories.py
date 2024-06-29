import json
import os
import requests

def get_categories_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            if data:
                return data
    return None

def fetch_and_save_categories(filename):
    categories = json.load(requests.get("https://trends.google.com/trends/api/explore/pickers/category?hl=en-US&tz=240").text)
    with open(filename, 'w') as file:
        json.dump(categories, file)
    return categories

def get_categories(filename="categories.json"):
    categories = get_categories_from_file(filename)
    if not categories:
        categories = fetch_and_save_categories(filename)
    return categories


def recursive_extract(d):
        if 'id' in d:
            del d['id']
        if 'children' in d:
            for child in d['children']:
                recursive_extract(child)

if __name__ == "__main__":
    
    categories = get_categories()
    recursive_extract(categories)
    
    with open('filtered_categories.json', 'w') as file:
        json.dump(categories, file)
    
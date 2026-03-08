import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from api.client import MusicClient
import json

client = MusicClient()
# get categories
cats = client.get_mood_categories()
params = None
for k, v in cats.items():
    for item in v:
        if item['title'] == 'Pop':
            params = item['params']
            break

print("Testing Pop genre params:", params)
res = client.get_category_page(params)

for section in res:
    if "video" in section["title"].lower():
        print("Found Videos section!")
        for item in section["items"][:3]:
            print(item.get("title"), item.get("videoId"), item.get("browseId"))

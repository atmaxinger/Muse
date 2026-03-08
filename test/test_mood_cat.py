import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from api.client import MusicClient

client = MusicClient()
cats = client.get_mood_categories()
moods = cats.get('Moods & moments', [])
if moods:
    chill_params = moods[0]['params']
    print(f"Fetching category page for {moods[0]['title']}...")
    page_data = client.get_category_page(chill_params)
    for section in page_data:
        print(f"Section: {section['title']} - {len(section['items'])} items")
else:
    print("No moods found.")

import json
import traceback
from ytmusicapi import YTMusic

yt = YTMusic()
try:
    cats = yt.get_mood_categories()
    print("CATEGORIES:")
    for key, val in cats.items():
        print(f"  {key}: {len(val)} items")
        if val:
            print(f"    First item: {val[0].get('title')} ({val[0].get('params')})")

    # Let's try to fetch a genre playlist using the params from get_mood_categories
    genres = cats.get('Genres', [])
    if genres:
        g = genres[0]
        print(f"\nTrying to fetch genre {g.get('title')}: {g.get('params')}")
        try:
            res = yt.get_mood_playlists(g.get('params'))
            print(f"Success! {len(res)} playlists")
        except Exception as e:
            traceback.print_exc()

except Exception as e:
    traceback.print_exc()

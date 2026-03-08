import json
from ytmusicapi import YTMusic

yt = YTMusic()
try:
    explore = yt.get_explore()
    moods_and_genres = explore.get("moods_and_genres", [])

    print(f"Total moods and genres: {len(moods_and_genres)}")
    
    print("\n--- Trying to fetch first mood category ---")
    if moods_and_genres:
        m = moods_and_genres[0]
        print(f"Fetching for {m.get('title')}: {m.get('params')}")
        res = yt.get_mood_categories()
        print(f"get_mood_categories returned keys: {res.keys()}")
        
        # Look for Rock or Pop to test
        for m in moods_and_genres:
            if m.get('title') == 'Rock' or m.get('title') == 'Pop':
                print(f"Fetching for {m.get('title')}: {m.get('params')}")
                try:
                    res2 = yt.get_mood_playlists(m.get('params'))
                    print(f"Fetched {len(res2)} playlists for {m.get('title')}")
                except Exception as e:
                    print(f"Error for {m.get('title')}: {e}")
                break
except Exception as e:
    print(f"Error: {e}")

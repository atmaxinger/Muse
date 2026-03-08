import json
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist, parse_mixed_content
from ytmusicapi.parsers.explore import *
from ytmusicapi import YTMusic

with open("genre_resp.json") as f:
    resp = json.load(f)

# The results are likely in singleColumnBrowseResultsRenderer
try:
    tabs = resp['contents']['singleColumnBrowseResultsRenderer']['tabs']
    results = tabs[0]['tabRenderer']['content']['sectionListRenderer']['contents']
    print(f"Found {len(results)} sections")
    
    parsed = []
    for section in results:
        if 'musicCarouselShelfRenderer' in section:
            carousel = section['musicCarouselShelfRenderer']
            title = carousel['header']['musicCarouselShelfBasicHeaderRenderer']['title']['runs'][0]['text']
            contents = carousel['contents']
            print(f"Section: {title} with {len(contents)} items")
            # Items could be musicTwoRowItemRenderer (playlists/albums) or musicResponsiveListItemRenderer (songs)
            # Let's see what keys are in contents[0]
            if contents:
                print(f"  Item keys: {list(contents[0].keys())}")
        elif 'musicDescriptionShelfRenderer' in section:
            pass
except Exception as e:
    import traceback
    traceback.print_exc()

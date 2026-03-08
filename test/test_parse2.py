import json
from ytmusicapi.parsers.browsing import parse_mixed_content, parse_playlist
import traceback

with open("genre_resp.json") as f:
    resp = json.load(f)

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
            
            parsed_items = []
            if contents:
                if 'musicResponsiveListItemRenderer' in contents[0]:
                    print("parsing as playlist...")
                    parsed_items = parse_playlist(contents)
                elif 'musicTwoRowItemRenderer' in contents[0]:
                    print("parsing as mixed content...")
                    parsed_items = parse_mixed_content(contents)
                print(f"Parsed {len(parsed_items)} items")
except Exception as e:
    traceback.print_exc()


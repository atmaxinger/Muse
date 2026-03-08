import json
from ytmusicapi.parsers.browsing import parse_mixed_content
import traceback

with open("genre_resp.json") as f:
    resp = json.load(f)

tabs = resp['contents']['singleColumnBrowseResultsRenderer']['tabs']
results = tabs[0]['tabRenderer']['content']['sectionListRenderer']['contents']

for section in results:
    if 'musicCarouselShelfRenderer' in section:
        carousel = section['musicCarouselShelfRenderer']
        title = carousel['header']['musicCarouselShelfBasicHeaderRenderer']['title']['runs'][0]['text']
        contents = carousel['contents']
        
        parsed_items = []
        try:
            print(f"Section {title}: keys in first item: {list(contents[0].keys())}")
            from ytmusicapi.parsers.browsing import parse_content_list
            from ytmusicapi.parsers.explore import parse_explore_page
            # Actually explore parsing parses sectionListRenderer
            # So yt.get_explore() uses it. What happens if we just pass `tabs[0]['tabRenderer']['content']` to it?
        except Exception as e:
            traceback.print_exc()


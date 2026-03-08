import json
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist, parse_mixed_content
from ytmusicapi.parsers.explore import parse_explore_page

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
        for i, item in enumerate(contents):
            try:
                if 'musicResponsiveListItemRenderer' in item:
                    # Let's try parse_playlist for single item
                    # wait parse_playlist takes dictionary maybe?
                    pass
                elif 'musicTwoRowItemRenderer' in item:
                    # use parse_mixed_content but pass a list of length 1
                    pass
            except Exception as e:
                pass
        
        try:
            from ytmusicapi.parsers.utils import nav
            # actually we can just use ytmusicapi's own parse_mixed_content for two row
            # But parse_mixed_content expects a list of items
            if 'musicResponsiveListItemRenderer' in contents[0]:
                print(f"{title}: musicResponsiveListItemRenderer (Songs usually)")
                from ytmusicapi.parsers.browsing import parse_playlist
                try: 
                    # parse_playlist is for playlist items, not the playlist itself
                    # parse_playlist is not imported, wait I imported it.
                    # parse_playlist expects the item itself or the wrapper?
                    # Let's look at parse_content_list(contents, parse_playlist) it crashed.
                    pass
                except Exception:
                    pass
            else:
                print(f"{title}: TwoRowItemRenderer")
                try:
                    res = parse_mixed_content(contents)
                    print(f" parse_mixed_content got {len(res)} items")
                except Exception as e:
                    print(f" Error: {e}")
        except Exception as e:
            pass

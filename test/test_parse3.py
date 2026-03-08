import json
from ytmusicapi.parsers.browsing import parse_content_list, parse_mixed_content, parse_playlist, parse_song, parse_album
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
            if contents:
                if 'musicResponsiveListItemRenderer' in contents[0]:
                    print("parsing as songs...")
                    parsed_items = parse_content_list(contents, parse_song)
                elif 'musicTwoRowItemRenderer' in contents[0]:
                    # Need to parse these item by item, let's see what parse_mixed_content takes
                    # parse_mixed_content normally takes an array of items and a renderer key?
                    print("parsing as mixed or something else...")
                    try:
                        # parse_mixed_content might take the list of contents directly?
                        # wait, look at parse_content_list(contents, parse_album)
                        # Let's try to just use parse_mixed_content
                        parsed_items = parse_mixed_content(contents)
                    except Exception as e:
                        print("parse_mixed_content failed:", e)
            print(f"Parsed {len(parsed_items)} items for {title}")
        except Exception as e:
            print("Error for", title)
            traceback.print_exc()


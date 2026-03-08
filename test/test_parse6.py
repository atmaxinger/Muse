import json

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
        for item in contents:
            try:
                data = {}
                if 'musicResponsiveListItemRenderer' in item:
                    renderer = item['musicResponsiveListItemRenderer']
                    runs = renderer['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs']
                    data['title'] = runs[0]['text']
                    
                    if 'navigationEndpoint' in runs[0]:
                        ep = runs[0]['navigationEndpoint']
                        if 'watchEndpoint' in ep:
                            data['videoId'] = ep['watchEndpoint']['videoId']
                        elif 'browseEndpoint' in ep:
                            data['browseId'] = ep['browseEndpoint']['browseId']
                            
                    # thumbnails
                    if 'thumbnail' in renderer:
                        data['thumbnails'] = renderer['thumbnail']['musicThumbnailRenderer']['thumbnail']['thumbnails']
                        
                    # artists/subtitle
                    if len(renderer['flexColumns']) > 1:
                        sub_runs = renderer['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs']
                        artists = []
                        for r in sub_runs:
                            if 'navigationEndpoint' in r and 'browseEndpoint' in r['navigationEndpoint']:
                                if r['navigationEndpoint']['browseEndpoint']['browseEndpointContextSupportedConfigs']['browseEndpointContextMusicConfig']['pageType'] == 'MUSIC_PAGE_TYPE_ARTIST':
                                    artists.append({"name": r['text'], "id": r['navigationEndpoint']['browseEndpoint']['browseId']})
                        data['artists'] = artists
                    
                elif 'musicTwoRowItemRenderer' in item:
                    renderer = item['musicTwoRowItemRenderer']
                    runs = renderer['title']['runs']
                    data['title'] = runs[0]['text']
                    
                    if 'navigationEndpoint' in runs[0]:
                        ep = runs[0]['navigationEndpoint']
                        if 'watchEndpoint' in ep:
                            data['videoId'] = ep['watchEndpoint']['videoId']
                        elif 'browseEndpoint' in ep:
                            data['browseId'] = ep['browseEndpoint']['browseId']
                            
                    if 'thumbnailRenderer' in renderer and 'musicThumbnailRenderer' in renderer['thumbnailRenderer']:
                        data['thumbnails'] = renderer['thumbnailRenderer']['musicThumbnailRenderer']['thumbnail']['thumbnails']
                        
                    if 'subtitle' in renderer and 'runs' in renderer['subtitle']:
                        sub_runs = renderer['subtitle']['runs']
                        artists = []
                        year = None
                        type_ = None
                        for r in sub_runs:
                            if 'navigationEndpoint' in r and 'browseEndpoint' in r['navigationEndpoint']:
                                ep = r['navigationEndpoint']['browseEndpoint']
                                if 'browseEndpointContextSupportedConfigs' in ep:
                                    pt = ep['browseEndpointContextSupportedConfigs']['browseEndpointContextMusicConfig']['pageType']
                                    if pt == 'MUSIC_PAGE_TYPE_ARTIST':
                                        artists.append({"name": r['text'], "id": ep['browseId']})
                            elif 'text' in r and r['text'].strip() != '•':
                                txt = r['text'].strip()
                                if txt.isdigit() and len(txt) == 4:
                                    year = txt
                                elif txt in ['Album', 'Single', 'EP', 'Playlist']:
                                    type_ = txt
                        data['artists'] = artists
                        if year: data['year'] = year
                        if type_: data['type'] = type_
                
                if data:
                    parsed_items.append(data)
            except Exception as e:
                print("Error parsing item", e)
        print(f"Parsed {len(parsed_items)} items for {title}")


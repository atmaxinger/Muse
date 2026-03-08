import json
from ytmusicapi import YTMusic
yt = YTMusic()
response = yt._send_request("browse", {"browseId": "FEmusic_moods_and_genres_category", "params": "ggMPOg1uX0UzWGxlRE5jMDVk"})
with open("genre_resp.json", "w") as f:
    json.dump(response, f, indent=2)

import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from api.client import MusicClient
except ImportError:
    print("Error: Could not import MusicClient.")
    sys.exit(1)

def check_like_status():
    client = MusicClient()
    
    # 1. Check Search
    print("\n--- Testing Search API ---")
    search_results = client.search("Hatsune Miku", filter="songs")
    if search_results:
        first_song = search_results[0]
        print(f"Search result (song): \"{first_song.get('title')}\"")
        print(f"  likeStatus: {first_song.get('likeStatus')}")
    
    # 2. Check Playlist (using a popular case or yours)
    # Hatsune Miku top songs playlist usually works
    print("\n--- Testing Playlist API ---")
    # Using 'RDCLAK5uy_m5uDq6kXJqX_zXv6q8YnS_f2l1U9sD3oI' (Hatsune Miku mix)
    playlist_results = client.get_playlist('RDCLAK5uy_m5uDq6kXJqX_zXv6q8YnS_f2l1U9sD3oI', limit=1)
    if playlist_results and 'tracks' in playlist_results:
        first_track = playlist_results['tracks'][0]
        print(f"Playlist track: \"{first_track.get('title')}\"")
        print(f"  likeStatus: {first_track.get('likeStatus')}")

if __name__ == "__main__":
    check_like_status()

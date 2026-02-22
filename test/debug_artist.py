import sys
import os
import json

# Add src to path so we can import our modules
# Assuming we are running from the project root
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from api.client import MusicClient
except ImportError:
    print("Error: Could not import MusicClient. Make sure you are running this from the project root.")
    sys.exit(1)

def test_artist(channel_id):
    """
    Fetches artist data using MusicClient and prints a summary.
    Saves the full JSON response to artist_debug.json for inspection.
    """
    client = MusicClient()
    print(f"--- Artist API Test ---")
    print(f"Target Channel ID: {channel_id}")
    
    try:
        data = client.get_artist(channel_id)
        print(data)
        if data:
            print("\n[SUCCESS] Successfully fetched artist data.")
            print(f"Artist Name:    {data.get('name', 'N/A')}")
            print(f"Subscribers:    {data.get('subscribers', 'N/A')}")
            
            description = data.get('description', '')
            if description:
                print(f"Description:    {description}")
            else:
                print(f"Description:    (Empty)")

            # Check for various content sections
            print("\nSections Found:")
            sections = ['songs', 'albums', 'singles', 'videos']
            for section in sections:
                if section in data:
                    results = data[section].get('results', [])
                    print(f"  - {section.capitalize()}: {len(results)} items")
                    if results:
                        # Print first item as example
                        first = results[0]
                        print(f"    Example: \"{first.get('title')}\" ({first.get('videoId') or first.get('browseId')})")
            
            # Save full JSON for manual inspection
            output_file = 'artist_debug.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nFull API response saved to: {os.path.abspath(output_file)}")
            
        else:
            print("\n[FAILURE] Failed to fetch artist data (API returned None).")
            print("Check if the Channel ID is correct and if you have a working internet connection.")
            
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # If no ID provided, default to Hatsune Miku (popular test case)
    # Hatsune Miku: UCh6VpM603u6-Tf88F0U7w_A
    # Kasane Teto: UCmwz6ogzQqq4FIYv7uLQAXQ
    target_id = sys.argv[1] if len(sys.argv) > 1 else "UCh6VpM603u6-Tf88F0U7w_A"
    
    test_artist(target_id)

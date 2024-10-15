import subprocess
import argparse
import json
import os

USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def get_anime_episodes(anime_id):
    try:
        # pass arguments to the hianime.js script
        result = subprocess.run(['node', 'test.js', anime_id], capture_output=True, text=True)
        
        # Split the output into lines
        lines = result.stdout.split('\n')
        
        # Join the remaining lines to form the JSON string
        json_str = '\n'.join(lines[:-1])

        try:
            data = json.loads(json_str)
            return data
        
        except json.JSONDecodeError:
            print("Error: Invalid JSON data")
            return None
    
    except Exception as e:
        print(f"Error running hianime.js: {e}")
        return None

def get_episode_title(data):
    print(data)
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][0]['title']
    else:
        print("No episodes found in the JSON data")
        return None
    
def get_episode_id(data):
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][0]['episodeId']
    else:
        print("No episodes found in the JSON data")
        return None
    
def get_episode_number(data):
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][0]['number']
    else:
        print("No episodes found in the JSON data")
        return None

def get_episode_stream_info(episode_id):
    try:
        # pass arguments to the hianime.js script
        result = subprocess.run(['node', 'hianime.js', episode_id, 'hd-1', 'sub'], capture_output=True, text=True)
        
        # Split the output into lines
        lines = result.stdout.split('\n')
        
        # Find the first line that starts with '{'
        json_start = next((i for i, line in enumerate(lines) if line.strip().startswith('{')), None)
        
        if json_start is None:
            print("Error: JSON object not found in output")
            return None
        
        # Join the remaining lines to form the JSON string
        json_str = '\n'.join(lines[json_start:])
        
        try:
            # parse the JSON output
            data = json.loads(json_str)
            return data
        
        except json.JSONDecodeError:
            print("Error: Invalid JSON data")
            return None
    
    except Exception as e:
        print(f"Error running hianime.js: {e}")
        return None
    
def extract_stream_url(data):
    # Extract the URL from the first source in the sources array
    if 'sources' in data and len(data['sources']) > 0:
        stream_url = data['sources'][0]['url']
        print(f"Stream URL: {stream_url}")
        return stream_url
    else:
        print("No sources found in the JSON data")
    
def extract_subtitles_url(data):
    # Extract the file name from the first tracks in the tracks array
    if 'tracks' in data and len(data['tracks']) > 0:
        subtitles_url = data['tracks'][0]['file']
        print(f"Subtitles URL: {subtitles_url}")
        return subtitles_url
    else:
        print("No tracks found in the JSON data")

# download the video and audio streams from the episode url
def download_streams(stream_url, file_name):
    print(f"Downloading stream from {stream_url} to {file_name}")
    try:    
        # use ffmpeg
        subprocess.run(['ffmpeg', '-i', stream_url, '-c', 'copy', os.path.join(USER_DOWNLOADS, file_name)])
    except Exception as e:
        print(f"Error downloading stream: {e}")

# download the subtitle from the sub url
def download_subtitles(subtitles_url, file_name):
    print(f"Downloading subtitles from {subtitles_url} to {file_name}")
    try:    
        # use ffmpeg
        subprocess.run(['ffmpeg', '-i', subtitles_url, '-c', 'copy', os.path.join(USER_DOWNLOADS, file_name)])
    except Exception as e:
        print(f"Error downloading subtitles: {e}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract information from HiAnime episodes')
    parser.add_argument('slug', help='The slug of the anime series') 
    parser.add_argument('playlist_id', help='The playlist ID of the anime series')
    # parser.add_argument('anime_id', help='The uniqueID of the anime series (e.g. slug-playlistId)')
    parser.add_argument('--start', type=int, help='Starting episode number')
    parser.add_argument('--end', type=int, help='Ending episode number')
    parser.add_argument('--episode', type=int, help='Single episode number to extract')
    args = parser.parse_args()
        
    if args.episode:
        episodes = [args.episode]
    elif args.start and args.end:
        episodes = range(args.start, args.end + 1)
    else:
        print("Please specify either a single episode or a range of episodes.")
        exit(1)

    anime_info = get_anime_episodes(args.slug + "-" + args.playlist_id)
    anime_title = "Berserk"
    year = "1997"
    season = "01"
    episode_title = get_episode_title(anime_info)
    episode_id = get_episode_id(anime_info) 
    episode_number = get_episode_number(anime_info)
    print(episode_title)
    print(episode_id)
    print(episode_number)

    for ep in episodes: 
        print(f"\nExtracting information for episode {ep}")
        
        data = get_episode_stream_info(episode_id)
        # print(data)
        stream_url = extract_stream_url(data)
        print(stream_url)
        subtitles_url = extract_subtitles_url(data)
        print(subtitles_url)

        if stream_url:
            print(f"Downloading episode: {anime_title} ({year}) - S{season}E{episode_number} - {episode_title}")
            # download_streams(stream_url, f"{anime_title} ({year}) - S{season}E{episode_number} - {episode_title}.mp4")
            print("Success!")
        # if subtitles_url:
        #     download_subtitles(subtitles_url, f"{args.slug}-{ep}.vtt")
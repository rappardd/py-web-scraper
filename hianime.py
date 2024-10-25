import subprocess
import argparse
import json
import os

# features to add:
# - download subtitles
# - save list of episodes downloaded so that if the script is run again, it doesn't redownload the episodes

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
            print("Error: Invalid JSON data (anime episodes)")
            return None
    
    except Exception as e:
        print(f"Error running hianime.js: {e}")
        return None

# extract the episode title from the JSON data
def get_episode_title(data, ep_number):
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][ep_number-1]['title']
    else:
        print("No episodes found in the JSON data")
        return None
    
# extract the episode id from the JSON data
def get_episode_id(data, ep_number):
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][ep_number-1]['episodeId']
    else:
        print("No episodes found in the JSON data")
        return None
    
# extract the episode number from the JSON data
def get_episode_number(data, ep_number):
    if 'episodes' in data and len(data['episodes']) > 0:
        return data['episodes'][ep_number-1]['number']
    else:
        print("No episodes found in the JSON data")
        return None

# get the stream info for the episode
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
            print("Error: Invalid JSON data (episode stream info)")
            return None
    
    except Exception as e:
        print(f"Error running hianime.js: {e}")
        return None
    
# extract the stream url from the JSON data
def extract_stream_url(data):
    # Extract the URL from the first source in the sources array
    if 'sources' in data and len(data['sources']) > 0:
        stream_url = data['sources'][0]['url']
        print(f"Stream URL: {stream_url}")
        return stream_url
    else:
        print("No sources found in the JSON data")
    
# extract the subtitles url from the JSON data
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

def save_downloaded_episodes(anime_id, episode):
    try:
        with open("downloaded_episodes.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"anime_id": anime_id, "episodes": []}

    if data["anime_id"] == anime_id:
        if episode not in data["episodes"]:
            data["episodes"] += [episode]
    else:
        data = {"anime_id": anime_id, "episodes": [episode]}

    with open("downloaded_episodes.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract information from HiAnime episodes')
    # parser.add_argument('slug', help='The slug of the anime series') 
    # parser.add_argument('playlist_id', help='The playlist ID of the anime series')
    parser.add_argument('anime_id', help='The uniqueID of the anime series (e.g. slug-playlistId)')
    parser.add_argument('--all', action='store_true', help='Download all episodes')
    parser.add_argument('--start', type=int, help='Starting episode number')
    parser.add_argument('--end', type=int, help='Ending episode number')
    parser.add_argument('--episode', type=int, help='Single episode number to extract')
    args = parser.parse_args()
        
    if args.episode:
        episodes = [args.episode]
    elif args.all:
        # get the number of episodes in the anime
        # check if the episodes have already been downloaded
        # if not, download the episodes 
        # if already downloaded, skip them

        episodes = range(1, 99)
    elif args.start and args.end:
        episodes = range(args.start, args.end + 1)
    else:
        print("Please specify either a single episode or a range of episodes.")
        exit(1)

    anime_info = get_anime_episodes(args.anime_id)
    anime_title = "Berserk"
    year = "1997"
    season = "01"


    for ep in episodes:
        print(f"\nExtracting information for episode {ep}")
        episode_title = get_episode_title(anime_info, ep)
        episode_id = get_episode_id(anime_info, ep) 
        episode_number = get_episode_number(anime_info, ep)
        print("Title:", episode_title)
        print("ID:", episode_id)
        print("Number:", episode_number)

        # print(f"\nExtracting information for episode {ep}")
        
        data = get_episode_stream_info(f"{args.anime_id}?ep={ep}")
        # print(data)
        stream_url = extract_stream_url(data)
        print(stream_url)
        subtitles_url = extract_subtitles_url(data)
        print(subtitles_url)

        if stream_url:
            print(f"Downloading episode: {anime_title} ({year}) - S{season}E{ep} - {episode_title}")
            # download_streams(stream_url, f"{anime_title} ({year}) - S{season}E{episode_number} - {episode_title}.mp4")
            # if download is successful, add the episode to the list of downloaded episodes
            save_downloaded_episodes(args.anime_id, ep)
        # if subtitles_url:
        #     download_subtitles(subtitles_url, f"{args.slug}-{ep}.vtt")

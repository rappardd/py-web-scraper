import subprocess
import argparse
import json
import os

USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def extract_episode_info(episode_url):
    try:
        # pass arguments to the hianime.js script
        result = subprocess.run(['node', 'hianime.js', episode_url, 'hd-1', 'sub'], capture_output=True, text=True)

        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        
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

    # fetch the title and episodeId using the hianime api
    try:
        result = subprocess.run(['node', 'test.js', args.slug, args.playlist_id], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error running test.js: {e}")

    for ep in episodes:
        episode_url = f'{args.slug}-{args.playlist_id}?ep={ep}'
        print(f"\nExtracting information for episode {ep}")
        
        data = extract_episode_info(episode_url)
        print(data)
        stream_url = extract_stream_url(data)
        print(stream_url)
        subtitles_url = extract_subtitles_url(data)
        print(subtitles_url)

        if stream_url:
            download_streams(stream_url, f"{args.slug}-{ep}.mp4")
        # if subtitles_url:
        #     download_subtitles(subtitles_url, f"{args.slug}-{ep}.vtt")
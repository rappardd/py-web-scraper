import json
import re

# 1. load the json file
# 2. parse the json data to access the structure
# 3. retrieve the array from the json object
# 4. check if the number is in the array
# 5. if it is, return a message saying it is already in the array
# 6. if it is not, add it to the array and return a message saying it has been added

filename = "downloaded_episodes.json"

# Read data from JSON file
def read_json_file(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

# Write data to JSON file
def write_json_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4, separators=(',', ': '), default=str)
    return "Data has been written to file"

def download_episode(episode):
    # print(f"Downloading episode {episode}...")
    pass

def check_episode_downloaded(anime_id, episode_id):
    data = read_json_file(filename)

    array = data.get("anime", {}).get(anime_id, {}).get("episodes", [])
    
    if anime_id not in data.get("anime", {}):
        print(f"Anime {anime_id} not found in the database")
        add_anime_to_database(anime_id)
    else:
        if episode_id in array:
            return True
        else:
            return False

def add_anime_to_database(anime_id):
    print(f"Adding anime {anime_id} to the database")
    data = read_json_file(filename)
    data.get("anime", {}).update({anime_id: {"episodes": []}})
    write_json_file(filename, data)

def save_downloaded_episodes(anime_id, episode_id):
    print(f"Saving episode {episode_id} for anime {anime_id} to the database")
    data = read_json_file(filename)

    # Get the episodes array
    episodes = data["anime"][anime_id]["episodes"]
    
    # Add the new episode_id and sort the list
    if episode_id not in episodes:
        episodes.append(episode_id)
        episodes.sort()  # Sort in ascending order

    # Write to file with custom formatting
    with open(filename, 'w') as file:
        # First create formatted JSON with standard indentation
        json_content = json.dumps(data, indent=4)
        # Format arrays to be on single line
        json_content = re.sub(
            r'\[\s*([^\]]+?)\s*\]', 
            lambda m: f"[{', '.join(re.split(r',\s*', m.group(1).strip()))}]", 
            json_content
        )
        file.write(json_content)

if __name__ == "__main__":
    episodes = range(1, 10)
    anime_id = input("Please enter the anime ID: ") # e.g. berserk-1997-103
    for episode in episodes:
        downloaded = check_episode_downloaded(anime_id, episode)
        if downloaded:
            print(f"Episode {episode} has already been downloaded, skipping...")
        elif not downloaded:
            print(f"Episode {episode} has not been downloaded, downloading...")
            download_episode(episode)
            save_downloaded_episodes(anime_id, episode)
        else:
            print("Error checking if episode has been downloaded")
    # anime_id = input("Please enter the anime ID: ") # e.g. berserk-1997-103
    # episode_id = input("Please enter the episode ID: ") # e.g. 1

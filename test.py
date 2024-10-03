import re
import html
import requests
from bs4 import BeautifulSoup
import json
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import ExtractorError, clean_html, get_element_by_class

class HianimeExtractor(InfoExtractor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anime_title = None
        self.episode_list = {}
        self.language = {
            'sub': 'ja',
            'dub': 'en',
            'raw': 'ja'
        }
        self.language_codes = {
            'Arabic': 'ar',
            'English Dubbed': 'en-IN',
            'English Subbed': 'en',
            'French - Francais(France)': 'fr',
            'German - Deutsch': 'de',
            'Italian - Italiano': 'it',
            'Portuguese - Portugues(Brasil)': 'pt',
            'Russian': 'ru',
            'Spanish - Espanol': 'es',
            'Spanish - Espanol(Espana)': 'es',
        }

    def get_anime_title(self, slug, playlist_id):
        if not self.anime_title:
            url = f'https://hianime.to/watch/{slug}?ep={playlist_id}'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_element = soup.find('a', class_='text-white dynamic-name')
            if title_element is None:
                print("Error: Could not find the title element")
                return "Unknown Title"
            
            self.anime_title = title_element.text.strip()
        return self.anime_title
    
    def _extract_custom_m3u8_formats(self, m3u8_url, episode_id, server_type=None):
        # This is a placeholder implementation
        # You may need to implement proper m3u8 parsing logic here
        return [{
            'url': m3u8_url,
            'format_id': f'{server_type.upper()}',
            'ext': 'mp4',
            'protocol': 'm3u8_native',
            'quality': 1,
            'language': self.language[server_type],
        }]
    
    def extract_playlist(self, slug, playlist_id):
        anime_title = self.get_anime_title(slug, playlist_id)
        playlist_url = f'https://hianime.to/ajax/v2/episode/list/{playlist_id}'
        
        response = requests.get(playlist_url)
        playlist_data = json.loads(response.text)
        
        entries = []
        self.episode_list = {}

        for episode_html in playlist_data['html'].split('<a ')[1:]:
            # Extract episode details
            title_match = re.search(r'title="([^"]+)"', episode_html)
            data_number_match = re.search(r'data-number="([^"]+)"', episode_html)
            data_id_match = re.search(r'data-id="([^"]+)"', episode_html)
            href_match = re.search(r'href="([^"]+)"', episode_html)

            title = title_match.group(1) if title_match else None
            data_number = data_number_match.group(1) if data_number_match else None
            data_id = data_id_match.group(1) if data_id_match else None
            url = f'https://hianime.to{href_match.group(1)}' if href_match else None

            # Clean HTML entities from title
            if title:
                title = re.sub(r'&[^;]+;', lambda m: html.unescape(m.group(0)), title)

            # Add episode details to episode_list
            self.episode_list[data_id] = {
                'title': title,
                'number': int(data_number) if data_number else None,
                'url': url,
            }

            # Prepare entry for playlist result
            entries.append({
                'id': data_id,
                'title': title,
                'url': url,
            })

        return {
            'anime_title': anime_title,
            'episodes': entries
        }

    def _extract_episode(self, slug, playlist_id, episode_id):
        anime_title = self.get_anime_title(slug, playlist_id)
        episode_data = self.episode_list.get(episode_id)
        if not episode_data:
            self.extract_playlist(slug, playlist_id)
            episode_data = self.episode_list.get(episode_id)
        if not episode_data:
            raise Exception(f'Episode data for episode_id {episode_id} not found')

        # Extract episode information and formats
        servers_url = f'https://hianime.to/ajax/v2/episode/servers?episodeId={episode_id}'
        response = requests.get(servers_url)
        servers_data = response.json()

        formats = []
        subtitles = {}

        for server_type in ['sub', 'dub', 'raw']:
            server_items = self._get_elements_by_tag_and_attrib(servers_data['html'], tag='div', attribute='data-type', value=f'{server_type}', escape_value=False)
            server_id = next((re.search(r'data-id="([^"]+)"', item.group(0)).group(1) for item in server_items if re.search(r'data-id="([^"]+)"', item.group(0))), None)

            if not server_id:
                continue

            sources_url = f'https://hianime.to/ajax/v2/episode/sources?id={server_id}'
            response = requests.get(sources_url)
            sources_data = response.json()
            link = sources_data.get('link')

            if not link:
                continue

            sources_id_match = re.search(r'/embed-2/[^/]+/([^?]+)\?', link)
            sources_id = sources_id_match.group(1) if sources_id_match else None

            if not sources_id:
                continue

            video_url = f'https://megacloud.tv/embed-2/ajax/e-1/getSources?id={sources_id}'
            response = requests.get(video_url)
            video_data = response.json()
            sources = video_data.get('sources', [])
            print(sources)

            for source in sources:
                file_url = source.get('file')

                if not (file_url and file_url.endswith('.m3u8')):
                    continue

                extracted_formats = self._extract_custom_m3u8_formats(file_url, episode_id, server_type)
                formats.extend(extracted_formats)

            tracks = video_data.get('tracks', [])

            for track in tracks:
                if track.get('kind') == 'captions':
                    file_url = track.get('file')
                    language = track.get('label')
                    if language == 'English':
                        language = f'{language} {server_type.capitalize()}bed'
                    language_code = self.language_codes.get(language)
                    if not language_code:
                        language_code = language

                    if not file_url:
                        break

                    if (language_code) not in subtitles:
                        subtitles[language_code] = []

                    subtitles[language_code].append({
                        'name': language,
                        'url': file_url,
                    })

        return {
            'id': episode_id,
            'title': episode_data['title'],
            'formats': formats,
            'subtitles': subtitles,
            'series': anime_title,
            'series_id': playlist_id,
            'episode': episode_data['title'],
            'episode_number': episode_data['number'],
            'episode_id': episode_id,
        }
    
    def _get_elements_by_tag_and_attrib(self, html, tag=None, attribute=None, value=None, escape_value=True):
        if tag is None:
            tag = r'[a-zA-Z0-9:._-]+'

        if attribute:
            attribute = rf'\s+{re.escape(attribute)}'

        if value:
            value = re.escape(value) if escape_value else value
            value = f'=[\'"]?(?P<value>.*?{value}.*?)[\'"]?'

        return list(re.finditer(rf'''(?xs)
            <{tag}
            (?:\s+[a-zA-Z0-9:._-]+(?:=[a-zA-Z0-9:._-]*|="[^"]*"|='[^']*'|))*?
            {attribute}{value}
            (?:\s+[a-zA-Z0-9:._-]+(?:=[a-zA-Z0-9:._-]*|="[^"]*"|='[^']*'|))*?
            \s*>
            (?P<content>.*?)
            </{tag}>
        ''', html))

if __name__ == "__main__":
    extractor = HianimeExtractor()
    result = extractor.extract_playlist('berserk-1997', '103')
    print(f"Anime Title: {result['anime_title']}")
    print(f"Number of episodes: {len(result['episodes'])}")
    print("First few episodes:")
    for ep in result['episodes'][:5]:
        print(f"  - {ep['title']}: {ep['url']}")

    result = extractor._extract_episode('berserk-1997', '103', '3123')
    print(f"Episode Title: {result['title']}")
    print(f"Episode ID: {result['id']}")
    print(f"Episode Formats: {result['formats']}")
    print(f"Subtitles: {result['subtitles']}")
    print(f"Series: {result['series']}")
    print(f"Series ID: {result['series_id']}")
    print(f"Episode: {result['episode']}")
import requests
import logging

class YouTubeTrending:
    def __init__(
        self,
        base_url='https://www.youtube.com/youtubei/v1/browse',
        country_code='FR',
        headers={'Content-Type': 'application/json'},
        prefix_url='https://www.youtube.com/watch?v='
        ):
        self.base_url = base_url
        self.headers = headers
        self.country_code = country_code
        self.prefix_url = prefix_url

    def fetch_trending(self):
        json_data = self._build_request_payload()
        response = requests.post(self.base_url, json=json_data, headers=self.headers)

        # in HTTPS, status code of 200 indicates a successful request
        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            try:
                return self._parse_youtube_response(response.json())
            except (ValueError, KeyError) as e:
                logging.error(f"Error parsing JSON response: {e}")
        else:
            logging.error(f"Failed to fetch data: Status Code {response.status_code}")
        return None, None

    def _build_request_payload(self):
        return {
            'context': {
                'client': {
                    'gl': self.country_code,
                    'clientName': 'WEB',
                    'clientVersion': '2.20231115.01.01',
                    'originalUrl': 'https://www.youtube.com/feed/trending',
                },
            },
            'browseId': 'FEtrending',
        }

    def _parse_youtube_response(self, json_response):
        try:
            contents = json_response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
            video_data = self._extract_videos(contents)
            shorts_data = self._extract_shorts(contents)
            return video_data, shorts_data
        except KeyError as e:
            logging.error(f"Key error in JSON response: {e}")
            return None, None
        

    def _extract_videos(self, contents):
        videos = []
        for section in contents:
            try:
                video_items = section["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
            except KeyError:
                continue  # Skip to the next section if not found

            for item in video_items:
                try:
                    title = item["videoRenderer"]["title"]["runs"][0]["text"]
                    video_id = item["videoRenderer"]["videoId"]
                    full_link = self.prefix_url + video_id
                    videos.append({"title": title, "video_link": full_link})
                except KeyError:
                    continue  # same

        return videos

    def _extract_shorts(self, contents):
        shorts = []
        for section in contents:
            try:
                short_items = section["itemSectionRenderer"]["contents"][0]["reelShelfRenderer"]["items"]
            except KeyError:
                continue

            for item in short_items:
                try:
                    title = item["reelItemRenderer"]["headline"]["simpleText"]
                    short_id = item["reelItemRenderer"]["videoId"]
                    full_link = self.prefix_url + short_id
                    shorts.append({"title": title, "short_link": full_link})
                except KeyError:
                    continue

        return shorts
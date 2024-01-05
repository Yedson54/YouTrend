"""
Module: youtube_data_fetcher

This module provides functions to fetch details of YouTube videos using the 
YouTube Data API.

Main Function:
- get_video_details: Fetches details of a YouTube video using its link.

Other Functions:
- get_video_id: Extracts the video ID from a YouTube video link.
- get_category_labels: Retrieves YouTube video category labels.
- convert_duration_to_seconds: Converts YouTube video duration from ISO 8601
    format to seconds.
- get_channel_subscriber_count: Retrieves subscriber count for YouTube
    channels.
"""

import re
import warnings
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from youtrend.duration_model.process_data import preprocessing_on_loading
from youtrend.data import API_KEY


def get_video_id(video_link: str) -> str:
    """
    Extracts the video ID from a YouTube video link.

    Parameters:
    - video_link (str): The YouTube video link.

    Returns:
    - str: The extracted video ID.

    Usage Example:
        >>> get_video_id("https://www.youtube.com/watch?v=ABC123")
        'ABC123'
    """
    parsed_url = urlparse(video_link)
    path_parts = parsed_url.path.split('/')

    if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtu.be':
        return (parse_qs(parsed_url.query).get('v', [path_parts[-1]])[0]
                if 'watch' in path_parts else path_parts[-1])
    
    warnings.warn("YouTube link not recognized")
    return None


def get_category_labels(
        api_key: str,
        region_code: str = 'US',
        youtube: Optional[Resource] = None) -> Dict[str, str]:
    """
    Retrieves YouTube video category labels.

    Parameters:
    - api_key (str): Your YouTube Data API key.
    - region_code (str): The region code for fetching category labels.
      Default is 'US'.
    - youtube: Optional. The YouTube API service object.

    Returns:
    - Dict[str, str]: Dictionary mapping category IDs to category labels.

    Usage Example:
        >>> get_category_labels("your_api_key")
        {'1': 'Film & Animation', '2': 'Autos & Vehicles', ...}
    """
    if youtube is None:
        youtube = build('youtube', 'v3', developerKey=api_key)

    # Fetch video categories
    categories_response = youtube.videoCategories().list(
        part='snippet',
        regionCode=region_code
    ).execute()

    # Map category IDs to category labels
    return {category['id']: category['snippet']['title']
            for category in categories_response.get('items', [])}


import re

def convert_duration_to_seconds(duration: str) -> int:
    """
    Converts YouTube video duration from ISO 8601 format to seconds.

    Parameters:
    - duration (str): Duration string in ISO 8601 format.

    Returns:
    - int: Duration in seconds.

    Usage Example:
        >>> convert_duration_to_seconds("PT3M45S")
        225
    """
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)
    
    hours, minutes, seconds = map(int, match.groups(default='0'))

    return hours * 3600 + minutes * 60 + seconds


def get_channel_subscriber_count(api: Resource, channel_ids: List[str]) -> Optional[int]:
    """
    Retrieves subscriber count for YouTube channels.

    Parameters:
    - api: The YouTube API service object.
    - channel_ids: List of YouTube channel IDs.

    Returns:
    - Optional[int]: The subscriber count or None if an error occurs.

    Usage Example:
        >>> get_channel_subscriber_count(youtube_api_instance, ["channel_id_1", "channel_id_2"])
        100000
    """
    try:
        response = api.channels().list(
            part="statistics",
            id=','.join(channel_ids)
        ).execute()

        items = response.get("items", [])
        if items:
            return int(items[0]['statistics'].get("subscriberCount", 0))
        else:
            return None
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None


def get_video_details(video_link: str,
                      api_key: str = API_KEY,
                      region_code: str = "US",
                      video_cat_enc: Optional[OneHotEncoder] = None
                      ) -> pd.DataFrame:
    """
    Fetches details of a YouTube video using its link.

    Parameters:
    - video_link (str): The link to the YouTube video.
    - api_key (str): Your YouTube Data API key.
    - region_code (str): The region code for fetching category labels.
        Default is "US".
    - video_cat_enc (Optional[OneHotEncoder]): One-hot encoder for video
        categories.

    Returns:
    - pd.DataFrame: DataFrame containing details of the YouTube video.

    Usage Example:
        >>> get_video_details("https://www.youtube.com/watch?v=ABC123", 
        >>> ... "your_api_key")
            videoId             Titre  videoExactPublishDate  videoLengthSeconds  ...
        0  ABC123  Example Video Title  2022-01-01 12:00:00 
    """
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Fetch category labels
    categories_dict = get_category_labels(api_key, region_code, youtube)

    # Get video ID from the link
    video_id = get_video_id(video_link)

    try:
        # Get video details from YouTube API
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        video_info = response['items'][0]

        # Extract relevant information
        data = {
            'videoId': [video_id],
            'Titre': [video_info['snippet']['title']],
            'videoExactPublishDate': [video_info['snippet']['publishedAt']],
            'videoLengthSeconds': [convert_duration_to_seconds(
                video_info['contentDetails']['duration'])
            ],
            'videoCategory': [video_info['snippet']['categoryId']],
            'exactViewNumber': [video_info['statistics']['viewCount']],
            'numberLikes': [video_info['statistics']['likeCount']],
            'numberOfComments': [video_info['statistics']['commentCount']],
            'creatorSubscriberNumber': [get_channel_subscriber_count(
                youtube, [video_info['snippet']['channelId']])
            ]
        }
        df = pd.DataFrame(data)
        df["videoCategory"] = df["videoCategory"].replace(categories_dict)
        df["videoExactPublishDate"] = pd.to_datetime(
            df["videoExactPublishDate"]
        ).dt.tz_localize(None)
        df, _, _ = preprocessing_on_loading(dataframe=df, on_loading=True,
                                            video_cat_enc=video_cat_enc)

        return df

    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

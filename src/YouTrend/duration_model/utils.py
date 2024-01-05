"""
utils: Utility Module

This module provides functions for extracting, processing, and analyzing YouTube
video data to predict the survival probability of a video trending on the platform.

Main Functions:
- get_video_details(video_link: str, api_key: str = API_KEY, region_code: str = "US",
                    video_cat_enc: Optional[OneHotEncoder] = None) -> pd.DataFrame:
  Fetches details of a YouTube video using its link.

- get_video_id(video_link: str) -> str:
  Extracts the video ID from a YouTube video link.

- preprocessing(filename: str = None, dataframe: pd.DataFrame = None,
                on_loading: bool = False, video_cat_enc: OneHotEncoder = None)
  -> Tuple[pd.DataFrame, Optional[List[str]], Optional[OneHotEncoder]]:
  Process the input data for the machine learning model.

Global Constants:
- API_KEY (str): YouTube Data API key.
- MODEL: Loaded machine learning model for predicting video survival probability.
- VIDEO_CAT_ENCODER: Loaded OneHotEncoder for video categories.
"""
import re
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from googleapiclient.discovery import build
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
    """
    parsed_url = urlparse(video_link)
    video_id = (
        parsed_url.path[1:]
        if parsed_url.netloc == 'youtu.be'
        else parse_qs(parsed_url.query).get('v', [None])[0]
    )
    return video_id


def get_category_labels(api_key: str, region_code: str = 'US',
                        youtube=None) -> Dict[str, str]:
    """
    Retrieves YouTube video category labels.

    Parameters:
    - api_key (str): Your YouTube Data API key.
    - region_code (str): The region code for fetching category labels.
      Default is 'US'.
    - youtube: Optional. The YouTube API service object.

    Returns:
    - Dict[str, str]: Dictionary mapping category IDs to category labels.
    """
    if youtube is None:
        youtube = build('youtube', 'v3', developerKey=api_key)

    categories_response = youtube.videoCategories().list(
        part='snippet',
        regionCode=region_code
    ).execute()

    return {
        category['id']: category['snippet']['title']
        for category in categories_response['items']
    }


def convert_duration_to_seconds(duration: str) -> int:
    """
    Converts YouTube video duration from ISO 8601 format to seconds.

    Parameters:
    - duration (str): Duration string in ISO 8601 format.

    Returns:
    - int: Duration in seconds.
    """
    duration_pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = duration_pattern.match(duration)
    return sum(int(n or 0) * factor for n,
               factor in zip(match.groups(), [3600, 60, 1]))


def get_channel_subscriber_count(api: any, channel_ids: List[str]) -> Optional[int]:
    """
    Retrieves subscriber count for YouTube channels.

    Parameters:
    - api: The YouTube API service object.
    - channel_ids: List of YouTube channel IDs.

    Returns:
    - Optional[int]: The subscriber count or None if an error occurs.
    """
    try:
        response = api.channels().list(
            part="statistics",
            id=','.join(channel_ids)
        ).execute()
        return (
            int(response["items"][0]['statistics']["subscriberCount"])
            if 'items' in response else None
        )
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
            'videoType': [video_info['snippet']['liveBroadcastContent']],
            'videoCategory': [video_info['snippet']['categoryId']],
            'exactViewNumber': [video_info['statistics']['viewCount']],
            'numberLikes': [video_info['statistics']['likeCount']],
            'numberOfComments': [video_info['statistics']['commentCount']],
            'isCreatorVerified': [video_info['snippet']['channelId']],
            'videoKeywords': [video_info['snippet'].get('tags', [])],
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

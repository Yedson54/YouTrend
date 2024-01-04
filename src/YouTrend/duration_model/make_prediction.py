import os
import re
from typing import List, Tuple, Optional
from urllib.parse import urlparse, parse_qs

# import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = "AIzaSyCkx5_g8o7bYQkra1_IGYE8LNxHO5yEsAk"


def preprocessing(
        filename: str = None,
        dataframe: pd.DataFrame = None,
        on_loading: bool = False,
        video_cat_enc: OneHotEncoder = None,
) -> Tuple[pd.DataFrame, Optional[List[str]], Optional[OneHotEncoder]]:
    """
    Process the input data for the machine learning model.

    Args:
        filename (str): Path to the CSV file containing the data.
        dataframe (pd.DataFrame): DataFrame containing the data.

    Returns:
        df (pd.DataFrame): Processed DataFrame.
        model_features (list): List of features for the duration model.
        encoder (sklearn.preprocessing.OneHotEncoder): OneHotEncoder for
            later preprocessing before predictions.
    """
    # Define features and date columns
    features = [
        'videoId', 'videoExactPublishDate', 'creatorSubscriberNumber',
        'videoLengthSeconds', 'videoCategory', 'isCreatorVerified',
        'scanTimeStamp', 'firstTrendingTime', 'isTrend',
        'timeToTrendSeconds'
    ]
    date_cols = [
        'videoExactPublishDate', 'scanTimeStamp', 'firstTrendingTime'
    ]

    # Check if either a filename or a DataFrame has been provided
    if filename is None and dataframe is None:
        raise ValueError("Either a filename or a DataFrame must be provided.")
    elif filename is not None and dataframe is not None:
        raise ValueError("Only one of filename or DataFrame should be provided.")
    elif filename is not None:
        # Check if file exists
        if not os.path.isfile(filename):
            raise ValueError(f"File {filename} does not exist.")
        # Read data from CSV file
        df = pd.read_csv(filename, usecols=features)
    else:
        # Check if DataFrame is not empty
        if dataframe.empty:
            raise ValueError("Provided DataFrame is empty.")
        df = dataframe
        if on_loading:
            df["dayOfWeek"] = df["videoExactPublishDate"].dt.day_name()
            encoded_categories = pd.DataFrame(
                video_cat_enc.transform(
                    df[['videoCategory']].to_numpy().reshape(-1, 1)),
                columns=video_cat_enc.categories_
            )
            encoded_categories.columns = pd.Index(
                ['videoCat_' + cat.replace(" & ", "_and_").strip().capitalize()
                for cat in encoded_categories.columns.get_level_values(0)]
            )
            df = pd.concat([df, encoded_categories], axis=1)
            prediction_features = [
                "videoExactPublishDate",
                "videoLengthSeconds",
                "creatorSubscriberNumber"
            ] + encoded_categories.columns.to_list()
            df = df[prediction_features]

            return df, prediction_features, None

    # Convert datetime columns and pass boolean columns to int
    df[date_cols] = df[date_cols].apply(pd.to_datetime, format='ISO8601')
    df[["isTrend", "isCreatorVerified"]] = df[["isTrend", "isCreatorVerified"]].astype(int)

    # Convert timeToTrend in days
    df["timeToTrendDays"] = (df["timeToTrendSeconds"] / 86400).astype(int)

    # Extract day of the week from videoExactPublishDate
    df["dayOfWeek"] = df["videoExactPublishDate"].dt.day_name()

    # One-hot encode the 'videoCategory' column
    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    one_hot = encoder.fit_transform(df[['videoCategory']])
    categories = encoder.categories_[0]
    categories = [
        'videoCat_' + cat.replace(" & ", "_and_").strip().capitalize()
        for cat in categories
    ]
    one_hot_df = pd.DataFrame(one_hot, columns=categories)
    df = pd.concat([df, one_hot_df], axis=1)

    # Model features for machine learning
    model_features = [
        'timeToTrendDays', 'isTrend', 'creatorSubscriberNumber',
        'videoLengthSeconds',
    ] + [col for col in df.columns if col.startswith('videoCat_')]

    return df, model_features, encoder


def get_video_details(
        video_link: str,
        api_key: str=API_KEY,
        region_code: str="US",
        video_cat_enc: Optional[OneHotEncoder]=None
) -> pd.DataFrame:
    youtube = build('youtube', 'v3', developerKey=api_key)

    categories_dict = _get_category_labels(api_key, region_code, youtube)

    video_id = _get_video_id(video_link)

    try:
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        video_info = response['items'][0]

        data = {
            'videoId': [video_id],
            'Titre': [video_info['snippet']['title']],
            'videoExactPublishDate': [video_info['snippet']['publishedAt']],
            'videoLengthSeconds': [_convert_duration_to_seconds(
                video_info['contentDetails']['duration'])],
            'videoType': [video_info['snippet']['liveBroadcastContent']],
            'videoCategory': [video_info['snippet']['categoryId']],
            'exactViewNumber': [video_info['statistics']['viewCount']],
            'numberLikes': [video_info['statistics']['likeCount']],
            'numberOfComments': [video_info['statistics']['commentCount']],
            'isCreatorVerified': [video_info['snippet']['channelId']],
            'videoKeywords': [video_info['snippet'].get('tags', [])],
            'creatorSubscriberNumber': [_get_channel_subscriber_count(
                youtube, [video_info['snippet']['channelId']])]
        }

        df = pd.DataFrame(data)
        df["videoCategory"] = df["videoCategory"].replace(categories_dict)
        df["videoExactPublishDate"] = pd.to_datetime(
            df["videoExactPublishDate"]
        ).dt.tz_localize(None)
        df, _, _ = preprocessing(dataframe=df, on_loading=True, video_cat_enc=video_cat_enc)

        return df

    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def _get_video_id(video_link: str) -> str:
    parsed_url = urlparse(video_link)
    video_id = (
        parsed_url.path[1:]
        if parsed_url.netloc == 'youtu.be'
        else parse_qs(parsed_url.query).get('v', [None])[0]
    )
    return video_id

def _get_category_labels(api_key: str, region_code: str='US', youtube=None):
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

def _convert_duration_to_seconds(duration: str) -> int:
    duration_pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = duration_pattern.match(duration)
    return sum(int(n or 0) * factor for n, factor in zip(match.groups(), [3600, 60, 1]))

def _get_channel_subscriber_count(api, channel_ids):
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

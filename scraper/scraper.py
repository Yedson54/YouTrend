import pandas as pd
import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sklearn.preprocessing import OneHotEncoder

# my_encoder = OneHotEncoder(handle_unknown='ignore')
# super_df = pd.read_csv('pages/donnees/duration_model_data.csv')
# n = len(super_df.videoCategory.unique())
# col_names = ['Video_cat_{}'.format(i) for i in range(n)]


def get_video_id(string_video_link):
    video_id = string_video_link.split('v=')[1]
    return video_id



API_KEY = "AIzaSyCkx5_g8o7bYQkra1_IGYE8LNxHO5yEsAk"  # Remplacez par votre propre clé API


def get_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=os.getenv("API_KEY"))

    try:
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        video_info = response['items'][0]

        # Extraire les informations spécifiques
        video_id = video_info['id']
        title = video_info['snippet']['title']
        published_at = video_info['snippet']['publishedAt']
        video_trends_ranking = video_info['statistics']['viewCount']
        video_length_seconds = video_info['contentDetails']['duration']
        video_type = video_info['snippet']['liveBroadcastContent']
        video_category = video_info['snippet']['categoryId']
        exact_view_number = video_info['statistics']['viewCount']
        number_likes = video_info['statistics']['likeCount']
        number_of_comments = video_info['statistics']['commentCount']
        is_creator_verified = video_info['snippet']['channelId']
        video_keywords = video_info[
            'snippet']['tags'] if 'tags' in video_info['snippet'] else []

        # Créer un DataFrame
        data = {
            'videoId': [video_id],
            'Titre': [title],
            'videoExactPublishDate': [published_at],
            'Classement tendances': [video_trends_ranking],
            'videoLengthSeconds': [video_length_seconds],
            'videoType': [video_type],
            'videoCategory': [video_category],
            'exactViewNumber': [exact_view_number],
            'numberLikes': [number_likes],
            'numberOfComments': [number_of_comments],
            'isCreatorVerified ?': [is_creator_verified],
            'videoKeywords': [video_keywords]
        }  # 'Nombre d\'abonnés du créateur': [creator_subscriber_number],

        df = pd.DataFrame(data)
        df.to_csv(f"/data/{datetime.date()}_extraction.csv")

    except HttpError as e:
        print(f"Une erreur s'est produite : {e}")
    return df

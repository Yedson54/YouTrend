"""
Make prediction

This module provides functions for analyzing the probability of YouTube
videos to not reach trend based on various features, including video length,
creator's subscriber count, and publication date.

Functions:
- survival_probability: Calculate survival probability for a video.

- plot_survival_probability:  Plot the survival probability over a specified
    duration for a given video.
"""
import os
import pickle
import datetime
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

from backend.utils import (
    preprocessing,
    get_video_details
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
print(YOUTUBE_API_KEY)

with open("backend/models/duration_model.pickle", "rb") as f:
    FINAL_MODEL = pickle.load(f)


with open("backend/models/video_category_encoder.pickle", "rb") as f:
    VIDEO_CAT_ENCODER = pickle.load(f)
    
    
data, model_features, cat_encoder = preprocessing(
    '/data/train_duration_sample.csv'
)


def _normalize(series, data_max, data_min):
    return np.maximum((series - data_min) / (data_max - data_min), [0])

def survival_probability(
        video_link,
        date: Optional[str] = None, 
        YOUTUBE_API_KEY: str = YOUTUBE_API_KEY,
        region_code: str = "US",
        video_cat_enc: OneHotEncoder = None
) -> float:
    """
    Calculate survival probability for a video.

    Parameters:
    - video_link: The link to the video.
    - date: Date for calculating survival probability.
    - YOUTUBE_API_KEY: YouTube Data API key.
    - region_code: Region code for fetching category labels.
    - video_cat_enc: One-hot encoder for video categories.

    Returns:
    - Survival probability as a float.
    """
    single_df = get_video_details(
        video_link=video_link,
        YOUTUBE_API_KEY=YOUTUBE_API_KEY,
        region_code=region_code,
        video_cat_enc=video_cat_enc
    )

    date = pd.to_datetime(date) if date else datetime.datetime.now()

    single_df['timeToTrendDays'] = (
        date - single_df["videoExactPublishDate"]
    ).dt.total_seconds() / (24 * 3600)

    scaler = MinMaxScaler()
    scaler.fit(data[['creatorSubscriberNumber']])
    single_df['creatorSubscriberNumber'] = _normalize(
        single_df['creatorSubscriberNumber'], scaler.data_max_[0], scaler.data_min_[0]
    )
    scaler.fit(data[['videoLengthSeconds']])
    single_df['videoLengthSeconds'] = _normalize(
        single_df['videoLengthSeconds'], scaler.data_max_[0], scaler.data_min_[0]
    )

    def predict_cumulative_hazard_at_single_time(
            self, X, times, ancillary_X=None):
        lambda_, rho_ = (
            self._prep_inputs_for_prediction_and_return_scores(X, ancillary_X)
        )
        return (times / lambda_) ** rho_

    def predict_survival_function_at_single_time(
            self, X, times, ancillary_X=None):
        return np.exp(
            -self.predict_cumulative_hazard_at_single_time(
                X, times=times,ancillary_X=ancillary_X)
        )

    FINAL_MODEL.predict_survival_function_at_single_time = (
        predict_survival_function_at_single_time.__get__(FINAL_MODEL)
    )
    FINAL_MODEL.predict_cumulative_hazard_at_single_time = (
        predict_cumulative_hazard_at_single_time.__get__(FINAL_MODEL)
    )

    p_surv = FINAL_MODEL.predict_survival_function_at_single_time(
        single_df, single_df['timeToTrendDays']
    )

    return p_surv

def plot_survival_probability(
        single_df,
        start_date: Optional[str] = None, 
        duration_days: int = 10, 
        gap: float = 0.5,
        video_link: str = None,  
        YOUTUBE_API_KEY: str = YOUTUBE_API_KEY,
        region_code: str = "US",
        video_cat_enc: OneHotEncoder = None
):
    # Prepare the DataFrame
    video_test = single_df.copy()
    video_test['duration_in_day'] = duration_days
    duration = [gap * (i + 1) for i in range(int(duration_days / gap))]
    video_test_duplicate = pd.concat([video_test for _ in range(len(duration))])
    video_test_duplicate.set_index(pd.Index(range(len(duration))), inplace=True)
    video_test_duplicate['duration_in_day'] = duration

    # Calculate survival probabilities
    p_survivals = np.zeros(len(duration))
    date_0 = single_df.loc[0, "videoExactPublishDate"]
    if start_date:
        start_date = pd.to_datetime(start_date)
        date_0 = max(start_date, date_0)

    for i, dur in enumerate(duration):
        current_date = date_0 + pd.Timedelta(days=dur)
        p_survivals[i] = survival_probability(
            date = current_date,
            video_link = video_link, 
            YOUTUBE_API_KEY = YOUTUBE_API_KEY,
            region_code = region_code,
            video_cat_enc = video_cat_enc
        )

    # Plot the survival probabilities
    x = list(range(1, len(duration) + 1))
    y = list(p_survivals)
    # plt.step(x, y, where='post', label='')
    # plt.title('Fonction de survie')
    # plt.xlabel('duree en 6 heures')
    # plt.ylabel('Probabilite')
    # plt.legend()
    # plt.show()
    return x, y
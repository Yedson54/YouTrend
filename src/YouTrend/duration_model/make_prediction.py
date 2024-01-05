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
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import (
    MinMaxScaler,
    OneHotEncoder,
)
from lifelines import KaplanMeierFitter

from youtrend.duration_model.utils import get_video_details
from youtrend.data import (
    MODEL,
    API_KEY,
    DURATION_MODEL_DF,
    VIDEO_CAT_ENCODER,
)


def _normalize(series, data_max, data_min):
    return np.maximum((series - data_min) / (data_max - data_min), [0])

def survival_probability(
        video_link,
        date: Optional[str] = None,
        api_key: str = API_KEY,
        region_code: str = "US",
        video_cat_enc: OneHotEncoder = VIDEO_CAT_ENCODER
) -> float:
    """
    Calculate survival probability for a video.

    Parameters:
    - video_link: The link to the video.
    - date: Date for calculating survival probability.
    - api_key: YouTube Data API key.
    - region_code: Region code for fetching category labels.
    - video_cat_enc: One-hot encoder for video categories.

    Returns:
    - Survival probability as a float.
    """
    single_df = get_video_details(
        video_link=video_link,
        api_key=api_key,
        region_code=region_code,
        video_cat_enc=video_cat_enc
    )

    date = pd.to_datetime(date) if date else datetime.datetime.now()

    single_df['timeToTrendDays'] = (
        date - single_df["videoExactPublishDate"]
    ).dt.total_seconds() / (24 * 3600)

    scaler = MinMaxScaler()
    scaler.fit(DURATION_MODEL_DF[['creatorSubscriberNumber']])
    single_df['creatorSubscriberNumber'] = _normalize(
        single_df['creatorSubscriberNumber'], scaler.data_max_[0], scaler.data_min_[0]
    )
    scaler.fit(DURATION_MODEL_DF[['videoLengthSeconds']])
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

    MODEL.predict_survival_function_at_single_time = (
        predict_survival_function_at_single_time.__get__(MODEL)
    )
    MODEL.predict_cumulative_hazard_at_single_time = (
        predict_cumulative_hazard_at_single_time.__get__(MODEL)
    )

    p_surv = MODEL.predict_survival_function_at_single_time(
        single_df, single_df['timeToTrendDays']
    )[0]

    return p_surv

def plot_survival_probability(
        start_date: Optional[str] = None,
        duration_days: int = 10,
        gap: float = 0.5,
        video_link: str = None,
        api_key: str = API_KEY,
        region_code: str = "US",
        video_cat_enc: OneHotEncoder = VIDEO_CAT_ENCODER
):
    single_df = get_video_details(
        video_link=video_link,
        api_key=api_key,
        region_code=region_code,
        video_cat_enc=video_cat_enc
    )

    # Prepare the DataFrame
    duration = np.arange(gap, duration_days + gap, gap)
    video_test_duplicate = pd.DataFrame(np.repeat(single_df.values, len(duration), axis=0), columns=single_df.columns)
    video_test_duplicate['duration_in_day'] = duration

    # Calculate survival probabilities
    date_0 = pd.to_datetime(single_df.loc[0, "videoExactPublishDate"])
    if start_date:
        start_date = pd.to_datetime(start_date)
        date_0 = max(start_date, date_0)

    p_survivals = np.array([survival_probability(
            date = date_0 + pd.Timedelta(days=dur),
            video_link = video_link, 
            api_key = api_key,
            region_code = region_code,
            video_cat_enc = video_cat_enc
        ) for dur in duration])

    # Plot the survival probabilities
    period = gap * 24
    plt.step(duration, 1 - p_survivals, where='post')
    plt.title("Probability of a YouTube Video Entering Trend Over Time")
    plt.xlabel(
        f"Elapsed Time (in periods of {period} hours from video publish date)"
    )
    plt.ylabel("Probability of Entering Trend")
    plt.show()


def _kmf_model_per_day_and_video_cat(
        day: str,
        category: str,
        full_df: pd.DataFrame = DURATION_MODEL_DF,
        p=0.05,
        random_state=42
):
    day, category = day.capitalize(), category.capitalize()
    valid_days = full_df["dayOfWeek"].unique()
    valid_categories = full_df["videoCategory"].unique()
    # Check that day and categorie are valid
    if not((day in valid_days) & (category in valid_categories)):
        raise ValueError(f"Invalid day {day} or category {category}."
                         f"Choose Days in {valid_days}." 
                         f"Choose categories in {valid_categories}")

    # Filter the DataFrame based on day and category
    df = full_df[(full_df["dayOfWeek"] == day) 
                  & (full_df["videoCategory"] == category)].copy()

    def add_ghost_censored_samples(input_df, p=p):
        df: pd.DataFrame = input_df.copy()
        n_ghost_sample = int(p * len(df)) # 10% add of censored sample
        if df["isTrend"][df["isTrend"] == 0].count() < n_ghost_sample:
            last_lines_df = df.sample(
                n=n_ghost_sample, random_state=random_state
            )
            last_lines_df["isTrend"] = 0
            df = pd.concat([df, last_lines_df])
        return df

    print("EMPTY?", df.empty)
    if df.empty:
        df = full_df[full_df["videoCategory"] == category]
        category = "None"

    df = add_ghost_censored_samples(df, p)

    kmf_model = KaplanMeierFitter()
    kmf_model.fit(df['videoLengthDays'], df['isTrend'])

    return kmf_model, category

def plot_survival_probabilities_by_group(days, category):
    full_df = DURATION_MODEL_DF
    for day in days:
        kmf, cat = _kmf_model_per_day_and_video_cat(day, category, full_df)
        kmf.plot(label=f"day={day} and category={cat}")
    plt.xlabel("Duration in Days")
    plt.ylabel('Survival Probability')
    plt.legend(loc='upper right', bbox_to_anchor=(2, 1))
    plt.show()

"""
Duration Model Processing Module

This module provides functions for processing data related to a duration model.
The duration model is designed to analyze videos' time-to-trend and determine
whether a video has been trending within a specified time frame.

Functions:
- load_data: Load data from a folder or specific files.
- _parse_numeric_column: Parse a numeric column, handling 'K' and 'M' suffixes.
- clean_columns: Clean columns in a DataFrame.
- create_duration_model_columns: Adjust the end date of the data based on the
  chosen frequency and compute the duration before trending for each video.
"""
import os
import glob
import warnings
from typing import List, Tuple, Optional, Literal

import numpy as np
import pandas as pd
from pandas import DataFrame, Series, Timedelta
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings(action="ignore")


def _load_data(
        folder: str = None,
        pattern: str = "dataset*",
        use_filenames: bool = False,
        filenames: List[str] = None) -> pd.DataFrame:
    """
    Load data from a folder or specific files.

    Args:
        folder (str, optional): The path to the folder containing the data
            files.
        pattern (str, optional): The pattern to match files in the folder.
        use_filenames (bool, optional): If True, use the filenames provided in
            the 'filenames' parameter. If False, load all files in the folder.
        filenames (List[str], optional): A list of filenames to load. Only
            used if 'use_filenames' is True.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.
    """
    if use_filenames:
        files = filenames
    else:
        files = glob.glob(rf"{folder}/{pattern}")

    dfs = [pd.read_csv(file, index_col=0) for file in files]
    concat_df = pd.concat(dfs, ignore_index=True)

    return concat_df


def _parse_numeric_column(series: Series) -> Series:
    """
    Parse a numeric column, handling 'K' and 'M' suffixes.

    Args:
        series (Series): The series to parse.

    Returns:
        Series: The parsed series, with 'K' and 'M' suffixes converted to
            numeric values.
    """
    # Normalize columns (remove whitespace, lowercase, remove ",")
    series = series.str.strip().str.lower().replace(',', '', regex=True)

    # Extract the numeric part and the suffix.
    pattern = r'(\d+(?:\.\d+)?)([KkMm])?'  # regex group capture
    result_df = series.str.extract(pattern, expand=True)
    numeric_part = pd.to_numeric(result_df[0], errors='coerce')
    suffix_series = result_df[1]
    # Define a dictionary to map suffixes to multiplication factors
    suffix_multiplier = {'K': 1e3, 'k': 1e3, 'M': 1e6, 'm': 1e6}
    multiplier = suffix_series.map(suffix_multiplier)
    multiplier = multiplier.fillna(1) # rows without a suffix
    # Multiply the numeric part by the multiplier.
    result_series = numeric_part * multiplier
    result_series = pd.to_numeric(result_series, downcast='integer')

    return result_series


def _clean_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean columns in a DataFrame.

    Args:
        data (pd.DataFrame): The DataFrame to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    df = data.copy()

    # Datetime columns
    df["videoExactPublishDate"] = pd.to_datetime(
        df["videoExactPublishDate"], utc=True
    )
    df["scanTimeStamp"] = pd.to_datetime(
        df["scanTimeStamp"], unit="s", utc=True
    )

    # Numeric columns
    df["numberLikes"] = _parse_numeric_column(df["numberLikes"])
    df["exactViewNumber"] = _parse_numeric_column(df["exactViewNumber"])
    df["numberOfComments"] = _parse_numeric_column(df["numberOfComments"])
    df["creatorSubscriberNumber"] = _parse_numeric_column(
        df["creatorSubscriberNumber"]
    )

    return df


def _create_duration_model_columns(
        data: DataFrame,
        frequency: Literal["hour", "day"] = "hour"
) -> DataFrame:
    """
    Adjust the end date of the data based on the chosen frequency and compute
    the duration before trending for each video.

    Args:
        data (DataFrame): The DataFrame containing the data.
        frequency (Literal["hour", "day"]): The frequency for the adjustment.
            If "hour", subtract 1 hour from the end date.
            If "day", subtract 1 day from the end date.
            Other possible values: see `pandas.Timedelta()`.

    Returns:
        DataFrame: The DataFrame with the time to trend in seconds.
    """
    df = data.copy()
    start_date = pd.to_datetime(df["videoExactPublishDate"].min())
    end_date = pd.to_datetime(df["scanTimeStamp"].max())
    end_date -= Timedelta(value=1.5, unit=frequency)

    # Compute the time spent before entering in the trending list.
    first_trending_time = df.groupby("videoId")["scanTimeStamp"].min()
    first_trending_time.name = "firstTrendingTime"
    df = df.merge(first_trending_time, left_on="videoId", right_index=True)
    df["timeToTrendSeconds"] = (
        df["firstTrendingTime"] - df["videoExactPublishDate"]
    ).dt.total_seconds()

    # Determine whether or not the video has been trending
    df["isTrend"] = np.logical_and(
        df["firstTrendingTime"] >= start_date,
        df["firstTrendingTime"] <= end_date
    )

    return df.sort_index()


def processing_for_duration_model(
        folder: str = "../../../data", #TODO: move data folder closer
        pattern: str = "dataset*",
        use_filenames: bool = False,
        filenames: List[str] = None,
        frequency: Literal["hour", "day"] = "hour"
) -> DataFrame:
    """
    Perform data processing operations for a duration model.

    This function combines loading data, cleaning columns, and creating
    duration model columns using the previously defined functions.

    Args:
        folder (str, optional): The path to the folder containing the data
            files.
        pattern (str, optional): The pattern to match files in the folder.
        use_filenames (bool, optional): If True, use the filenames provided
            in the 'filenames' parameter. If False, load all files in the
            folder.
        filenames (List[str], optional): A list of filenames to load. Only
            used if 'use_filenames' is True.
        frequency (Literal["hour", "day"], optional): The frequency for the
            adjustment.
                If "hour", subtract 1 hour from the end date.
                If "day", subtract 1 day from the end date.
                Other possible values: see `pandas.Timedelta()`.

    Returns:
        DataFrame: The processed DataFrame for the duration model.
    """
    # Load data
    data = _load_data(
        folder=folder,
        pattern=pattern,
        use_filenames=use_filenames,
        filenames=filenames
    )

    # Clean columns
    cleaned_data = _clean_columns(data)

    # Create duration model columns
    processed_data = _create_duration_model_columns(cleaned_data, frequency)

    return processed_data


def preprocessing_on_loading(
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
    if filename is not None and dataframe is not None:
        raise ValueError("Only one of filename or DataFrame should be provided.")
    if filename is not None:
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
    df["videoLengthDays"] = (df["videoLengthSeconds"] / 86400).astype(float)

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

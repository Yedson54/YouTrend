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
import glob
from typing import List, Literal

import numpy as np
import pandas as pd
from pandas import DataFrame, Series, Timedelta


def load_data(
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

    # Define a regex pattern to match numbers with optional K or M suffix
    pattern = r'(\d+(?:\.\d+)?)([KkMm])?'  # regex group capture

    # Extract the numeric part and the suffix.
    result_df = series.str.extract(pattern, expand=True)
    numeric_part = pd.to_numeric(result_df[0], errors='coerce')
    suffix_series = result_df[1]

    # Define a dictionary to map suffixes to multiplication factors
    suffix_multiplier = {'K': 1e3, 'k': 1e3, 'M': 1e6, 'm': 1e6}

    # Multiply by the corresponding factor based on the suffix
    multiplier = suffix_series.map(suffix_multiplier)

    # Replace NaN values with 1 (default multiplier for rows without a suffix)
    multiplier = multiplier.fillna(1)

    # Multiply the numeric part by the multiplier, ensure numeric type.
    result_series = numeric_part * multiplier
    result_series = pd.to_numeric(result_series, downcast='integer')

    return result_series


def clean_columns(data: pd.DataFrame) -> pd.DataFrame:
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


def create_duration_model_columns(
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
        folder: str = None,
        pattern: str = "dataset*",
        use_filenames: bool = False,
        filenames: List[str] = None,
        frequency: Literal["hour", "day"] = "hour") -> DataFrame:
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
    data = load_data(
        folder=folder,
        pattern=pattern,
        use_filenames=use_filenames,
        filenames=filenames
    )

    # Clean columns
    cleaned_data = clean_columns(data)

    # Create duration model columns
    processed_data = create_duration_model_columns(cleaned_data, frequency)

    return processed_data

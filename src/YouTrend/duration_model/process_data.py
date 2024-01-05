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
import warnings
from pathlib import Path
from typing import List, Tuple, Optional, Literal

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings(action="ignore")


def _load_data(
        folder: Optional[str] = None,
        pattern: str = "dataset*",
        use_filenames: bool = False,
        filenames: Optional[List[str]] = None) -> DataFrame:
    """
    Load data from a folder or specific files.

    Args:
        folder (str, optional): The path to the folder containing the data files.
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
        folder_path = Path(folder)
        files = list(folder_path.glob(pattern))

        # Check if any files were found
        if not files:
            raise FileNotFoundError(
                f"No files found with pattern '{pattern}' in folder "
                f"'{folder}'.")

    # Read data from files into a list of DataFrames
    dfs = [pd.read_csv(file, index_col=0) for file in files]

    # Concatenate DataFrames into a single DataFrame
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
    series = series.str.replace(r'\s|,', '', regex=True).str.lower()

    # Extract the numeric part and the suffix.
    pattern = r'(\d+(?:\.\d+)?)([KkMm]?)'  # regex group capture
    result_df = series.str.extract(pattern, expand=True)

    # Replace (45K or 45k -> 45_000), (45M or 45m -> 45_000_000)
    result_series = (
        pd.to_numeric(result_df[0], errors='coerce') *
        result_df[1].map({'K': 1e3, 'k': 1e3, 'M': 1e6, 'm': 1e6}).fillna(1)
    ).astype('Int64')

    return result_series


def _clean_columns(data: DataFrame) -> DataFrame:
    """
    Clean columns in a DataFrame.

    Args:
        data (pd.DataFrame): The DataFrame to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    # Datetime columns
    data["videoExactPublishDate"] = pd.to_datetime(data["videoExactPublishDate"], utc=True)
    data["scanTimeStamp"] = pd.to_datetime(data["scanTimeStamp"], unit="s", utc=True)

    # Numeric columns
    # numeric_columns = ["numberLikes", "exactViewNumber",
    #                    "numberOfComments", "creatorSubscriberNumber"]
    numeric_columns = data.columns[
        data.columns.str.contains(r"number|Number", regex=True)
    ]
    data[numeric_columns] = data[numeric_columns].apply(_parse_numeric_column)

    return data


def _create_duration_model_columns(
        data: DataFrame,
        frequency: Literal["hour", "day"] = "hour",
        delay: int = 1.5
) -> DataFrame:
    """
    Adjust the end date of the data based on the chosen frequency and compute
    the duration before trending for each video.

    Args:
        data (DataFrame): The DataFrame containing the data.
        frequency (Literal["hour", "day"]): The frequency for the adjustment.
            If "hour", subtract `delay` hour from the end date.
            If "day", subtract `delay` day from the end date.
            Other possible values: see `pandas.Timedelta()`.

    Returns:
        DataFrame: The DataFrame with the time to trend in seconds.
    """
    df = data.copy()
    start_date = pd.to_datetime(data["videoExactPublishDate"].min())
    end_date = (pd.to_datetime(data["scanTimeStamp"].max())
                - pd.Timedelta(value=delay, unit=frequency))

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
        df["firstTrendingTime"] <= end_date)

    return df.sort_index()


def processing_for_duration_model(
        folder: str = "original_data",
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
            files. Defaults to "original_data".
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
    if folder == "original_data":
        module_path = os.path.dirname(os.path.abspath(__file__))
        data_folder = os.path.join(module_path, "..", "data", folder) #TODO: it is using the folder "youtube.data"
    else:
        data_folder = folder

    # Load data
    data = _load_data(
        folder=data_folder,
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
        dataframe: DataFrame = None,
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
    bool_cols = ["isTrend", "isCreatorVerified"]

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
    df[bool_cols] = df[bool_cols].astype(int)

    # Convert in days
    convert_in_days_cols, new_names_days_cols = zip(*[
        ("timeToTrendSeconds", "timeToTrendDays"),
        ("videoLengthSeconds", "videoLengthDays")])
    df[list(new_names_days_cols)] = (df[list(convert_in_days_cols)] / 86400).astype(float)

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

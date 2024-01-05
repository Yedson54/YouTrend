import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from youtrend.duration_model.process_data import (
    _load_data,
    _clean_columns,
    _parse_numeric_column,
    _create_duration_model_columns,
)


# Test cases
def test_load_data_from_folder(tmp_path):
    # Create a temporary folder with test files
    test_folder = tmp_path / "test_data_folder"
    test_folder.mkdir()

    # Create sample CSV files with test data
    file1_path = test_folder / "dataset1.csv"
    file2_path = test_folder / "dataset2.csv"
    file1_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    file2_data = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    file1_data.to_csv(file1_path)
    file2_data.to_csv(file2_path)

    # Test the function
    result_df = _load_data(folder=str(test_folder), pattern="dataset*")

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    pd.testing.assert_frame_equal(result_df, pd.concat([file1_data, file2_data], ignore_index=True))


def test_load_data_from_filenames(tmp_path):
    # Create a temporary folder with test files
    test_folder = tmp_path / "test_data_folder"
    test_folder.mkdir()

    # Create sample CSV files with test data
    file1_path = test_folder / "dataset1.csv"
    file2_path = test_folder / "dataset2.csv"
    file1_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    file2_data = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    file1_data.to_csv(file1_path)
    file2_data.to_csv(file2_path)

    # Test the function with specific filenames
    result_df = _load_data(use_filenames=True, filenames=[str(file1_path), str(file2_path)])

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    pd.testing.assert_frame_equal(result_df, pd.concat([file1_data, file2_data], ignore_index=True))


# Test case with invalid values
def test_parse_numeric_column_invalid_values():
    input_series = pd.Series(['abc', '4.5K', '1.2M'])
    result_series = _parse_numeric_column(input_series)
    expected_series = pd.Series([None, 4500, 1200000], dtype='Int64')
    pd.testing.assert_series_equal(result_series, expected_series)


def test_clean_columns():
    # Sample data with mixed data types
    data = pd.DataFrame({
        'videoExactPublishDate': ['2022-01-01 12:00:00', '2022-02-01 15:30:00'],
        'scanTimeStamp': [1641062400, 1643750700],
        'numberLikes': ['1.2K', '3.5M'],
        'exactViewNumber': [1000, '2.2M'],
        'numberOfComments': ['500', '1K'],
        'creatorSubscriberNumber': ['800', '1.8M']
    })

    # Call the function
    cleaned_data = _clean_columns(data)

    # Assertions for datetime columns
    assert pd.api.types.is_datetime64_any_dtype(cleaned_data['videoExactPublishDate'])
    assert pd.api.types.is_datetime64_any_dtype(cleaned_data['scanTimeStamp'])

    # Assertions for numeric columns
    assert pd.api.types.is_integer_dtype(cleaned_data['numberLikes'])
    assert pd.api.types.is_integer_dtype(cleaned_data['exactViewNumber'])
    assert pd.api.types.is_integer_dtype(cleaned_data['numberOfComments'])
    assert pd.api.types.is_integer_dtype(cleaned_data['creatorSubscriberNumber'])


@pytest.fixture
def sample_data():
    # Sample DataFrame for testing
    data = pd.DataFrame({
        'videoId': ['video1', 'video1', 'video2'],
        'videoExactPublishDate': ['2022-01-01 12:00:00', '2022-01-02 12:00:00', '2022-01-01 12:00:00'],
        'scanTimeStamp': [1641139200, 1641225600, 1641139200]
    })
    data = _clean_columns(data)
    return data


@pytest.fixture
def sample_data():
    # Sample DataFrame for testing
    data = pd.DataFrame({
        'videoId': ['video1', 'video1', 'video2'],
        'videoExactPublishDate': pd.to_datetime(
        ['2022-01-01 12:00:00', 
         '2022-01-01 12:00:00', 
         '2022-01-02 12:00:00'], utc=True),
        'scanTimeStamp': pd.to_datetime(
        [1641139200, 1641225600, 1641225600], unit="s", utc=True),
    })
    return data

def test_create_duration_model_columns(sample_data):

    expected_result = pd.DataFrame({
        'videoId': ['video1', 'video1', 'video2'],
        'videoExactPublishDate': pd.to_datetime(
            ['2022-01-01 12:00:00', 
            '2022-01-01 12:00:00', 
            '2022-01-02 12:00:00'], utc=True),
        'scanTimeStamp': pd.to_datetime(
            [1641139200, 1641225600, 1641225600], unit="s", utc=True),
        'firstTrendingTime': pd.to_datetime(
            [1641139200, 1641139200, 1641225600], unit="s", utc=True),
        'timeToTrendSeconds': [100800.0, 100800.0, 100800.0], # 28 hours
        'isTrend': [True, True, False]
    })
    print(pd.to_datetime(1641139200, unit="s") >= pd.to_datetime('2022-01-01 12:00:00'))
    # Selecting only relevant columns for the comparison
    relevant_columns = ['videoId', 'videoExactPublishDate', 'scanTimeStamp',
                        'firstTrendingTime', 'timeToTrendSeconds', 'isTrend']
    result = _create_duration_model_columns(sample_data, frequency='day', delay=1)

    # Checking DataFrame equality for relevant columns
    assert_frame_equal(result[relevant_columns], expected_result[relevant_columns], check_dtype=False)


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])

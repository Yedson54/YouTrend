"""
Testing `utils.py` utility functions (get details from YouTube).

Tests include:
- Extraction of video IDs from different YouTube video URL formats.
- Retrieval of YouTube video category labels.
- Conversion of YouTube video duration from ISO 8601 format to seconds.
- Fetching of YouTube video details using a video link.
"""
import pytest
import pandas as pd
from youtrend.data import API_KEY, VIDEO_CAT_ENCODER
from youtrend.duration_model.utils import (
    get_video_id,
    get_category_labels,
    convert_duration_to_seconds,
    get_video_details
)


def test_get_video_id():
    """
    Test the extraction of video IDs from different YouTube video URL formats.
    """
    # Test case for regular YouTube URL
    link = 'https://www.youtube.com/watch?v=3cYxeaerGoc'
    assert get_video_id(link) == '3cYxeaerGoc'

    # Test case for YouTube short URL
    short_link = 'https://youtu.be/3cYxeaerGoc'
    assert get_video_id(short_link) == '3cYxeaerGoc'

    # Test case for YouTube Shorts URL
    shorts_link = 'https://www.youtube.com/shorts/5eQGjtxsMho'
    assert get_video_id(shorts_link) == '5eQGjtxsMho'

    # Test case for unsupported URL
    unsupported_link = 'https://example.com/video'
    assert get_video_id(unsupported_link) is None


def test_get_category_labels():
    """
    Test the retrieval of YouTube video category labels.
    """
    # Testing the function with the API_KEY variable
    result = get_category_labels(api_key=API_KEY, youtube=None)

    assert isinstance(result, dict)
    assert all(isinstance(category_id, str) for category_id in result.keys())
    assert all(isinstance(label, str) for label in result.values())


def test_convert_duration_to_seconds():
    """
    Test the conversion of YouTube video duration from ISO 8601 format to seconds.
    """
    # Test with a duration string that represents 1 hour, 2 minutes, and 3 seconds
    assert convert_duration_to_seconds("PT1H2M3S") == 3723
    # Test with a duration string that represents 0 hours, 2 minutes, and 3 seconds
    assert convert_duration_to_seconds("PT2M3S") == 123
    # Test with a duration string that represents 1 hour, 0 minutes, and 3 seconds
    assert convert_duration_to_seconds("PT1H3S") == 3603
    # Test with a duration string that represents 1 hour, 2 minutes, and 0 seconds
    assert convert_duration_to_seconds("PT1H2M") == 3720


def test_get_video_details():
    """
    Test the fetching of YouTube video details using a video link.
    """
    # Mock data for a single video link
    video_link = "https://www.youtube.com/watch?v=nKiMp7vrXlY"
    api_key = API_KEY
    video_cat_enc = VIDEO_CAT_ENCODER

    # Call the function
    result_df = get_video_details(
        video_link, api_key, video_cat_enc=video_cat_enc)

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 1
    assert isinstance(result_df["videoExactPublishDate"].iloc[0], pd.Timestamp)
    # assert result_df["videoCategory"].str.isalpha().all()
    assert any(result_df.columns.str.startswith("videoCat_"))


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
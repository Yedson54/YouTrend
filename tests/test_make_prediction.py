from unittest.mock import Mock

import pytest
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
from youtrend.duration_model.make_prediction import (
    _normalize,
    survival_probability,
    plot_survival_probability,
    _kmf_model_per_day_and_video_cat,
    plot_survival_probabilities_by_group
)

@pytest.mark.parametrize("series, data_max, data_min, expected", [
    (pd.Series([1, 2, 3, 4, 5]), 4, 2, np.array([0., 0., 0.5, 1., 1.5])),
    # Add more test cases if needed
])
def test_normalize(series, data_max, data_min, expected):
    result = _normalize(series, data_max, data_min)
    np.testing.assert_array_equal(result, expected)

def test_survival_probability():
    video_link = "https://www.youtube.com/watch?v=wuxW7X2BHJY"
    result = survival_probability(video_link)
    assert isinstance(result, float)

def test_plot_survival_probability():
    # Mocking plt.show() to prevent displaying plots during tests
    show_mock = Mock()
    original_show = plt.show
    plt.show = show_mock

    start_date = "2022-01-01"
    duration_days = 5
    gap = 0.5
    video_link = "https://www.youtube.com/watch?v=wuxW7X2BHJY"
    
    # The actual test checks if an exception is raised or not
    plot_survival_probability(start_date, duration_days, gap, video_link)

    # Assert that plt.show() was called
    show_mock.assert_called_once()

    # Restore the original plt.show()
    plt.show = original_show

def test__kmf_model_per_day_and_video_cat():
    # Mock data
    day = "Monday"
    category = "Comedy"
    full_df = pd.DataFrame({
        'videoLengthDays': [1, 2, 3, 4, 5],
        'isTrend': [0, 1, 1, 0, 1],
        'dayOfWeek': ['Monday', 'Monday', 'Monday', 'Monday', 'Monday'],
        'videoCategory': ['Comedy'] * 5
    })

    # The actual test
    kmf_model, returned_category = _kmf_model_per_day_and_video_cat(day, category, full_df)

    # Assertions
    assert isinstance(kmf_model, KaplanMeierFitter)
    assert returned_category == category

def test_plot_survival_probabilities_by_group():
    # Mocking plt.show() to prevent displaying plots during tests
    show_mock = Mock()
    original_show = plt.show
    plt.show = show_mock

    # Mock data
    day_list = ["Monday", "Tuesday", "Wednesday"]
    category = "Comedy"

    # The actual test checks if an exception is raised or not
    plot_survival_probabilities_by_group(day_list, category)

    # Assert that plt.show() was called
    show_mock.assert_called_once()

    # Restore the original plt.show()
    plt.show = original_show

# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])

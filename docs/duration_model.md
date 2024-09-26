## Duration Model: Navigating YouTube Trending Probabilities

Welcome to the Duration Model, where we embark on a journey through three main sections – **Process Data**, **Make Prediction**, and **Utility**. This module is designed to analyze the likelihood of a video entering the trending list and the probability of it not gaining traction. Let's explore each section step by step.



### Make Prediction

Welcome to the heart of the Duration Model – the **Make Prediction** section. This module provides robust functions for analyzing the probability of YouTube videos not reaching the trending section based on various features, including video length, creator's subscriber count, and publication date.

#### Functions:

#####  `survival_probability(video_link, date, api_key, region_code, video_cat_enc)`

Calculate the survival probability for a video.

- **Parameters:**
  - `video_link`: The link to the video.
  - `date`: Date for calculating the survival probability.
  - `api_key`: YouTube Data API key.
  - `region_code`: Region code for fetching category labels.
  - `video_cat_enc`: One-hot encoder for video categories.

- **Returns:** Survival probability as a float.

##### `plot_survival_probability(single_df, start_date, duration_days, gap, video_link, api_key, region_code, video_cat_enc)`

Plot the survival probability over a specified duration for a given video.

- **Parameters:**
  - `single_df`: DataFrame containing details of a single video.
  - `start_date`: Starting date for the survival probability calculation.
  - `duration_days`: Duration for which survival probability is calculated.
  - `gap`: Time gap between survival probability points.
  - `video_link`: The link to the video.
  - `api_key`: YouTube Data API key.
  - `region_code`: Region code for fetching category labels.
  - `video_cat_enc`: One-hot encoder for video categories.

- **Returns:** X and Y coordinates for plotting the survival probability.

#### How to Use the Prediction Module:

1. **Survival Probability Calculation:**
   - Use `survival_probability` function to calculate the survival probability for a specific video based on its features.

   ```python
   prob = survival_probability(
       video_link="your_video_link",
       date="2023-01-01",
       api_key="your_api_key",
       region_code="US",
       video_cat_enc=VIDEO_CAT_ENCODER
   )
   ```

2. **Plotting Survival Probability:**
   - Utilize `plot_survival_probability` function to visualize the survival probability over a specified duration for a given video.

   ```python
   x, y = plot_survival_probability(
       single_df=your_single_video_data_frame,
       start_date="2023-01-01",
       duration_days=30,
       gap=1,
       video_link="your_video_link",
       api_key="your_api_key",
       region_code="US",
       video_cat_enc=VIDEO_CAT_ENCODER
   )
   ```

Unlock the potential of predicting YouTube trending probabilities with precision using YouTrend's Duration Model. Leverage these functions to make informed decisions about your content strategy and optimize your chances of reaching the trending list!

## Utility Functions

Ladies and gentlemen, let's dive into the powerhouse of the Duration Model - the **Utility Module**. This module is the backbone, providing essential functions for extracting, processing, and analyzing YouTube video data. It's the wizard behind the scenes, making predictions about the survival probability of a video on the platform.

### Main Functions:

#### `get_video_details(video_link, api_key, region_code, video_cat_enc) -> pd.DataFrame`

   Fetches comprehensive details of a YouTube video using its link.

   - **Parameters:**
     - `video_link`: The link to the YouTube video.
     - `api_key`: Your YouTube Data API key.
     - `region_code`: The region code for fetching category labels. Default is "US".
     - `video_cat_enc`: Optional OneHotEncoder for video categories.

   - **Returns:** DataFrame containing rich information about the YouTube video.

#### `get_video_id(video_link) -> str`

   Extracts the video ID from a YouTube video link.

   - **Parameters:**
     - `video_link`: The YouTube video link.

   - **Returns:** The extracted video ID as a string.

#### `preprocessing(filename, dataframe, on_loading, video_cat_enc) -> Tuple[pd.DataFrame, Optional[List[str]], Optional[OneHotEncoder]]`

   Processes the input data for the machine learning model.

   - **Parameters:**
     - `filename`: Path to the CSV file containing the data.
     - `dataframe`: DataFrame containing the data.
     - `on_loading`: A boolean indicating whether the preprocessing is during loading.
     - `video_cat_enc`: OneHotEncoder for later preprocessing before predictions.

   - **Returns:**
     - `df`: Processed DataFrame.
     - `model_features`: List of features for the duration model.
     - `encoder`: OneHotEncoder for later preprocessing before predictions.

#### `get_category_labels(api_key, region_code, youtube) -> Dict[str, str]`

   Retrieves YouTube video category labels.

   - **Parameters:**
     - `api_key`: Your YouTube Data API key.
     - `region_code`: The region code for fetching category labels. Default is 'US'.
     - `youtube`: Optional. The YouTube API service object.

   - **Returns:** Dictionary mapping category IDs to category labels.

#### `convert_duration_to_seconds(duration) -> int`

   Converts YouTube video duration from ISO 8601 format to seconds.

   - **Parameters:**
     - `duration`: Duration string in ISO 8601 format.

   - **Returns:** Duration in seconds.

#### 6. `get_channel_subscriber_count(api, channel_ids) -> Optional[int]`

   Retrieves subscriber count for YouTube channels.

   - **Parameters:**
     - `api`: The YouTube API service object.
     - `channel_ids`: List of YouTube channel IDs.

   - **Returns:** The subscriber count or None if an error occurs.

### Global Constants:

- `API_KEY (str)`: YouTube Data API key.

And there you have it, the robust and versatile Utility Module, an indispensable part of our Duration Model. Let's give a round of applause for these functions that work tirelessly behind the scenes, making our predictions accurate and our analysis impeccable! 🚀✨
## Scraper: Unleashing the Power of YouTube Trending Data

Welcome to the heart of YouTrend's data-gathering prowess – the Scraper module. This essential component empowers you to delve deep into the YouTube trending landscape by collecting and parsing data from the Google YouTube API. Harnessing the capabilities of Python, requests, and pandas, our Scraper module ensures you have access to a rich dataset, enabling you to derive valuable insights and make informed decisions.

### Key Functions:

#### `post_request_ytb(country_code_list, trending_type_dict)`
- Post an HTTP request to retrieve generic data about trending videos on YouTube.
- **Parameters:**
  - `country_code_list`: List of countries from which to retrieve trending videos.
  - `trending_type_dict`: Dictionary of different video categories to retrieve.
- **Returns:** Dictionary containing the response to the HTTP request.

#### `collect_video_data(video_list, data_dictionary, trending_type, country_code)`
- Parse generic video data given an input list of videos previously collected.
- **Parameters:**
  - `video_list`: List of videos retrieved using the `post_request_ytb` function.
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
  - `trending_type`: Code corresponding to different categories in trending videos.
  - `country_code`: Code corresponding to the country from which the videos are scraped.
- **Returns:** None.

#### `collect_short_data(shorts_list, data_dictionary, country_code)`
- Parse generic short data given an input list of shorts previously collected.
- **Parameters:**
  - `shorts_list`: List of shorts retrieved using the `post_request_ytb` function.
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
  - `country_code`: Code corresponding to the country from which the videos are scraped.
- **Returns:** None.

#### `add_now_videos_shorts(response_dict, data_dictionary)`
- Update the `data_dictionary` dictionary with trending videos and shorts from YouTube.
- **Parameters:**
  - `response_dict`: Dictionary containing the response to the HTTP post request.
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
- **Returns:** None.

#### `add_other_sections(response_dict, data_dictionary)`
- Update the `data_dictionary` dictionary with trending videos from categories other than "Now."
- **Parameters:**
  - `response_dict`: Dictionary containing the response to the HTTP post request.
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
- **Returns:** None.

#### `update_video_data(data_dictionary)`
- Update `data_dictionary` in place with information on individual videos.
- **Parameters:**
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
- **Returns:** None.

#### `update_meta_data(data_dictionary)`
- Update `data_dictionary` in place with metadata information on individual videos.
- **Parameters:**
  - `data_dictionary`: Dictionary containing YouTube data to be updated in place.
- **Returns:** None.

### How to Run the Scraper Script:

1. Create an empty `data_dictionary` to be filled.
2. Fill it with YouTube ID information and other basic information using `post_request_ytb`, `add_now_videos_shorts`, and `add_other_sections` functions.
3. Update the `data_dictionary` with individual data by calling `update_video_data` and `update_meta_data` functions.
4. Create the corresponding `.csv` file within the `/data` directory.

Unleash the power of data-driven decision-making with YouTrend's Scraper module. Dive into the world of YouTube trending with confidence!
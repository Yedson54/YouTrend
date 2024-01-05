import requests
import numpy as np
import pandas as pd
import time


TRENDING_TYPE_DICT = {
    'Now': None,
    'Music': '4gINGgt5dG1hX2NoYXJ0cw%3D%3D',
    'Gaming': '4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D',
    'Movie': '4gIKGgh0cmFpbGVycw%3D%3D',
}

ENGLISH_COUNTRY_CODE_LIST = ['US', 'CA', 'AU']
FRENCH_COUNTRY_CODE_LIST = ['FR']

DATA_DICTIONARY_TEMPLATE =  { # Will be filled inplace
    "videoTitle": [],
    "videoId": [],
    "videoThumbnailUrl": [],
    "videoDescriptionSnippet": [],
    "videoRelativePublishedTimeText": [],
    "videoLength": [],
    "videoViewCountText": [],
    "videoCreatorName": [],
    "videoType": [],
    "trendingCountry": [],
    "exactViewNumber": [],
    "numberLikes": [],
    "videoDate": [],
    "creatorSubscriberNumber": [],
    "videoVerboseDescription": [],
    "numberOfComments": [],
    "isCreatorVerified": [],
    "videoKeywords": [],
    "videoLengthSeconds": [],
    "videoIsLiveContent": [],
    "videoCategory": [],
    "isFamilySafe": [],
    "videoExactPublishDate": [],
    "creatorUrl": []
}


def post_request_ytb(country_code_list, trending_type_dict):
    """
    Post an HTTP request to retrieve generic data about videos trending on YouTube

    Args:
        country_code_list (List): list of countries from which to retrieve the trending videos
        trending_type_dict (Dict): dictionary of different video categories to retrieve

    Returns:
        Dict: dictionary containing the response to the HTTP request
    """
    responses_dict = {}
    for country_code in country_code_list:
        responses_dict[country_code] = {}
        for trending_type, trending_type_url in trending_type_dict.items():
            json_data = {
                'context': {
                    'client': {
                        'gl': country_code,
                        'clientName': 'WEB',
                        'clientVersion': '2.20231115.01.01',
                        'originalUrl': 'https://www.youtube.com/feed/trending',
                    },
                },
                'browseId': 'FEtrending',
                'params': trending_type_url,
            }

            response = requests.post(
                'https://www.youtube.com/youtubei/v1/browse',
                json=json_data,
            )
            responses_dict[country_code][trending_type] = response.json()
            time.sleep(1)
    return responses_dict        


def collect_video_data(video_list, data_dictionary, trending_type, country_code):
    """
    Parse generic video data given an input list of videos that were previously collected
    Args:
        video_list (List): list of videos that are retrieved using the post_request_ytb function
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace
        trending_type (str): code that corresponds to the different categories in the trending videos
        country_code (str): code that corresponds to the country from which the videos are scraped from

    Returns:
        None
    """
    nb_items = len(video_list)
    data_dictionary["videoTitle"] += [video_list[k]["videoRenderer"]["title"]["runs"][0]["text"] for k in range(nb_items)]
    data_dictionary["videoId"] += [video_list[k]["videoRenderer"]["videoId"] for k in range(nb_items)]
    data_dictionary["videoThumbnailUrl"] += [video_list[k]["videoRenderer"]["thumbnail"]["thumbnails"][2]["url"] for k in range(nb_items)]
    for k in range(nb_items):
        try:
            data_dictionary["videoDescriptionSnippet"].append(video_list[k]["videoRenderer"]["descriptionSnippet"]["runs"][0]['text'])
        except KeyError:
            data_dictionary["videoDescriptionSnippet"].append(np.nan)
    data_dictionary["videoRelativePublishedTimeText"] += [video_list[k]["videoRenderer"]["publishedTimeText"]['simpleText'] for k in range(nb_items)]
    data_dictionary["videoLength"] += [video_list[k]["videoRenderer"]["lengthText"]["simpleText"] for k in range(nb_items)]   
    data_dictionary["videoViewCountText"] += [video_list[k]["videoRenderer"]["viewCountText"]["simpleText"] for k in range(nb_items)]
    data_dictionary["videoCreatorName"] += [video_list[k]["videoRenderer"]["ownerText"]["runs"][0]["text"] for k in range(nb_items)]
    data_dictionary["videoType"] += [trending_type for k in range(nb_items)]
    data_dictionary["trendingCountry"] += [country_code for k in range(nb_items)]
    return None


def collect_short_data(shorts_list, data_dictionary, country_code):
    """
    Parse generic short data given an input list of shorts that were previously collected
    Args:
        shorts_list (List): list of shorts that are retrieved using the post_request_ytb function
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace
        country_code (str): code that corresponds to the country from which the videos are scraped from

    Returns:
        None
    """    
    nb_items = len(shorts_list)
    data_dictionary["videoTitle"] += [shorts_list[k]["reelItemRenderer"]["headline"]["simpleText"] for k in range(nb_items)]
    data_dictionary["videoId"] += [shorts_list[k]["reelItemRenderer"]["videoId"] for k in range(nb_items)]
    data_dictionary["videoThumbnailUrl"] += [shorts_list[k]["reelItemRenderer"]["thumbnail"]["thumbnails"][0]["url"] for k in range(nb_items)]
    data_dictionary["videoDescriptionSnippet"] += [np.nan for k in range(nb_items)]
    data_dictionary["videoRelativePublishedTimeText"] += [np.nan for k in range(nb_items)]
    data_dictionary["videoLength"] += [np.nan for k in range(nb_items)]   
    data_dictionary["videoViewCountText"] += [shorts_list[k]["reelItemRenderer"]["viewCountText"]["simpleText"] for k in range(nb_items)]
    data_dictionary["videoCreatorName"] += [np.nan for k in range(nb_items)]
    data_dictionary["videoType"] += ['Short' for k in range(nb_items)]
    data_dictionary["trendingCountry"] += [country_code for k in range(nb_items)]
    return None

def add_now_videos_shorts(response_dict, data_dictionary):
    """
    Update the data_dictionary dictionary with trending videos and shorts from YouTube

    Args:
        response_dict (Dict): the dictionary containing the response to the HTTP post request
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace

    Returns:
        None
    """
    for country_code in response_dict.keys():
        print("Current country : ", country_code)
        section_now = response_dict[country_code]['Now']["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
        try:
            list_videos_before = section_now[0]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
            shorts_list = section_now[1]["itemSectionRenderer"]["contents"][0]["reelShelfRenderer"]["items"]
            list_videos_after = section_now[2]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
            list_videos_recently = section_now[3]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
        except KeyError:
            list_videos_before = section_now[1]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
            shorts_list = section_now[2]["itemSectionRenderer"]["contents"][0]["reelShelfRenderer"]["items"]
            list_videos_after = section_now[3]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
            list_videos_recently = section_now[4]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
        collect_video_data(list_videos_before, data_dictionary, 'Now', country_code)
        collect_video_data(list_videos_after, data_dictionary, 'Now', country_code)
        collect_video_data(list_videos_recently, data_dictionary, 'Recently Trending', country_code)
        collect_short_data(shorts_list, data_dictionary, country_code)
    return None


def add_other_sections(response_dict, data_dictionary):
    """
    Update the data_dictionary dictionary with trending videos from categories other than "Now"

    Args:
        response_dict (Dict): the dictionary containing the response to the HTTP post request
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace

    Returns:
        None
    """    
    for country_code in response_dict.keys():
        for idx, key in enumerate(response_dict[country_code].keys()): # in recent Python versions, dictionary are ordered
            if idx != 0:
                sections = response_dict[country_code][key]["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][idx]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
                video_list = sections[0]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
                collect_video_data(video_list, data_dictionary, key, country_code)
    return None


def update_video_data(data_dictionary):
    """
    Update data_dictionary inplace with information on individual videos

    Args:
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace

    Returns:
        None
    """

    for video_id in data_dictionary["videoId"]:
        print("Currently processing video_id:", video_id)
        json_data = {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20231208.01.00',            
                    }
            },
            'videoId': video_id,
        }
        
        response = requests.post('https://www.youtube.com/youtubei/v1/next', json=json_data)
        video_response = response.json()
        individual_video_data = video_response["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]
        data_dictionary["exactViewNumber"].append(individual_video_data[0]["videoPrimaryInfoRenderer"]["viewCount"]["videoViewCountRenderer"]["viewCount"]["simpleText"])
        data_dictionary["numberLikes"].append(individual_video_data[0]["videoPrimaryInfoRenderer"]["videoActions"]["menuRenderer"]["topLevelButtons"][0]["segmentedLikeDislikeButtonViewModel"]["likeButtonViewModel"]["likeButtonViewModel"]["toggleButtonViewModel"]["toggleButtonViewModel"]["defaultButtonViewModel"]["buttonViewModel"]["title"])
        data_dictionary["videoDate"].append(individual_video_data[0]["videoPrimaryInfoRenderer"]["dateText"]["simpleText"])
        data_dictionary["creatorSubscriberNumber"].append(individual_video_data[1]["videoSecondaryInfoRenderer"]["owner"]["videoOwnerRenderer"]["subscriberCountText"]["simpleText"])
        try:
            data_dictionary["videoVerboseDescription"].append(individual_video_data[1]["videoSecondaryInfoRenderer"]["attributedDescription"]["content"])
        except KeyError: # no description available
            data_dictionary["videoVerboseDescription"].append(np.nan)
        try:    
            data_dictionary["numberOfComments"].append(individual_video_data[2]["itemSectionRenderer"]["contents"][0]["commentsEntryPointHeaderRenderer"]["commentCount"]["simpleText"])
        except KeyError: # correct for additional "merchandise" section
            try:
                data_dictionary["numberOfComments"].append(individual_video_data[3]["itemSectionRenderer"]["contents"][0]["commentsEntryPointHeaderRenderer"]["commentCount"]["simpleText"])
            except IndexError: # comments are turned off
                data_dictionary["numberOfComments"].append(np.nan)
        try:
            data_dictionary["isCreatorVerified"].append(individual_video_data[1]["videoSecondaryInfoRenderer"]["owner"]["videoOwnerRenderer"]["badges"][0]["metadataBadgeRenderer"]["tooltip"] == "Verified")
        except KeyError:
            data_dictionary["isCreatorVerified"].append(False)    
        time.sleep(1)
    return None


def update_meta_data(data_dictionary):
    """
    Update data_dictionary inplace with metadata information on individual videos

    Args:
        data_dictionary (Dict): the dictionary containing the YouTube data to be updated inplace

    Returns:
        None
    """
    for video_id in data_dictionary["videoId"]:
        print("Currently processing video_id:", video_id)
        json_data = {
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20231208.01.00',
            },
        },
        'videoId': video_id,
        }
        
        response = requests.post('https://www.youtube.com/youtubei/v1/player', json=json_data)
        
        meta_response = response.json()
        try:
            data_dictionary["videoKeywords"].append(meta_response["videoDetails"]["keywords"])
        except KeyError: # no keywords
            data_dictionary["videoKeywords"].append(np.nan)
        data_dictionary["videoLengthSeconds"].append(meta_response["videoDetails"]["lengthSeconds"])
        data_dictionary["videoIsLiveContent"].append(meta_response["videoDetails"]["isLiveContent"])
        data_dictionary["videoCategory"].append(meta_response["microformat"]["playerMicroformatRenderer"]["category"])
        data_dictionary["isFamilySafe"].append(meta_response["microformat"]["playerMicroformatRenderer"]["isFamilySafe"])
        data_dictionary["creatorUrl"].append(meta_response["microformat"]["playerMicroformatRenderer"]["ownerProfileUrl"])
        data_dictionary["videoExactPublishDate"].append(meta_response["microformat"]["playerMicroformatRenderer"]["uploadDate"])
        time.sleep(1)
    return None


# How to run this script :
# 1) Create an empty data_dictionary to be filled
# 2) Fill it with the youtube_id information, and with other basic information using 
# 2  post_request_ytb, add_now_videos_shorts and add_other_sections functions
# 3) Update the data_dictionary with individual data by calling update_video_data and _update_meta_data functions
# 4) Create the corresponding .csv file within the /data directory


# 1
french_data_dictionary = {
"videoTitle": [],
"videoId": [],
"videoThumbnailUrl": [],
"videoDescriptionSnippet": [],
"videoRelativePublishedTimeText": [],
"videoLength": [],
"videoViewCountText": [],
"videoCreatorName": [],
"videoType": [],
"trendingCountry": [],
"exactViewNumber": [],
"numberLikes": [],
"videoDate": [],
"creatorSubscriberNumber": [],
"videoVerboseDescription": [],
"numberOfComments": [],
"isCreatorVerified": [],
"videoKeywords": [],
"videoLengthSeconds": [],
"videoIsLiveContent": [],
"videoCategory": [],
"isFamilySafe": [],
"videoExactPublishDate": [],
"creatorUrl": []
}

# 2

response_dict = post_request_ytb(FRENCH_COUNTRY_CODE_LIST, TRENDING_TYPE_DICT)
add_now_videos_shorts(response_dict, french_data_dictionary)
add_other_sections(response_dict, french_data_dictionary)

# 3

update_video_data(french_data_dictionary)
update_meta_data(french_data_dictionary)

# 4
trending_df = pd.DataFrame(french_data_dictionary)
trending_df.to_csv("../data/french_youtube_today.csv")
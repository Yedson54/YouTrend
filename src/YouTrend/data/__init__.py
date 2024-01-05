"""
This module is used for loading and preprocessing data for the YouTube trend 
duration model.

It includes functionality to load a trained model and its associated data, as 
well as a video category encoder. The module also provides the ability to 
preprocess data on loading.

Environment Variables:
    - YOUTUBE_API_KEY: The API key for making Google YouTube API calls.

Functions:
    - load_pickle(file_path: str) -> Any: Loads a pickle file from the given 
        file path.
    - load the model, video category encoder, and preprocess data.
"""
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

from youtrend.duration_model.process_data import preprocessing_on_loading # noqa: E0401

def load_pickle(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)

base_folder = Path(__file__).resolve().parent

# Load environment variables
load_dotenv()

# Key for Google YouTube api calls.
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Load model.
MODEL = load_pickle(base_folder / "duration_model.pickle")

# Load video_category encoder.
VIDEO_CAT_ENCODER = load_pickle(base_folder / "video_category_encoder.pickle")

# Load data, model features list and category encoder.
DURATION_MODEL_DF, MODEL_FEATURES, VIDEO_CAT_ENCODER = (
    preprocessing_on_loading(base_folder / 'duration_model_data.csv')
)

import pickle
from pathlib import Path

from youtrend.duration_model.process_data import preprocessing_on_loading # noqa: E0401

base_folder = Path(__file__).resolve().parent

# Key for Google YouTube api calls.
API_KEY = "AIzaSyCkx5_g8o7bYQkra1_IGYE8LNxHO5yEsAk"

# Load model.
with open(base_folder / "duration_model.pickle", "rb") as f:
    MODEL = pickle.load(f)

# Load video_category encoder.
with open(base_folder / "video_category_encoder.pickle", "rb") as f:
    VIDEO_CAT_ENCODER = pickle.load(f)

# Load data, model features list and category encoder.
DURATION_MODEL_DF, MODEL_FEATURES, VIDEO_CAT_ENCODER = preprocessing_on_loading(
    base_folder / 'duration_model_data.csv'
)

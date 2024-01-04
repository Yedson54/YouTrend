"""
Load 
- from parent directory, load "data/duration_model.pickle" as DURATION_MODEL
- from parent directory, load "data/duration_model_data.csv" as
DURATION_MODEL_DF using make_prediction.preprocessing function
- from parent directory, load "data/video_category_encoder.pickle" as
VIDEO_CAT_ENCODER
"""
from pathlib import Path
import json

base_folder = Path(__file__).resolve().parent

# Load synonyms
# TODO: make loading synonyms prettier and more flexible
# with open(base_folder / "data" / "en_synonyms.json", encoding="utf-8") as f:
#     SYNONYM_DICT = {"en": json.load(f)}

# # List supported languages
# SUPPORTED_LANGUAGES = list(SYNONYM_DICT.keys())
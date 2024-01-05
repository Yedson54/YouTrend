import pickle

with open("pages/data/duration_model.pickle", "rb") as f:
    MODEL = pickle.load(f)
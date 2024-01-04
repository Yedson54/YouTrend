# """Tests suite for duratio model processing operation. 
# """
# import pytest
# import numpy as np
# import pandas as pd

# from YouTrend.duration_model import load_data


# # Loads data from a folder with default filenames.
# def test_load_data_default_filenames(self):
#     # Arrange
#     folder = "data_folder"

#     # Act
#     result = load_data(folder)

#     # Assert
#     assert isinstance(result, pd.DataFrame)
#     assert len(result) > 0

# # Loads data from a folder with specified filenames.
# def test_load_data_specified_filenames(self):
#     # Arrange
#     folder = "data_folder"
#     filenames = ["file1.csv", "file2.csv"]

#     # Act
#     result = load_data(folder, use_filenames=True, filenames=filenames)

#     # Assert
#     assert isinstance(result, pd.DataFrame)
#     assert len(result) > 0

# def test_load_data_folder_not_exist(self):
#     # Arrange
#     folder = "nonexistent_folder"

#     # Act and Assert
#     with pytest.raises(FileNotFoundError):
#         load_data(folder)

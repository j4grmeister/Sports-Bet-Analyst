import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import csv
import logging

import statsapi

from data.datasets.MLBDataset import MLBDataset

import ui

if __name__ == "__main__":
    logging.basicConfig(filename="logs/build_dataset.log", level=logging.INFO)
    
    dataset = MLBDataset()
    dataset.build_dataset("data/training_dataset.csv", "01/01/2024", "01/01/2025", verbose=True)

    #build_mlb_dataset("data/training_dataset.csv", "01/01/2024", "01/01/2025", verbose=True)
    #build_mlb_dataset("data/test_dataset.csv", "07/25/2025", "08/09/2025", verbose=True)
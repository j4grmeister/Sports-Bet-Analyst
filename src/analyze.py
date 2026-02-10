import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

if __name__ == "__main__":
    dataset_filename = "MLBModel/training_dataset.csv"
    df = pd.read_csv(dataset_filename)
    df = df.drop("datetime", axis=1)

    # correlation plot
    corr = df.corr()
    #display(corr.style.background_gradient(cmap='coolwarm'))
    plt.matshow(corr)
    plt.show()


    """
    # histograms for each feature
    for col in df.columns:
        plt.figure()
        plt.title(f'{col}')
        plt.hist(df[col])
    plt.show()

    #box plots for each feature
    for column in df:
        plt.figure()
        df.boxplot([column])
    plt.show()
    """
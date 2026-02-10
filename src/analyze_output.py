import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

if __name__ == "__main__":
    dataset_filename = "MLBModel/bets_analysis.csv"
    df = pd.read_csv(dataset_filename)
    df = (df.drop("date", axis=1)
          .drop("bankroll_start", axis=1)
          .drop("home_team", axis=1)
          .drop("away_team", axis=1)
          .drop("home_odds", axis=1)
          .drop("away_odds", axis=1)
          .drop("bet_amount", axis=1)
          .drop("payout", axis=1)
          .drop("kelly_fraction", axis=1)
          .drop("game_outcome", axis=1)
          .drop("bankroll_final", axis=1)
    )

    wins = df[df["bet_outcome"] == 1]
    wins = wins.drop("bet_outcome", axis=1)
    losses = df[df["bet_outcome"] == 0]
    losses = losses.drop("bet_outcome", axis=1)

    """
    # correlation plot
    corr = df.corr()
    #display(corr.style.background_gradient(cmap='coolwarm'))
    plt.matshow(corr)
    plt.show()
    """


    # histograms for each feature
    for col in wins.columns:
        plt.figure()
        plt.title(f'{col} - wins')
        plt.hist(wins[col])
    # histograms for each feature
    for col in losses.columns:
        plt.figure()
        plt.title(f'{col} - losses')
        plt.hist(losses[col])
    plt.show()

    """
    #box plots for each feature
    for column in df:
        plt.figure()
        df.boxplot([column])
    plt.show()
    """
from typing import Counter
import bs4 as bs
import pickle
import requests
import os
import datetime as dt
import pandas_datareader.data as web
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
from collections import Counter
from sklearn import svm, neighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from statistics import mean

# Process data.
def process_data_for_labels(ticker):
    hm_days = 7
    df = pd.read_csv("sp500_joined_closes.csv", index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)
    for i in range(1, hm_days+1):
        df[f"{ticker}_{i}d"] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]
    df.fillna(0, inplace=True)
    return tickers, df

# Tells if you should buy, sell or hold.
def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0

# Creates the target column (label).
def extract_featuresets(ticker):
    tickers, df = process_data_for_labels(ticker)
    df[f"{ticker}_target"] = list(map( buy_sell_hold,
                                       df[f"{ticker}_1d"],
                                       df[f"{ticker}_2d"],
                                       df[f"{ticker}_3d"],
                                       df[f"{ticker}_4d"],
                                       df[f"{ticker}_5d"],
                                       df[f"{ticker}_6d"],
                                       df[f"{ticker}_7d"]))
    vals = df[f"{ticker}_target"].values.tolist()
    str_vals = [str(i) for i in vals]
    print("Data spread: ", Counter(str_vals))
    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(0, inplace=True)
    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)
    X = df_vals.values
    y = df[f"{ticker}_target"].values
    return X,y,df

# Machine learning.
def do_ml(ticker):
    X, y, df = extract_featuresets(ticker)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    clf = VotingClassifier([("lsvc", svm.LinearSVC()),
                            ("knn", neighbors.KNeighborsClassifier()),
                            ("rfor", RandomForestClassifier())])
    clf.fit(X_train, y_train)
    confidence = clf.score(X_test, y_test)
    print("Accuracy: ", confidence)
    predictions = clf.predict(X_test)
    print("Predicted class counts: ", Counter(predictions))
    return confidence


def ml_stock_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    accuracies = []
    for count, ticker in enumerate(tickers):
        if count % 10 == 0:
            print(count)
        accuracy = do_ml(ticker)
        accuracies.append(accuracy)
        print(f"{ticker} accuracy: {accuracy}. Average accuracy: {mean(accuracies)}\n")
        if ticker != tickers[-1]:
            print()

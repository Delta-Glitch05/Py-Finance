import bs4 as bs
import pickle
from pandas.core.indexes.api import get_objs_combined_axis
import requests
import os
import datetime as dt
import pandas_datareader.data as web
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import _thread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
import sys
import time

"""
TIME_LIMIT = 100
progVar = 0
class External(QThread):
    # Runs a counter thread.
    countChanged = pyqtSignal(int)
    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count = progVar
            time.sleep(0.2)
            print(count)
            self.countChanged.emit(count)
"""
visualize_data_bool = False
class Actions(QDialog):
    """
    Simple dialog that consists of a Progress Bar and a Button.
    Clicking on the button results in the start of a timer and
    updates the progress bar.
    """
    def __init__(self, comp_data_bool):
        super().__init__()
        self.comp_data_bool = comp_data_bool
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Progress Bar')
        self.setGeometry(650, 500, 305, 60)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(2.5, 2.5, 300, 25)
        self.progress.setMaximum(100)
        self.start_button = QPushButton('Start', self)
        self.start_button.move(10, 30)
        # self.arrest_button = QPushButton('Arrest', self)
        # self.arrest_button.move(215, 30)
        self.setFixedSize(305, 60)
        self.show()
        self.start_button.clicked.connect(self.onButtonClick)
        # self.arrest_button.clicked.connect(lambda: self.reject())

    def onButtonClick(self):
        self.start_button.setEnabled(False)
        self.get_data_from_yahoo()
        if self.comp_data_bool:
            self.compile_data()

    def onCountChanged(self, value):
        self.progress.setValue(value)

    # Gets all the tickers of the S&P 500 members.
    def save_sp500_tickers(self):
        resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text[:-1]
            tickers.append(ticker)
        with open('sp500tickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)
        return tickers

    # Gets the stocks for every ticker from Yahoo.
    def get_data_from_yahoo(self, reload_sp500=False):
        if reload_sp500:
            tickers = self.save_sp500_tickers()
        else:
            with open('sp500tickers.pickle', 'rb') as f:
                tickers = pickle.load(f)
        if not os.path.exists('stock_dfs'):
            os.mkdir('stock_dfs')
        start = dt.datetime(2010, 1, 1)
        end = dt.datetime.now()
        for ticker in tickers:
            ticker = ticker.replace('.', '-')
            if not os.path.exists(f'stock_dfs/{ticker}.csv'):
                df = web.DataReader(ticker, 'yahoo', start, end)
                df.reset_index(inplace=True)
                df.set_index('Date', inplace=True)
                df.to_csv(f'stock_dfs/{ticker}.csv')
            else:
                # print(f'Already have {ticker}')
                pass
        #self.compile_data()

    # Takes the Adjusted Close column and removes all the others.
    def compile_data(self):
        global visualize_data_bool
        progVar = 0
        with open('sp500tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)
        main_df = pd.DataFrame()
        for count, ticker in enumerate(tickers):
            ticker = ticker.replace('.', '-')
            df = pd.read_csv(f'stock_dfs/{ticker}.csv')
            df.set_index('Date', inplace=True)
            df.rename(columns={'Adj Close': ticker}, inplace=True)
            df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)
            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')
            if count % 10 == 0:
                if(count != 0):
                    progVar += 2
                    self.progress.setValue(progVar)
        print(main_df.head())
        main_df.to_csv('sp500_joined_closes.csv')
        visualize_data_bool = True
        self.reject()

    # Creates the correlation table and displays it.
def visualize_data():
    global visualize_data_bool
    visualize_data_bool = False
    df = pd.read_csv('sp500_joined_closes.csv')
    df_corr = df.corr()
    print(df_corr.head())
    df_corr.to_csv('sp500corr.csv')
    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1,1,1)
    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)
    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1,1)
    plt.tight_layout()
    # plt.savefig('correlations.png', dpi = (300))
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(550,250,640, 545)
    mngr.set_window_title("Py Finance")
    plt.show()

# Executes all the functions.
def get_SP500(comp_data_bool=True):
    window = Actions(comp_data_bool)
    window.exec()
    if visualize_data_bool:
        visualize_data()

import sys
import os
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.window.rolling import Window
import pandas_datareader.data as web
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QAbstractTableModel, Qt
from getStockPrices import pandasModel, get_columns
from tableWind import TableWind

def show_table(self, df):
    self.table = QTableView()
    self.model = pandasModel(df)
    self.table.setModel(self.model)
    self.w2 = TableWind(self.table)
    self.w2.show()


def readStockPricesFile(self, tag):
    continue_1 = True
    style.use('ggplot')
    while continue_1:
        csvFile, ok = QInputDialog.getText(self, 'input dialog', 'Insert the name of the file: ')
        fileExt = '.csv'
        if ok:
            continue_2 = True
            if csvFile[-4:] != fileExt:
                for i in csvFile:
                    if i == '.':
                        error_dialog = QErrorMessage()
                        error_dialog.showMessage('The file has not a valid extension!')
                        error_dialog.exec_()
                        continue_2 = False
                        break
                csvFile += fileExt
            if continue_2:
                if os.path.exists(csvFile):
                    df = pd.read_csv('tsla.csv', parse_dates=True, index_col=0)
                    print('\n--------HEAD--------\n')
                    print(df.head(6))
                    print('\n--------TAIL--------\n')
                    print(df.tail(6))
                    print('\n')
                    if self.showPlot and tag == None:
                        while True:
                            col_list = ['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']
                            col_list_str = str(col_list)
                            col_list_str = col_list_str[:33] + ' \n' + col_list_str[33:]
                            if self.normalGraph.isChecked():
                                col, ok = QInputDialog.getText(self, 'input dialog', f'Insert the name of the column/s to graph {col_list_str} (if more than one, separate with \'-\', for all: \'All\'): ')
                                if ok:
                                    if col.strip().lower() == 'all':
                                        col = col_list
                                    else:
                                        col = get_columns(col, col_list)
                                    if col != 'Err':
                                        show_table(self, df)
                                        df[col].plot()
                                        mngr = plt.get_current_fig_manager()
                                        mngr.window.setGeometry(550,250,640, 545)
                                        mngr.set_window_title("Py Finance")
                                        plt.show()
                                        break
                                    else:
                                        error_dialog2 = QErrorMessage()
                                        error_dialog2.showMessage('You\'ve not entered a valid column name!')
                                        error_dialog2.exec_()
                                else:
                                    break
                            elif self.complexGraph.isChecked() and tag == None:
                                daysWind, ok2 = QInputDialog.getInt(self, 'input dialog', f'Insert the days window:', value=10, min=1, max=200)
                                if ok2:
                                    daysWind = str(daysWind) + 'D'
                                    df_ohlc = df['Adj Close'].resample(daysWind).ohlc()
                                    df_volume = df['Volume'].resample(daysWind).sum()
                                    show_table(self, df_ohlc)
                                    df_ohlc = df_ohlc.reset_index()
                                    df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)
                                    fig = plt.figure()
                                    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
                                    ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1,sharex=ax1)
                                    ax1.xaxis_date()
                                    candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
                                    ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
                                    mngr = plt.get_current_fig_manager()
                                    mngr.window.setGeometry(550,250,640, 545)
                                    mngr.set_window_title("Py Finance")
                                    plt.show()
                                    break
                                else:
                                    break
                    elif not self.showPlot and tag == None:
                        show_table(self, df)
                    return df
                else:
                    error_dialog = QErrorMessage()
                    error_dialog.showMessage('The file does not exist!')
                    error_dialog.exec_()
        else:
            break

import sys
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.window.rolling import Window
import pandas_datareader.data as web
import pandas_datareader._utils
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QAbstractTableModel, Qt

df = None
startYear, startMonth, startDay, endYear, endMonth, endDay, end = 0, 0, 0, 0, 0, 0, dt.datetime.now()
def validateForStockPrices(date, type_):
    global startYear, startMonth, startDay, endYear, endMonth, endDay, end
    # if type_ == 'end' and date == 'now':
    #     end = dt.datetime.now()
    if type_ == 'start' and date == 'now':
        return False
    elif date != 'now':
        try:
            if len(date) == 10:
                date = date.split('-')
                #dateYear = int(date[:4])
                #dateMonth = int(date[5:7])
                #dateDay = int(date[8:10])
                dateYear = int(date[0])
                dateMonth = int(date[1])
                dateDay = int(date[2])
                continue_ = True
                if type_ == 'start':
                    startYear, startMonth, startDay = dateYear, dateMonth, dateDay
                else:
                    endYear, endMonth, endDay = dateYear, dateMonth, dateDay + 1
                    end = dt.datetime(endYear, endMonth, endDay)
                if dateMonth > 12:
                    continue_ = False
                    raise ValueError
                if dateDay > 31:
                    continue_ = False
                    raise ValueError
            else:
                raise ValueError
        except (ValueError, IndexError) as Error:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('You\'ve not entered a valid value!')
            error_dialog.exec_()
            return False
        if continue_:
            return True
    else:
        return True

def getStockPrices(self, tickerSymbol, tag):
    global end, df
    style.use('ggplot')
    start = dt.datetime(startYear, startMonth, startDay)
    print(start)
    print(end)
    # df = web.DataReader(tickerSymbol, 'yahoo', start, end)
    while True:
        try:
            df = web.DataReader(tickerSymbol, 'yahoo', start, end)
        except pandas_datareader._utils.RemoteDataError:
            symbol_error_dialog = QErrorMessage()
            symbol_error_dialog.showMessage('You\'ve not entered a valid ticker symbol!')
            symbol_error_dialog.exec_()
            tickerSymbol, ok = QInputDialog.getText(self, 'input dialog', 'Insert the ticker simbol: ')
            if ok:
                print(tickerSymbol)
            else:
                return 'None'
        except KeyError:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('An error has occurred.')
            error_dialog.exec_()
        else:
            break
    print('\n--------HEAD--------\n')
    print(df.head(6))
    print('\n--------TAIL--------\n')
    print(df.tail(6))
    print('\n')
    if self.saveInFile:
        continue_1 = True
        while continue_1:
            csvFile, ok = QInputDialog.getText(self, 'input dialog', 'Insert the name of the file: ')
            fileExt = '.csv'
            continue_2 = True
            if ok:
                continue_2 = True
                if csvFile[-4:] != fileExt:
                    for i in csvFile:
                        if i == '.':
                            error_dialog = QErrorMessage()
                            error_dialog.showMessage('You\'ve not entered a valid extension!')
                            error_dialog.exec_()
                            continue_2 = False
                            break
                    else:
                        csvFile += fileExt
                if continue_2:
                    df.to_csv(csvFile)
                    break
            else:
                break
    if self.showPlot:
        while True:
            col_list = ['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']
            col_list_str = str(col_list)
            col_list_str = col_list_str[:33] + ' \n' + col_list_str[33:]
            if self.normalGraph.isChecked() and tag == None:
                col, ok = QInputDialog.getText(self, 'input dialog', f'Insert the name of the column/s to graph {col_list_str} (if more than one, separate with \'-\', for all: \'All\'): ')
                if ok:
                    if col.strip().lower() == 'all':
                        col = col_list
                    else:
                        col = get_columns(col, col_list)
                    if col != 'Err':
                        if tag == None:
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
            elif self.complexGraph.isChecked() and tag == None:
                daysWind, ok2 = QInputDialog.getInt(self, 'input dialog', f'Insert the days window:', value=10, min=1, max=200)
                if ok2:
                    daysWind = str(daysWind) + 'D'
                    df_ohlc = df['Adj Close'].resample(daysWind).ohlc()
                    df_volume = df['Volume'].resample(daysWind).sum()
                    df_ohlc = df_ohlc.reset_index()
                    df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)
                    plt.figure()
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
            else:
                break
    return df


def get_columns(col, col_list):
    in_col_list = col.split('-')
    in_col_list = [i.strip().capitalize() for i in in_col_list]
    for i in in_col_list:
        if i not in col_list:
            return 'Err'
    return in_col_list


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

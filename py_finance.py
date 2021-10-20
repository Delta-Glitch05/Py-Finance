import os
import sys
import subprocess
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDateTime, Qt, QTimer, QProcess, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QDesktopServices
from getStockPrices import validateForStockPrices, getStockPrices, get_columns, pandasModel
from readStockPricesFile import readStockPricesFile
from get_SP_500 import get_SP500
from machine_learning_with_stock_data import ml_stock_data
from tableWind import TableWind
from PyQt5.QtCore import QAbstractTableModel, Qt
import matplotlib.pyplot as plt
import pandas as pd
import time
import requests


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Py Finance")
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.originalPalette = QApplication.palette()
        self.styleComboBox = QComboBox()
        self.styleComboBox.addItems(QStyleFactory.keys())
        self.styleLabel = QLabel('&Style:')
        self.styleLabel.setBuddy(self.styleComboBox)
        self.index = self.styleComboBox.findText('Fusion', QtCore.Qt.MatchFixedString)
        self.styleComboBox.setCurrentIndex(self.index)
        self.useStylePaletteCheckBox = QCheckBox('&Use style\'s standard palette')
        self.useStylePaletteCheckBox.setChecked(True)
        self.disableWidgetsCheckBox = QCheckBox('&Disable widgets')
        self.createLeftGroupBox()
        self.createRightGroupBox()
        self.styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        self.disableWidgetsCheckBox.toggled.connect(self.leftGroupBox.setDisabled)
        self.disableWidgetsCheckBox.toggled.connect(self.rightGroupBox.setDisabled)
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(self.styleLabel)
        self.topLayout.addWidget(self.styleComboBox)
        self.topLayout.addStretch(1)
        self.topLayout.addWidget(self.useStylePaletteCheckBox)
        self.topLayout.addWidget(self.disableWidgetsCheckBox)
        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(self.topLayout, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.leftGroupBox, 1, 0)
        self.mainLayout.addWidget(self.rightGroupBox, 1, 1)
        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setRowStretch(1, 0)
        self.mainLayout.setRowStretch(1, 0)
        self.widget = QWidget()
        self.widget.setLayout(self.mainLayout)
        self.setCentralWidget(self.widget)
        self.changeStyle('Fusion')
        self.setGeometry(400, 200, 800, 600)
    
    def changeStyle(self, styleName):
        self.styleName = styleName
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if self.useStylePaletteCheckBox.isChecked():
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)
    
    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox('Applications')
        self.font_1 = QtGui.QFont()
        self.font_1.setFamily("Ubuntu")
        self.font_1.setPointSize(12)
        self.font_1.setBold(False)
        self.gen_font = QtGui.QFont()
        self.gen_font.setFamily("Arial Black")
        self.gen_font.setPointSize(12)
        self.gen_font.setBold(True)
        self.leftGroupBox.setFont(self.gen_font)
        self.getStockPricesButton = QPushButton('Get Stock Prices')
        self.getStockPricesButton.setDefault(True)
        self.getStockPricesButton.setFont(self.font_1)
        self.readStockPricesFileButton = QPushButton('Read Stock Prices File')
        self.readStockPricesFileButton.setDefault(True)
        self.readStockPricesFileButton.setFont(self.font_1)
        self.addMovingAverageButton = QPushButton('Add Moving Average')
        self.addMovingAverageButton.setDefault(True)
        self.addMovingAverageButton.setFont(self.font_1)
        self.get_SP500_Button = QPushButton('Get S&&P 500 pricing data and correlation table')
        self.get_SP500_Button.setDefault(True)
        self.get_SP500_Button.setFont(self.font_1)
        self.ml_SP500_Button = QPushButton('Machine learning with stock data')
        self.ml_SP500_Button.setDefault(True)
        self.ml_SP500_Button.setFont(self.font_1)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.getStockPricesButton)
        self.layout.addWidget(self.readStockPricesFileButton)
        self.layout.addWidget(self.addMovingAverageButton)
        self.layout.addWidget(self.get_SP500_Button)
        self.layout.addWidget(self.ml_SP500_Button)
        self.layout.addStretch(1)
        self.leftGroupBox.setLayout(self.layout)
        self.clicksOnButton = 0
        self.getStockPricesButton.clicked.connect(lambda: self.getStockPricesBtnFunc(None))
        self.readStockPricesFileButton.clicked.connect(lambda: readStockPricesFile(self, None))
        self.addMovingAverageButton.clicked.connect(self.addMovingAverage)
        self.get_SP500_Button.clicked.connect(lambda: get_SP500(True))
        self.ml_SP500_Button.clicked.connect(self.call_ml_stock_data)
    
    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Settings")
        self.rightGroupBox.setFont(self.gen_font)
        self.font_2 = QtGui.QFont()
        self.font_2.setFamily("Roboto")
        self.font_2.setPointSize(12)
        self.layout2 = QVBoxLayout()
        self.saveInFile = False
        self.saveInFileBox = QCheckBox(self)
        self.saveInFileBox.setText('Save in a CSV file')
        self.saveInFileBox.stateChanged.connect(self.saveInFileOption)
        self.showPlot = False
        self.showPlotBox = QCheckBox(self)
        self.showPlotBox.setText('Show plot')
        self.showPlotBox.stateChanged.connect(self.showPlotOption)
        self.saveInFileBox.setFont(self.font_2)
        self.showPlotBox.setFont(self.font_2)
        self.saveInFileBox.setStyleSheet("QCheckBox::indicator"
                               "{"
                               "width :20px;"
                               "height : 20px;"
                               "}")
        self.showPlotBox.setStyleSheet("QCheckBox::indicator"
                               "{"
                               "width :20px;"
                               "height : 20px;"
                               "}")
        self.normalGraph = QRadioButton("Display a normal graph")
        self.complexGraph = QRadioButton("Display a more complex graph")
        self.normalGraph.setChecked(True)
        self.normalGraph.setFont(self.font_1)
        self.complexGraph.setFont(self.font_1)
        self.layout2.addWidget(self.saveInFileBox)
        self.layout2.addWidget(self.showPlotBox)
        self.layout2.addWidget(self.normalGraph)
        self.layout2.addWidget(self.complexGraph)
        self.layout2.addStretch(1)
        self.rightGroupBox.setLayout(self.layout2)
    
    def saveInFileOption(self, checked):
        if checked:
            self.saveInFile = True
        else:
            self.saveInFile = False
    
    def showPlotOption(self, checked):
        if checked:
            self.showPlot = True
        else:
            self.showPlot = False

    def getStockPricesBtnFunc(self, tag):
        tickerSymbol, ok = QInputDialog.getText(self, 'input dialog', 'Insert the ticker simbol: ')
        tickerSymbol = tickerSymbol.upper()
        if ok:
            continue_ = True
            while continue_:
                start, ok2 = QInputDialog.getText(self, 'input dialog', 'Insert the starting date [yyyy-mm-dd]: ')
                if ok2:
                    check = validateForStockPrices(start, 'start')
                    if check == True:
                        break
                else:
                    break
            if ok2:
                continue_ = True
                while continue_:
                    end, ok3 = QInputDialog.getText(self, 'input dialog', 'Insert the ending date [yyyy-mm-dd OR \'now\']: ')
                    if ok3:
                        check = validateForStockPrices(end, 'end')
                        if check == True:
                            try:
                                df = getStockPrices(self, tickerSymbol, tag)
                                if str(df) == 'None':
                                    return 'None'
                                if tag == None:
                                    self.table = QTableView()
                                    self.model = pandasModel(df)
                                    self.table.setModel(self.model)
                                    self.w2 = TableWind(self.table)
                                    self.w2.show()
                                elif tag == 'ma':
                                    return df
                                break
                            except requests.exceptions.ConnectionError:
                                conn_error_dialog = QErrorMessage()
                                conn_error_dialog.showMessage('A connection error has occurred. Make sure you are connected to the internet.')
                                conn_error_dialog.exec_()
                                return 'None'
                    else:
                        break

    def addMovingAverage(self):
        continue_1 = True
        while continue_1:
            movAvgChoice, ok = QInputDialog.getInt(self, 'input dialog', 'Do you want to get stocks from the internet (1) or from a file (2)?:', min=1, max=2)
            if ok:
                if movAvgChoice == 1:
                    df = self.getStockPricesBtnFunc('ma')
                else:
                    df = readStockPricesFile(self, 'ma')
                if str(df) != 'None':
                    while True:
                        movAvgDays, ok2 = QInputDialog.getInt(self, 'input dialog', 'How many days do you want the moving average to be?', value=100, min=1, max=200)
                        if ok2:
                            self.table = QTableView()
                            self.model = pandasModel(df)
                            self.table.setModel(self.model)
                            self.w2 = TableWind(self.table)
                            self.w2.show()
                            movAvg = str(movAvgDays) + 'ma'
                            df[movAvg] = df['Adj Close'].rolling(window=movAvgDays, min_periods=0).mean()
                            ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
                            ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1,sharex=ax1)
                            ax1.plot(df.index, df['Adj Close'])
                            ax1.plot(df.index, df['100ma'])
                            ax2.bar(df.index, df['Volume'])
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(550,250,640, 545)
                            mngr.set_window_title("Py Finance")
                            plt.show()
                            continue_1 = False
                            break
                        else:
                            continue_1 = False
                            break
                    else:
                        break
            else:
                break

    def call_ml_stock_data(self):
        ret = time_info_dialog = QMessageBox.warning(self, "Warning", "This operation is going to take some time. Do you want to continue?", 
                                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            ml_stock_data()


def main():
    app = QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

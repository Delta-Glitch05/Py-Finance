from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDateTime, Qt, QTimer, QProcess, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QDesktopServices

class TableWind(QMainWindow):
    def __init__(self, table, parent=None):
        self.language = 'English'
        self.table = table
        # print(self.language)
        super(TableWind, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Py Finance")
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.originalPalette = QApplication.palette()
        self.styleComboBox = QComboBox()
        self.styleComboBox.addItems(QStyleFactory.keys())
        self.styleLabel = QLabel("&Style:")
        self.styleLabel.setBuddy(self.styleComboBox)
        self.setCentralWidget(self.table)
        self.setGeometry(400, 200, 800, 600)

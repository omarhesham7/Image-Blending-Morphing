# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MorphingGUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 706)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsViewStartingImage = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsViewStartingImage.setGeometry(QtCore.QRect(10, 40, 341, 251))
        self.graphicsViewStartingImage.setObjectName("graphicsViewStartingImage")
        self.pushButtonStartingImage = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStartingImage.setGeometry(QtCore.QRect(10, 10, 161, 27))
        self.pushButtonStartingImage.setObjectName("pushButtonStartingImage")
        self.pushButtonEndingImage = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonEndingImage.setGeometry(QtCore.QRect(450, 10, 161, 27))
        self.pushButtonEndingImage.setObjectName("pushButtonEndingImage")
        self.labelStartingImage = QtWidgets.QLabel(self.centralwidget)
        self.labelStartingImage.setGeometry(QtCore.QRect(110, 300, 111, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelStartingImage.setFont(font)
        self.labelStartingImage.setObjectName("labelStartingImage")
        self.labelEndingImage = QtWidgets.QLabel(self.centralwidget)
        self.labelEndingImage.setGeometry(QtCore.QRect(570, 300, 111, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelEndingImage.setFont(font)
        self.labelEndingImage.setObjectName("labelEndingImage")
        self.checkBoxShowTriangles = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBoxShowTriangles.setGeometry(QtCore.QRect(340, 300, 121, 22))
        self.checkBoxShowTriangles.setObjectName("checkBoxShowTriangles")
        self.graphicsViewEndingImage = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsViewEndingImage.setGeometry(QtCore.QRect(450, 40, 341, 251))
        self.graphicsViewEndingImage.setObjectName("graphicsViewEndingImage")
        self.graphicsViewBlendedImage = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsViewBlendedImage.setGeometry(QtCore.QRect(240, 360, 341, 251))
        self.graphicsViewBlendedImage.setObjectName("graphicsViewBlendedImage")
        self.labelBlendingResult = QtWidgets.QLabel(self.centralwidget)
        self.labelBlendingResult.setGeometry(QtCore.QRect(350, 620, 121, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelBlendingResult.setFont(font)
        self.labelBlendingResult.setObjectName("labelBlendingResult")
        self.pushButtonBlend = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonBlend.setGeometry(QtCore.QRect(360, 640, 91, 27))
        self.pushButtonBlend.setObjectName("pushButtonBlend")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(60, 330, 661, 19))
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(5)
        self.horizontalSlider.setSliderPosition(0)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(10)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.labelAlpha = QtWidgets.QLabel(self.centralwidget)
        self.labelAlpha.setGeometry(QtCore.QRect(10, 320, 41, 17))
        self.labelAlpha.setObjectName("labelAlpha")
        self.label00 = QtWidgets.QLabel(self.centralwidget)
        self.label00.setGeometry(QtCore.QRect(60, 350, 21, 17))
        self.label00.setObjectName("label00")
        self.label10 = QtWidgets.QLabel(self.centralwidget)
        self.label10.setGeometry(QtCore.QRect(710, 350, 21, 17))
        self.label10.setObjectName("label10")
        self.textEditCurrentAlphaValue = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditCurrentAlphaValue.setGeometry(QtCore.QRect(740, 330, 51, 21))
        self.textEditCurrentAlphaValue.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditCurrentAlphaValue.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditCurrentAlphaValue.setObjectName("textEditCurrentAlphaValue")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButtonStartingImage.setText(_translate("MainWindow", "Load Starting Image ..."))
        self.pushButtonEndingImage.setText(_translate("MainWindow", "Load Ending Image ..."))
        self.labelStartingImage.setText(_translate("MainWindow", "Starting Image"))
        self.labelEndingImage.setText(_translate("MainWindow", "Ending Image"))
        self.checkBoxShowTriangles.setText(_translate("MainWindow", "Show Triangles"))
        self.labelBlendingResult.setText(_translate("MainWindow", "Blending Result"))
        self.pushButtonBlend.setText(_translate("MainWindow", "Blend"))
        self.labelAlpha.setText(_translate("MainWindow", "Alpha"))
        self.label00.setText(_translate("MainWindow", "0.0"))
        self.label10.setText(_translate("MainWindow", "1.0"))


# Form implementation generated from reading ui file 'main_test_window_ui.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtWidgets

from files.testing_system_files.test_image_label import TestImageLabel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1135, 748)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image_label = TestImageLabel(parent=self.centralwidget)
        self.image_label.setGeometry(QtCore.QRect(10, 10, 1100, 650))
        self.image_label.setObjectName("image_label")
        self.finish_test_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.finish_test_button.setGeometry(QtCore.QRect(0, 680, 1111, 23))
        self.finish_test_button.setObjectName("finish_testButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1135, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Тестирование"))
        self.image_label.setText(_translate("MainWindow", "TextLabel"))
        self.finish_test_button.setText(_translate("MainWindow", "Завершить тест"))

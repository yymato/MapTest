# Form implementation generated from reading ui file 'creator_ui1.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtWidgets

from files.creator_files.image_label import ImageLabel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1202, 824)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image_label = ImageLabel(parent=self.centralwidget)
        self.image_label.setGeometry(QtCore.QRect(30, 110, 1100, 650))
        self.image_label.setObjectName("image_label")
        self.updated_question_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.updated_question_button.setGeometry(QtCore.QRect(20, 10, 121, 31))
        self.updated_question_button.setObjectName("updated_question_button")
        self.input_question_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.input_question_button.setGeometry(QtCore.QRect(160, 10, 121, 31))
        self.input_question_button.setObjectName("input_question_button")
        self.choose_question_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.choose_question_button.setGeometry(QtCore.QRect(300, 10, 121, 31))
        self.choose_question_button.setObjectName("choose_question_button")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1202, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Создание теста"))
        self.image_label.setText(_translate("MainWindow", "Нажмите, чтобы выбрать картинку"))
        self.updated_question_button.setText(_translate("MainWindow", "Развернутый ответ"))
        self.input_question_button.setText(_translate("MainWindow", "Ввод ответа"))
        self.choose_question_button.setText(_translate("MainWindow", "Выбор варинта(ов)"))
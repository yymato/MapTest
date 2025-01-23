# Form implementation generated from reading ui file 'setting_test.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
import io
import sqlite3

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from files.CONSTANT import HISTORY_PATH_QUESTION, HISTORY_PATH_ANSWERS
from files.main_files.interpreter_result_files.interpreter_result import PathError


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(768, 236)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 40, 691, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.question_path_combo_box = QtWidgets.QComboBox(parent=self.verticalLayoutWidget)
        self.question_path_combo_box.setObjectName("question_path_combo_box")
        self.horizontalLayout.addWidget(self.question_path_combo_box)
        self.choose_question_path_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.choose_question_path_button.setMaximumSize(QtCore.QSize(50, 16777215))
        self.choose_question_path_button.setObjectName("choose_question_path_button")
        self.horizontalLayout.addWidget(self.choose_question_path_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.answer_path_combo_box = QtWidgets.QComboBox(parent=self.verticalLayoutWidget)
        self.answer_path_combo_box.setObjectName("answer_path_combo_box")
        self.horizontalLayout_2.addWidget(self.answer_path_combo_box)
        self.choose_answer_path_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.choose_answer_path_button.setMaximumSize(QtCore.QSize(50, 16777215))
        self.choose_answer_path_button.setObjectName("choose_answer_path_button")
        self.horizontalLayout_2.addWidget(self.choose_answer_path_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.starting_test_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.starting_test_button.setObjectName("starting_test_button")
        self.verticalLayout.addWidget(self.starting_test_button)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 768, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Файл с тестом"))
        self.choose_question_path_button.setText(_translate("MainWindow", "Обзор"))
        self.label_2.setText(_translate("MainWindow", "Файл с ответами"))
        self.choose_answer_path_button.setText(_translate("MainWindow", "Обзор"))
        self.starting_test_button.setText(_translate("MainWindow", "Начать тестирование"))


class SettingsTestWindow(Ui_MainWindow, QMainWindow):
    successful_start_test = pyqtSignal()
    cancel_start_test = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.test_db_path = None

        self.answers_db_path = None

        self.terminate = False

        self.choose_question_path_button.clicked.connect(self.choose_question_path)
        self.choose_answer_path_button.clicked.connect(self.choose_answer_path)
        self.starting_test_button.clicked.connect(self.start_test)

        self.question_path_combo_box.currentIndexChanged.connect(self.on_question_path_changed)
        self.answer_path_combo_box.currentIndexChanged.connect(self.on_answer_path_changed)

        self.update_question_history('init')
        self.update_answers_history('init')

    def update_question_history(self, data):
        if data != 'init':
            # Обновляем историю для проекта
            if data:
                if self.test_db_path != data:  # Предотвращаем повторную запись одинакового пути
                    self.test_db_path = data
                    with open(HISTORY_PATH_QUESTION, 'a+') as history_path:
                        history_path.seek(0)  # Перемещаем указатель в начало файла
                        paths = history_path.readlines()
                        if self.test_db_path + '\n' not in paths:  # Если путь еще не в истории
                            history_path.write(self.test_db_path + '\n')

            # Загружаем и обновляем QComboBox для проектов
        try:
            with open(HISTORY_PATH_QUESTION, 'r') as history_path:
                paths = [line.strip() for line in history_path.readlines()]

            # Удаляем старые элементы и добавляем уникальные последние 10 путей
            self.question_path_combo_box.clear()
            for path in paths[-10:][::-1]:
                if path.strip():
                    self.question_path_combo_box.addItem(path.strip())

            if data == 'init' or self.test_db_path is None:
                self.question_path_combo_box.setCurrentIndex(-1)
        except io.UnsupportedOperation:
            pass

    def update_answers_history(self, data):
        if data != 'init':
            if data:
                if self.answers_db_path != data:  # Предотвращаем повторную запись одинакового пути
                    self.answers_db_path = data
                    with open(HISTORY_PATH_ANSWERS, 'a+') as history_path:
                        history_path.seek(0)  # Перемещаем указатель в начало файла
                        paths = history_path.readlines()
                        if self.answers_db_path + '\n' not in paths:  # Если путь еще не в истории
                            history_path.write(self.answers_db_path + '\n')

        # Загружаем и обновляем QComboBox для изображений
        try:
            with open(HISTORY_PATH_ANSWERS, 'r') as history_path:
                paths = [line.strip() for line in history_path.readlines()]

            # Удаляем старые элементы и добавляем уникальные последние 10 путей
            self.answer_path_combo_box.clear()
            for path in paths[-10:][::-1]:
                if path.strip():
                    self.answer_path_combo_box.addItem(path.strip())

            if self.answers_db_path is None or data == 'init':
                self.answer_path_combo_box.setCurrentIndex(-1)
        except io.UnsupportedOperation:
            pass


    def choose_question_path(self):
        test_db_path = QFileDialog.getOpenFileName(self, "Открыть файл с тестом", "", "SQL Files (*.sqlite)")[0]
        try:
            conn = sqlite3.connect(test_db_path)
            tables = conn.cursor().execute('SELECT name FROM sqlite_master WHERE type="table"')
            quest_reference = {'type', 'sqlite_sequence', 'question_data', 'main_ids', 'choice_question_data',
                               'main_image',
                               'question_values'}
            if set(map(lambda table: str(*table), tables)) != quest_reference:
                raise PathError
            else:
                self.update_question_history(test_db_path)
        except PathError:
            QMessageBox.warning(self, 'Ошибка', 'Не корректный файл. Возможно, вы выбрали ответы, а не вопросы.')

    def choose_answer_path(self):
        answers_db_path = QFileDialog.getSaveFileName(self, "Сохранить ответы", "", "SQL Files (*.sqlite)")[0]
        if answers_db_path:
            self.update_answers_history(answers_db_path)

    def on_question_path_changed(self):
        self.test_db_path = self.question_path_combo_box.currentText()

    def on_answer_path_changed(self):
        self.answers_db_path = self.answer_path_combo_box.currentText()

    def start_test(self):
        if self.test_db_path is not None and self.answers_db_path is not None:
            self.successful_start_test.emit()
            self.terminated()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')

    def get_test_db_path(self):
        return self.test_db_path

    def get_answers_db_path(self):
        return self.answers_db_path

    def terminated(self):
        self.terminate = True
        self.close()

    def closeEvent(self, event):
        if self.terminate:
            event.accept()
            self.terminate = False
        else:
            self.cancel_start_test.emit()
            event.accept()

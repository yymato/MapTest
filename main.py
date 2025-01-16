import sys
import sqlite3
import xlsxwriter
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from files.testing_system_files.main_testing_window import MainTestingWindow
from files.main_files.ui_py_files.main_ui import Ui_MainWindow
from files.creator_files.creator import CreatorWindow
from files.main_files.interpreter_result_files.interpreter_result import InterpreterResultWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Главное окно приложения для работы с тестами.
    """

    def __init__(self):
        """
        Инициализация главного окна приложения.
        """
        super().__init__()
        self.setupUi(self)

        self.creator = None
        self.test = None
        self.interpreter = None
        self.create_testButton.clicked.connect(self.create_test)
        self.starting_testButton.clicked.connect(self.starting_test)
        self.interpreter_result_button.clicked.connect(self.interpreter_result)

        self.is_open = False

    def create_test(self):
        """
        Открывает окно для создания нового теста.
        """
        if not self.is_open:
            self.creator = CreatorWindow(self)
            self.creator.close_window.connect(self.closed_window)

            self.creator.show()
            self.is_open = True

    def starting_test(self):
        """
        Открывает окно для прохождения теста.
        """
        if not self.is_open:
            self.test = MainTestingWindow(self)
            self.test.close_window.connect(self.closed_window)
            self.test.connect_to_bds()
            self.test.show()
            self.is_open = True

    def interpreter_result(self):
        if not self.is_open:
            self.interpreter = InterpreterResultWindow()
            self.interpreter.close_window.connect(self.closed_window)
            self.interpreter.show()
            self.is_open = True

    def closed_window(self):
        """
        Закрывает окна редактора и теста.
        """
        self.is_open = False


def except_hook(cls, exception, traceback):
    """
    Обработчик исключений для корректной работы PyQt.
    """
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    """
    Основная точка входа приложения.
    """
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())

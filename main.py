import os
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from files.CONSTANT import HISTORY_PATH_PROJECT, HISTORY_PATH_ANSWERS, HISTORY_PATH_IMAGES
from files.creator_files.creator import CreatorWindow
from files.main_files.interpreter_result_files.interpreter_result import InterpreterResultWindow
from files.main_files.ui_py_files.main_ui_V1 import Ui_MainWindow
from files.testing_system_files.main_testing_window import MainTestingWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Главное окно приложения
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
        self.create_test_button.clicked.connect(self.create_test)
        self.start_button.clicked.connect(self.start_test)
        self.get_result_button.clicked.connect(self.get_result)
        self.change_test_button.clicked.connect(self.change_test)

        # Проверяем что папка существует
        if not os.path.exists(os.path.dirname(HISTORY_PATH_PROJECT)):
            os.makedirs(os.path.dirname(HISTORY_PATH_PROJECT))

        # Создаем Файлы для хранения истории вводимых путей и для истории проектов.
        # TODO Очистку файлов с историей до 10 строк
        for PATH in [HISTORY_PATH_PROJECT, HISTORY_PATH_ANSWERS, HISTORY_PATH_IMAGES]:
            if not os.path.exists(PATH):
                op = open(PATH, 'x')
                op.close()

        self.is_open = False

    def create_test(self):
        """
        Открывает окно для создания нового теста.
        """
        if not self.is_open:
            self.creator = CreatorWindow(self, new_project=True)
            self.creator.close_window.connect(self.closed_window)
            self.is_open = True

    def change_test(self, path=None):
        pass


    def start_test(self):
        """
        Открывает окно для прохождения теста.
        """
        if not self.is_open:
            self.test = MainTestingWindow(self)
            self.test.close_window.connect(self.closed_window)
            self.is_open = True

    def get_result(self):
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

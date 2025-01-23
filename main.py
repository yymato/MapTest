import io
import os
import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidgetItem

from files.CONSTANT import HISTORY_PATH_QUESTION, HISTORY_PATH_ANSWERS, HISTORY_PATH_IMAGES, HISTORY_PATH_PROJECT
from files.creator_files.creator import CreatorWindow
from files.main_files.interpreter_result_files.interpreter_result import InterpreterResultWindow
from files.main_files.other import ListWidgetButton
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

        self.path_buttons = []  # Хранит пути кнопок которые были добавлены

        self.create_test_button.clicked.connect(self.create_test)
        self.start_button.clicked.connect(self.start_test)
        self.get_result_button.clicked.connect(self.get_result)
        self.change_test_button.clicked.connect(self.change_test)

        # Проверяем что папка существует
        if not os.path.exists(os.path.dirname(HISTORY_PATH_QUESTION)):
            os.makedirs(os.path.dirname(HISTORY_PATH_QUESTION))

        # Создаем Файлы для хранения истории вводимых путей и для истории проектов.
        # TODO Очистку файлов с историей до 10 строк
        for PATH in [HISTORY_PATH_QUESTION, HISTORY_PATH_ANSWERS, HISTORY_PATH_IMAGES, HISTORY_PATH_PROJECT]:
            if not os.path.exists(PATH):
                op = open(PATH, 'x')
                op.close()

        self.is_open = False

        self.load_latest_project()

    def load_latest_project(self):
        try:
            with open(HISTORY_PATH_PROJECT, 'r') as history_path:
                paths = [line.strip() for line in history_path.readlines()]

            # Удаляем старые элементы и добавляем уникальные последние 10 путей
            self.latests_test_list_widget.clear()
            for path in paths[-10:][::-1]:
                if path:
                    for butt_index in range(self.latests_test_list_widget.count()):
                        if path == self.latests_test_list_widget.itemWidget(
                                self.latests_test_list_widget.item(butt_index)):
                            break
                    else:
                        button_text = os.path.basename(path).split('.')[0]  # Получаем имя файла без расширения
                        button = ListWidgetButton(path, self, text=button_text)
                        button.clicked.connect(self.change_test)

                        # Оборачиваем кнопку в QListWidgetItem и добавляем в список
                        list_item = QListWidgetItem()
                        self.latests_test_list_widget.addItem(list_item)
                        self.latests_test_list_widget.setItemWidget(list_item, button)
        except io.UnsupportedOperation:
            pass


    def create_test(self):
        """
        Открывает окно для создания нового теста.
        """
        if not self.is_open:
            self.creator = CreatorWindow(self)
            self.creator.close_window.connect(self.closed_window)
            self.is_open = True

    def change_test(self):
        path = None

        if self.sender().text() == 'Редактировать тест':
            dialog = QFileDialog.getOpenFileName(self, "Открыть файл с тестом", "", "Test files (*.sqlite)")[0]
            if dialog:
                path = dialog
        else:
            path = self.sender().get_data()

        if not path is None:
            conn = sqlite3.connect(path)
            tables = conn.cursor().execute('SELECT name FROM sqlite_master WHERE type="table"')
            quest_reference = {'type', 'sqlite_sequence', 'question_data', 'main_ids', 'choice_question_data',
                               'main_image',
                               'question_values'}
            if set(map(lambda table: str(*table), tables)) != quest_reference:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось открыть тест. Возможно, файл изменен или удален')
            else:
                self.creator = CreatorWindow(self, path)

            with open(HISTORY_PATH_PROJECT, 'a+') as history_path:
                history_path.seek(0)  # Перемещаем указатель в начало файла
                paths = history_path.readlines()
                if path + '\n' not in paths:  # Если путь еще не в истории
                    history_path.write(path + '\n')
                else:
                    # Удаляем путь из списка и добавляем его в конец
                    paths.remove(path + '\n')
                    paths.append(path + '\n')
                    # Перемещаем указатель в начало и перезаписываем файл
                    history_path.seek(0)
                    history_path.truncate()
                    history_path.writelines(paths)

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

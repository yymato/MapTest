import shutil
import sqlite3

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from files.main_files.compiled_path_fuction import resource_path
from files.main_files.database.database_images import load_pixmap_from_db
from files.testing_system_files.test_question import TestIconQuestion
from files.testing_system_files.testing_ui_files.main_test_window_ui import Ui_MainWindow
from files.testing_system_files.testing_ui_py_files.input_fio import InputFIO
from files.testing_system_files.testing_ui_py_files.setting_test import SettingsTestWindow


class MainTestingWindow(Ui_MainWindow, QMainWindow):
    # Сигналы для управления событиями окна
    close_window = pyqtSignal()  # Сигнал для закрытия окна
    start_test = pyqtSignal()  # Сигнал для начала теста
    update_window_question = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Привязка кнопки завершения теста к обработчику
        self.finish_test_button.clicked.connect(self.end_test)

        self.settings_test = SettingsTestWindow()
        self.settings_test.cancel_start_test.connect(self.terminated)
        self.settings_test.successful_start_test.connect(self.get_path)
        self.settings_test.show()

        # Инициализация атрибутов для хранения путей, идентификаторов и соединений с базой данных
        self.path_to_test = None
        self.path_to_result = None
        self.student_id = 0  # ID текущего участника теста
        self.icon_path = resource_path("files/images/icon.png")  # Путь к иконке вопроса
        self.is_open_quest = False
        self.test_con = None  # Соединение с базой данных теста
        self.result_con = None  # Соединение с базой данных результатов

        self.terminate = False

        # Создание и скрытие окна ввода ФИО
        self.get_fio_window = InputFIO(self, self)
        self.get_fio_window.close()

        # Привязка сигнала начала теста к обработчику установки ФИО студента
        self.start_test.connect(self.set_student_fio)

        self.update_window_question.connect(self.quest_signal)

    def get_path(self):
        self.path_to_test = self.settings_test.get_test_db_path()
        self.path_to_result = self.settings_test.get_answers_db_path()

        self.connect_to_bds()

    def connect_to_bds(self):
        # Копирование шаблона базы данных для результатов
        shutil.copyfile(resource_path('files/main_files/database/result_test.sqlite'),
                        self.path_to_result, follow_symlinks=True)

        # Установка соединений с базами данных
        self.test_con = sqlite3.connect(self.path_to_test)
        self.result_con = sqlite3.connect(self.path_to_result)

        # Запуск окна ввода ФИО студента
        self.show()
        self.get_student_fio()

    def get_student_fio(self):
        # Очистка поля ввода ФИО и отображение окна
        self.get_fio_window.student_fio.setText('')
        self.get_fio_window.show()

    def set_student_fio(self):
        # Сохранение ФИО студента в базу данных результатов
        self.result_con.cursor().execute('INSERT INTO students (student_fio) VALUES (?)',
                                         (self.get_fio_window.student_fio.text(),))
        # Получение ID добавленного студента
        self.student_id = int(*self.result_con.cursor().execute(
            'SELECT id FROM students WHERE student_fio = ?',
            (self.get_fio_window.student_fio.text(),)
        ).fetchone())
        self.result_con.commit()  # Фиксация изменений

        # Закрытие окна ввода ФИО
        self.get_fio_window.close()
        self.load_test()  # Загрузка теста

    def load_test(self):
        # Загрузка изображения из базы данных
        self.image_label.my_pixmap(load_pixmap_from_db(*self.test_con.cursor().execute(
            'SELECT image FROM main_image').fetchone()))

        # Вычисление смещения изображения в метке (для корректного размещения элементов)
        label_rect = self.image_label.rect()
        pixmap_rect = self.image_label.pixmap().rect()
        offset_x = (label_rect.width() - pixmap_rect.width()) // 2
        offset_y = (label_rect.height() - pixmap_rect.height()) // 2

        # Загрузка данных вопросов из базы
        request = self.test_con.cursor().execute('SELECT * from main_ids')
        for i in request:
            if i[2] == 2:  # Вопрос с вводом ответа
                for data in self.test_con.cursor().execute(
                        'SELECT x, y, quest, image FROM question_data WHERE id = ?', (i[1],)):
                    x, y, text_question, bytes_image = data
                    pixmap_image = load_pixmap_from_db(bytes_image)

                    # Создание и настройка иконки вопроса
                    icon = TestIconQuestion(self.image_label, self, self.icon_path, i[0],
                                            self.result_con, self.result_con.cursor())
                    icon.set_question_maket("Запись ответа")
                    icon.question.question_plain_text.setPlainText(text_question)
                    icon.question.image_label.my_pixmap(pixmap_image)

                    # Установка положения с учетом смещения
                    icon.move(x + offset_x, y + offset_y)
                    icon.show()

            elif i[2] == 1:  # Вопрос с развернутым ответом
                for data in self.test_con.cursor().execute(
                        'SELECT x, y, quest, answer, image FROM question_data WHERE id = ?', (i[1],)):
                    x, y, text_question, answer, bytes_image = data
                    pixmap_image = load_pixmap_from_db(bytes_image)
                    # Создание и настройка иконки вопроса
                    icon = TestIconQuestion(self.image_label, self, self.icon_path, i[0],
                                            self.result_con, self.result_con.cursor())
                    icon.set_question_maket('Развернутый ответ (проверяется вручную)')
                    icon.question.question_plain_text.setPlainText(text_question)
                    icon.question.image_label.my_pixmap(pixmap_image)
                    icon.move(x + offset_x, y + offset_y)
                    icon.show()
            else:  # Вопрос с выбором варианта ответа
                for data in self.test_con.cursor().execute(
                        'SELECT x, y, quest, correct_answers, incorrect_answers, image'
                        ' FROM choice_question_data WHERE id = ?', (i[1],)):
                    x, y, text_question, correct_answers, incorrect_answers, bytes_image = data
                    correct_answers = correct_answers.split('↑♛')
                    incorrect_answers = incorrect_answers.split('↑♛')
                    pixmap_image = load_pixmap_from_db(bytes_image)
                    # Создание и настройка иконки вопроса
                    icon = TestIconQuestion(self.image_label, self, self.icon_path, i[0],
                                            self.result_con, self.result_con.cursor())
                    icon.set_question_maket('Выбор варианта(ов) ответа(ов)')
                    icon.question.question_plain_text.setPlainText(text_question)
                    icon.question.image_label.my_pixmap(pixmap_image)
                    icon.question.load_variants(correct_answers, incorrect_answers)
                    icon.move(x + offset_x, y + offset_y)
                    icon.show()

    def end_test(self):
        # Подтверждение завершения тестирования
        reply = QMessageBox.question(
            self,
            "Подтверждение завершения",
            "Вы действительно хотите завершить тестирование текущего участника? Убедитесь, что все ответы сохранены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Очистка интерфейса для следующего участника
            self.image_label.clear()
            self.student_id = 0
            self.result_con.commit()
            self.get_student_fio()

    def terminated(self):
        self.terminate = True
        self.close()

    def closeEvent(self, event):
        if self.terminate:
            self.terminate = False
            event.accept()


        # Предупреждение при закрытии окна
        reply = QMessageBox.question(
            self,
            "Подтверждение закрытия",
            "Вы действительно хотите выйти В ГЛАВНОЕ МЕНЮ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            if not self.result_con is None:
                self.result_con.commit()
            self.close_window.emit()
        else:
            event.ignore()

    def quest_signal(self):
        self.is_open_quest = not self.is_open_quest
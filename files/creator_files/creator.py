import shutil
import sqlite3

from PyQt6.QtCore import pyqtSignal
# Импортируем необходимые модули PyQt6
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from files.creator_files.create_project import ProjectCreateWindow
# Импортируем пользовательский интерфейс главного окна
from files.creator_files.creator_ui_py_files.creator_ui import Ui_MainWindow
from files.creator_files.question import IconQuestion
from files.main_files.compiled_path_fuction import resource_path
# Импортируем функции для работы с изображениями в базе данных
from files.main_files.database.database_images import load_pixmap_from_db, save_pixmap_to_db


class CreatorWindow(QMainWindow, Ui_MainWindow):
    # Сигнал для оповещения о закрытии окна
    close_window = pyqtSignal()

    def __init__(self, parent=None, new_project=False):
        super().__init__(parent)
        self.setupUi(self)  # Инициализация интерфейса
        self.show()
        self.icon_path = resource_path("files/images/icon.png")  # Путь к изображению иконки по умолчанию

        if new_project:
            self.create_project = ProjectCreateWindow()
            self.create_project.show()
            self.create_project.successful_save_project.connect(self.save_test)
            self.create_project.cancel_save_project.connect(self.terminated)

        # Подключение сигналов к обработчикам
        self.choose_question_button.clicked.connect(self.add_icon)
        self.input_question_button.clicked.connect(self.add_icon)
        self.updated_question_button.clicked.connect(self.add_icon)

        self.image_label.UpdateImage.connect(self.update_image)

        self.icon_positions = {}  # Словарь для хранения координат иконок
        self.con = None  # Объект соединения с базой данных
        self.cur = None  # Объект курсора базы данных
        self.terminate = False

    def load_test(self):
        """Загрузка теста из базы данных и отображение связанных элементов."""
        path_to_test = QFileDialog.getOpenFileName(self, "Открыть файл", "", "SQL Files (*.sqlite)")[0]
        if path_to_test:
            self.con = sqlite3.connect(path_to_test)  # Устанавливаем соединение с базой данных
            self.cur = self.con.cursor()

            # Устанавливаем изображение из базы данных на главную метку
            self.image_label.my_pixmap(
                load_pixmap_from_db(*self.cur.execute('SELECT image FROM main_image').fetchone())
            )

            # Рассчитываем смещение изображения относительно области метки
            label_rect = self.image_label.rect()  # Размер области метки
            pixmap_rect = self.image_label.pixmap().rect()  # Размер изображения
            offset_x = (label_rect.width() - pixmap_rect.width()) // 2
            offset_y = (label_rect.height() - pixmap_rect.height()) // 2

            # Обрабатываем данные из таблицы main_ids
            request = self.con.cursor().execute('SELECT * from main_ids')
            for i in request:
                # Вопрос с выбором варианта(ов) ответа(ов)
                if i[2] == 2:
                    for data in self.con.cursor().execute(
                            'SELECT x, y, quest, answer, image FROM question_data WHERE type = 2'):
                        value = int(self.con.execute('SELECT value FROM question_values WHERE question_main_id = ?',
                                                     (i[0],)).fetchall()[0][0])
                        x, y, text_question, answer, bytes_image = data
                        pixmap_image = load_pixmap_from_db(bytes_image)

                        # Создаем иконку и задаем ей параметры
                        icon = IconQuestion(self.image_label, self, self.icon_path, self.con, self.cur)
                        icon.setting_question_maket("Запись ответа")
                        icon.question.question_plain_text.setPlainText(text_question)
                        icon.question.answer_line_edit.setText(answer)
                        icon.question.image_label.setPixmap(pixmap_image)
                        icon.question.value_spinbox.setValue(value)
                        icon.question.main_id = i[0]

                        # Учитываем смещение изображения
                        corrected_x = x + offset_x
                        corrected_y = y + offset_y
                        icon.move(corrected_x, corrected_y)
                        icon.show()
                        self.icon_positions[icon] = (corrected_x, corrected_y)

                # Вопрос с развернутым ответом
                elif i[2] == 1:
                    for data in self.con.cursor().execute(
                            'SELECT x, y, quest, answer, image FROM question_data WHERE type = 1'):
                        x, y, text_question, answer, bytes_image = data
                        pixmap_image = load_pixmap_from_db(bytes_image)
                        # Создаем иконку и задаем ей параметры
                        icon = IconQuestion(self.image_label, self, self.icon_path, self.con, self.cur)
                        icon.setting_question_maket('Развернутый ответ (проверяется вручную)')
                        icon.question.main_id = i[0]
                        icon.question.question_plain_text.setPlainText(text_question)
                        icon.question.image_label.setPixmap(pixmap_image)

                        # Учитываем смещение изображения
                        corrected_x = x + offset_x
                        corrected_y = y + offset_y
                        icon.move(corrected_x, corrected_y)
                        icon.show()
                        self.icon_positions[icon] = (corrected_x, corrected_y)

                # Вопрос с выбором правильных и неправильных ответов
                else:
                    for data in self.con.cursor().execute(
                            'SELECT x, y, quest, correct_answers, incorrect_answers, image FROM choice_question_data'):
                        value = int(self.con.execute('SELECT value FROM question_values WHERE question_main_id = ?',
                                                     (i[0],)).fetchall()[0][0])

                        x, y, text_question, correct_answers, incorrect_answers, bytes_image = data
                        correct_answers = correct_answers.split('↑♛')
                        incorrect_answers = incorrect_answers.split('↑♛')
                        pixmap_image = load_pixmap_from_db(bytes_image)

                        # Создаем иконку и задаем ей параметры
                        icon = IconQuestion(self.image_label, self, self.icon_path, self.con, self.cur)
                        icon.setting_question_maket('Выбор варианта(ов) ответа(ов)')
                        icon.question.question_plain_text.setPlainText(text_question)
                        icon.question.image_label.setPixmap(pixmap_image)
                        icon.question.load_variants(correct_answers, incorrect_answers)
                        icon.question.value_spinbox.setValue(value)
                        icon.question.main_id = i[0]

                        # Учитываем смещение изображения
                        corrected_x = x + offset_x
                        corrected_y = y + offset_y
                        icon.move(corrected_x, corrected_y)
                        icon.show()
                        self.icon_positions[icon] = (corrected_x, corrected_y)

    def terminated(self):
        self.terminate = True
        self.close()

    def closeEvent(self, event):
        """Обработчик закрытия окна с предупреждением."""

        if self.terminate:
            event.accept()
            self.terminate = False

        reply = QMessageBox.question(
            self,
            "Подтверждение закрытия",
            "Вы действительно хотите закрыть окно?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.close_window.emit()  # Сигнал о закрытии окна
        else:
            event.ignore()

    def add_icon(self):
        """Добавление новой иконки на изображение."""
        if self.con is None:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Сначала добавьте картинку",
            )
            return
        icon = IconQuestion(self.image_label, self, self.icon_path, self.con, self.cur)
        if self.sender().objectName() == 'updated_question_button':
            icon.setting_question_maket("Развернутый ответ (проверяется вручную)")
        elif self.sender().objectName() == 'input_question_button':
            icon.setting_question_maket("Запись ответа")
        else:
            icon.setting_question_maket("Выбор варианта(ов) ответа(ов)")
        icon.move(10, 10)
        icon.show()
        self.icon_positions[icon] = (10, 10)  # Сохраняем координаты иконки

    def update_image(self):
        self.con.cursor().execute('DELETE FROM main_image')
        self.con.cursor().execute('INSERT INTO main_image(image) VALUES (?)',
                                  (save_pixmap_to_db(self.image_label.pixmap()),))
        self.con.commit()

    def save_test(self):
        """Сохранение изображения и создание таблицы, если она отсутствует."""

        shutil.copyfile(resource_path('files/main_files/database/save_test.sqlite'),
                        self.create_project.get_project_path(), follow_symlinks=True)
        self.con = sqlite3.connect(self.create_project.get_project_path())
        self.cur = self.con.cursor()
        self.image_label.set_my_image(self.create_project.get_image_path())
        self.con.cursor().execute('DELETE FROM main_image')
        self.con.cursor().execute('INSERT INTO main_image(image) VALUES (?)',
                                  (save_pixmap_to_db(self.image_label.pixmap()),))
        self.con.commit()

    def save_icon_position(self, icon):
        """Сохранение координат иконки относительно изображения."""
        icon_position = icon.pos()  # Локальные координаты иконки
        label_rect = self.image_label.rect()
        pixmap_rect = self.image_label.pixmap().rect()
        offset_x = (label_rect.width() - pixmap_rect.width()) // 2
        offset_y = (label_rect.height() - pixmap_rect.height()) // 2

        # Корректируем координаты с учетом смещения
        corrected_x = icon_position.x() - offset_x
        corrected_y = icon_position.y() - offset_y

        self.icon_positions[icon] = (corrected_x, corrected_y)

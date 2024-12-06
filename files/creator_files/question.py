# Импорт необходимых модулей и классов
from files.creator_files.creator_ui_py_files.question_files.question_maket_choice_answer import (
    QuestionUiMaketChoiceAnswer)
from files.creator_files.creator_ui_py_files.question_files.question_maket_input_answer import (
    QuestionUiMaketInputAnswer)
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap, QMouseEvent, QKeyEvent
from files.creator_files.creator_ui_py_files.question_files.question_maket_open_answer import QuestionUiMaketOpenAnswer


class IconQuestion(QWidget):
    """Класс для виджета с вопросом и поддержкой перетаскивания."""

    def __init__(self, parent=None, creator=None, icon_path="", con=None, cur=None):
        """
        Инициализация виджета.

        :param parent: Родительский виджет.
        :param creator: Главное окно.
        :param icon_path: Путь к изображению иконки.
        :param con: Подключение к базе данных.
        :param cur: Курсор базы данных.
        """
        super().__init__(parent)

        self.setFixedSize(40, 40)  # Устанавливаем фиксированный размер виджета
        self._offset = QPoint()  # Переменная для хранения смещения при перетаскивании
        self.creator = creator
        self.con = con
        self.cur = cur

        # Добавляем метку QLabel для отображения иконки
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(30, 30)  # Размер области для иконки
        self.icon_label.move(5, 5)  # Расположение метки внутри виджета

        # Если указан путь к изображению, загружаем его в QLabel
        if icon_path:
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio))

        # Создаем объект для отображения окна вопроса
        self.question = QuestionUiMaketInputAnswer(self, self)

        # Инициализация таймера для определения двойного клика
        self._double_click_timer = QTimer(self)
        self._double_click_timer.setSingleShot(True)  # Таймер срабатывает только один раз

    def mousePressEvent(self, event: QMouseEvent):
        """
        Обработчик нажатия мыши. Запоминает начальное положение и запускает таймер.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Запуск таймера для обработки двойного клика
            if not self._double_click_timer.isActive():
                self._double_click_timer.start(400)  # Интервал в 400 мс для определения двойного клика
            self._offset = event.pos()  # Запоминаем точку нажатия

    def enterEvent(self, event):
        """Устанавливает фокус на виджет при наведении мыши."""
        self.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатия клавиш. Удаляет виджет при нажатии Delete."""
        if event.key() == Qt.Key.Key_Delete:
            self.deletePressEvent()

    def deletePressEvent(self):
        """
        Удаление иконки при подтверждении действия пользователем.
        """
        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            'Вы действительно хотите удалить? Это действие необратимо',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.question.sql_delete()  # Удаление данных, связанных с вопросом, из базы
            self.deleteLater()  # Безопасное удаление виджета
            print("Иконка удалена!")  # Сообщение для отладки

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        Обработка двойного клика. Открывает окно редактирования вопроса.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            print("Двойной клик обнаружен!")  # Сообщение для отладки
            self.question.show()  # Показываем окно с вопросом
            self.question.raise_()  # Переносим окно на передний план
            self.question.activateWindow()  # Делаем окно активным
            self.question.move(100, 100)  # Задаем позицию окна (можно изменить)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Обработка перемещения мыши. Реализует перетаскивание виджета.
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            # Перемещение виджета с учетом начального смещения
            self.move(self.mapToParent(event.pos() - self._offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Фиксирует положение виджета после завершения перетаскивания.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.creator.save_icon_position(self)  # Вызываем метод для сохранения позиции

    def set_question_maket(self, maket_name):
        """
        Обновляет макет вопроса в зависимости от выбранного типа. Запускает окно вопроса

        :param maket_name: Название нового макета.
        """
        if maket_name == "Запись ответа":
            self.question.forced_close()
            self.question = QuestionUiMaketInputAnswer(self, self)
            self.question.show()
        elif maket_name == "Выбор варианта(ов) ответа(ов)":
            self.question.forced_close()
            self.question = QuestionUiMaketChoiceAnswer(self, self)
            self.question.show()
        elif maket_name == "Развернутый ответ (проверяется вручную)":
            self.question.forced_close()
            self.question = QuestionUiMaketOpenAnswer(self, self)
            self.question.show()

    def setting_question_maket(self, maket_name):
        """
        Изменяет макет вопроса без отображения окна.

        :param maket_name: Название нового макета.
        """
        if maket_name == "Запись ответа":
            self.question.forced_close()
            self.question = QuestionUiMaketInputAnswer(self, self)
        elif maket_name == "Выбор варианта(ов) ответа(ов)":
            self.question.forced_close()
            self.question = QuestionUiMaketChoiceAnswer(self, self)
        elif maket_name == "Развернутый ответ (проверяется вручную)":
            self.question.forced_close()
            self.question = QuestionUiMaketOpenAnswer(self, self)

from files.testing_system_files.testing_ui_py_files.question_files.question_choice_answer import (
    QuestionUiChoiceAnswer)
from files.testing_system_files.testing_ui_py_files.question_files.question_input_answer import QuestionUiInputAnswer
from files.testing_system_files.testing_ui_py_files.question_files.question_open_answer import QuestionUiOpenAnswer
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap, QMouseEvent


class TestIconQuestion(QWidget):
    """Класс для виджета с вопросом и поддержкой перетаскивания."""

    def __init__(self, parent=None, creator=None, icon_path="", main_id=0, con=None, cur=None):
        """
        Инициализация виджета.

        :param parent: Родительский виджет.
        :param creator: Главное окно.
        :param icon_path: Путь к изображению иконки.
        :param main_id: Общий id вопроса в базе данных
        :param con: Подключение к базе данных.
        :param cur: Курсор базы данных.
        """
        super().__init__(parent)

        self.setFixedSize(40, 40)  # Размер виджета для удобства перетаскивания
        self._offset = QPoint()  # Переменная для отслеживания смещения при перетаскивании
        self.creator = creator

        self.con = con
        self.cur = cur
        self.main_id = main_id

        # Добавляем QLabel для отображения иконки
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(30, 30)  # Размер для отображения иконки
        self.icon_label.move(5, 5)  # Позиционируем иконку внутри виджета

        self.question = QuestionUiOpenAnswer(self, self)

        # Загружаем изображение иконки, если указан путь
        if icon_path:
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio))

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Обработка двойного клика по иконке."""
        if event.button() == Qt.MouseButton.LeftButton:
            print("Двойной клик обнаружен!")  # Отладочный вывод
            # Показать окно с вопросом при двойном клике
            self.question.show()
            self.question.raise_()  # Форсируем окно на передний план
            self.question.activateWindow()  # Активируем окно, чтобы оно получило фокус

            # Проверим, видно ли оно на экране
            print(f"Окно QuestionWindow видимо: {self.question.isVisible()}")
            print(f"Размер окна: {self.question.size()}")
            self.question.move(100, 100)

    def set_question_maket(self, maket_name):
        """Обновляет макет вопроса для этой иконки в зависимости от выбора."""
        # В зависимости от имени выбранного макета обновляем экземпляр `self.question`
        if maket_name == "Запись ответа":
            self.question.forced_close()
            self.question = QuestionUiInputAnswer(self, self)
        elif maket_name == "Выбор варианта(ов) ответа(ов)":
            self.question.forced_close()
            self.question = QuestionUiChoiceAnswer(self, self)
        elif maket_name == "Развернутый ответ (проверяется вручную)":
            self.question.forced_close()
            self.question = QuestionUiOpenAnswer(self, self)
        else:
            print("Неизвестный макет вопроса")
            print(maket_name)

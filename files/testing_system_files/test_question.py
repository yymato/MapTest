from files.testing_system_files.testing_ui_py_files.question_files.question_choice_answer import (
    QuestionUiChoiceAnswer)
from files.testing_system_files.testing_ui_py_files.question_files.question_input_answer import QuestionUiInputAnswer
from files.testing_system_files.testing_ui_py_files.question_files.question_open_answer import QuestionUiOpenAnswer
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QMessageBox
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
            if self.creator.is_open_quest:
                self.question.show()
                self.question.raise_()  # Форсируем окно на передний план
                self.question.activateWindow()  # Активируем окно, чтобы оно получило фокус
                self.creator.update_window_question.emit()
                # Проверим, видно ли оно на экране
                print(f"Окно QuestionWindow видимо: {self.question.isVisible()}")
                print(f"Размер окна: {self.question.size()}")
                self.question.move(100, 100)
            else:
                QMessageBox.warning(self, 'Окно вопроса уже открыто. Для продолжения закройте его.')


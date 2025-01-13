from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMessageBox
import random
# Импорт интерфейса формы выбора ответа
from files.testing_system_files.testing_ui_py_files.question_ui_py_files.question_ui_choice_answer import Ui_Form


class QuestionUiChoiceAnswer(Ui_Form, QMainWindow):
    """Класс, представляющий окно вопроса с выбором ответа."""

    def __init__(self, parent=None, icon_question=None):
        """
        Конструктор класса.

        :param parent: Родительский виджет (если есть).
        :param icon_question: Объект TestIconQuestion, содержащий информацию о вопросе.
        """
        super().__init__(parent)
        self.setupUi(self)  # Инициализация интерфейса
        self.question_plain_text.setReadOnly(True)  # Устанавливаем текст вопроса как только для чтения
        self.is_saved = False  # Флаг, указывающий, был ли сохранен ответ
        self.icon_question = icon_question  # Ссылка на объект с данными вопроса
        self.main_id = self.icon_question.main_id  # Основной идентификатор вопроса
        # Подключение обработчика к кнопке сохранения
        self.save_button.clicked.connect(self.save_answer)
        self.is_forced_close = True  # Флаг принудительного закрытия
        self.close()  # Закрытие окна после инициализации

    def load_variants(self, correct: list[str], incorrect: list[str]):
        """
        Загружает варианты ответов в виджет с сеткой.

        :param correct: Список правильных ответов.
        :param incorrect: Список неправильных ответов.
        """
        # Объединяем списки правильных и неправильных ответов
        variants = correct + incorrect
        # Перемешиваем варианты, чтобы не было предсказуемого порядка

        random.shuffle(variants)

        # Добавляем варианты ответов в сетку
        for i, variant in enumerate(variants):
            checkbox = QtWidgets.QCheckBox(variant)  # Создаем чекбокс для каждого варианта
            checkbox.setObjectName(f"variant_{i}")  # Устанавливаем уникальное имя
            self.checkbox_layout.addWidget(checkbox, i // 2, i % 2)  # Размещаем в сетке (по 2 в строке)

    def save_answer(self):
        """
        Сохраняет выбранные пользователем ответы в базу данных.
        """
        selected_answers = []  # Список выбранных пользователем ответов

        # Перебираем все элементы в сетке с вариантами
        for i in range(self.checkbox_layout.count()):
            widget = self.checkbox_layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QCheckBox) and widget.isChecked():
                selected_answers.append(widget.text())  # Добавляем текст выбранного варианта

        # Проверяем, чтобы был выбран хотя бы один ответ
        if not selected_answers:
            QMessageBox.warning(self, 'Ошибка', 'Выберите хотя бы один ответ перед сохранением.')
            return

        # Формируем строку из выбранных ответов с разделителем
        answers_string = "↑♛".join(selected_answers)

        # Сохраняем данные в базу данных
        if self.is_saved:
            # Обновление существующего ответа
            self.icon_question.cur.execute(
                'UPDATE answers SET answer = ? WHERE student_id = ?',
                (answers_string, self.icon_question.creator.student_id)
            )
            self.icon_question.con.commit()
            self.icon_question.creator.update_window_question.emit()

            self.forced_close()

        else:
            # Сохранение нового ответа
            self.icon_question.cur.execute(
                'INSERT INTO answers (question_main_id, student_id, answer) VALUES (?, ?, ?)',
                (self.main_id, self.icon_question.creator.student_id, answers_string)
            )
            self.icon_question.con.commit()
            QMessageBox.information(self, 'Сохранение', 'Ответ успешно сохранен!')
            self.icon_question.creator.update_window_question.emit()

            self.forced_close()

        self.is_saved = True  # Устанавливаем флаг сохранения

    def forced_close(self):
        """
        Принудительно закрывает окно без проверки.
        """
        self.is_forced_close = True
        self.close()

    def closeEvent(self, event):
        """
        Обработчик события закрытия окна. Спрашивает подтверждение у пользователя, если
        окно закрывается не принудительно.
        """
        if self.is_forced_close:
            self.is_forced_close = False
            event.accept()  # Закрываем окно без предупреждения
            return

        # Показываем окно подтверждения
        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно?'
            ' Изменения внесенные после нажатия кнопки "сохранить" не будут сохранены',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.icon_question.creator.update_window_question.emit()
            event.accept()  # Закрываем окно
        else:
            event.ignore()  # Отменяем закрытие

from PyQt6.QtWidgets import QMessageBox, QMainWindow

# Импортируем пользовательский интерфейс для работы с вопросами открытого ответа
from files.testing_system_files.testing_ui_py_files.question_ui_py_files.question_ui_open_answer import Ui_Form


class QuestionUiOpenAnswer(QMainWindow, Ui_Form):
    """Класс окна вопроса с развернутым ответом."""

    def __init__(self, parent=None, icon_question=None):
        """
        Инициализация окна вопроса с открытым ответом.

        :param parent: Родительский объект окна.
        :param icon_question: Ссылка на объект TestIconQuestion для взаимодействия с базой данных.
        """
        super().__init__(parent)
        self.setupUi(self)  # Инициализация элементов интерфейса
        self.question_plain_text.setReadOnly(True)  # Делаем текст вопроса только для чтения
        self.is_saved = False  # Флаг, указывающий, сохранен ли ответ
        self.is_forced_close = False  # Флаг для принудительного закрытия окна
        self.icon_question = icon_question  # Ссылка на объект TestIconQuestion
        self.main_id = self.icon_question.main_id  # ID вопроса в базе данных

        # Подключаем кнопку сохранения к методу save_answer
        self.save_button.clicked.connect(self.save_answer)
        self.forced_close()

    def save_answer(self):
        """
        Сохраняет текст ответа студента на вопрос.
        """
        # Получаем текст ответа из текстового поля
        answer_text = self.answer_plain_text.toPlainText().strip()

        # Проверяем, что текст ответа не пустой
        if not answer_text:
            QMessageBox.warning(self, 'Ошибка', 'Ответ не должен быть пустым.')
            return

        # Если ответ уже сохранен, обновляем существующую запись
        if self.is_saved:
            self.icon_question.cur.execute(
                'UPDATE answers SET answer = ? WHERE student_id = ?',
                (answer_text, self.icon_question.creator.student_id)
            )
            self.icon_question.con.commit()  # Сохраняем изменения в базе данных
            self.forced_close()

            return

        # Если ответ еще не сохранен, добавляем новую запись в базу данных
        self.icon_question.cur.execute(
            'INSERT INTO answers (question_main_id, student_id, answer) VALUES (?, ?, ?)',
            (self.main_id, self.icon_question.creator.student_id, answer_text)
        )
        self.icon_question.con.commit()  # Сохраняем изменения в базе данных

        # Сообщение об успешном сохранении
        QMessageBox.information(self, 'Сохранение', 'Вопрос успешно сохранен!')
        self.is_saved = True  # Устанавливаем флаг сохранения
        self.forced_close()

    def forced_close(self):
        """
        Выполняет принудительное закрытие окна.
        """
        self.is_forced_close = True  # Устанавливаем флаг принудительного закрытия
        self.close()  # Закрываем окно

    def closeEvent(self, event):
        """
        Обрабатывает событие закрытия окна.
        Если изменения не сохранены, показывает диалоговое окно с предупреждением.
        """
        if self.is_forced_close:  # Если закрытие было принудительным
            self.is_forced_close = False  # Сбрасываем флаг
            event.accept()  # Закрываем окно
            return

        # Показываем диалоговое окно подтверждения закрытия
        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно? '
            'Изменения внесенные после нажатия кнопки "сохранить" не будут сохранены',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Проверим, видно ли оно на экране
            print(f"Окно QuestionWindow видимо: {self.question.isVisible()}")
            print(f"Размер окна: {self.question.size()}")
            self.question.move(100, 100)
            event.accept()  # Подтверждаем закрытие окна
        else:
            event.ignore()  # Отменяем закрытие окна

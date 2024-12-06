from PyQt6.QtWidgets import QMainWindow, QMessageBox
from files.testing_system_files.testing_ui_py_files.question_ui_py_files.question_ui_input_answer import Ui_Form


# Класс для окна ввода ответа на вопрос
class QuestionUiInputAnswer(Ui_Form, QMainWindow):
    """Класс, представляющий окно вопроса с вводом ответа."""

    def __init__(self, parent=None, icon_question=None):
        """
        Конструктор класса.

        :param parent: Родительский объект (по умолчанию None).
        :param icon_question: Ссылка на объект TestIconQuestion.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Устанавливаем текст вопроса только для чтения
        self.question_plain_text.setReadOnly(True)

        # Флаг сохранения данных
        self.is_saved = False

        # Ссылка на объект TestIconQuestion
        self.icon_question = icon_question

        # Идентификатор главного вопроса
        self.main_id = self.icon_question.main_id

        # Подключаем сигнал нажатия кнопки "Сохранить" к методу сохранения
        self.save_button.clicked.connect(self.save_answer)

        # Флаг принудительного закрытия
        self.is_forced_close = True

        self.forced_close()

    def save_answer(self):
        """
        Сохраняет текст ответа на вопрос в базу данных.
        Если данные уже сохранены, выполняется обновление записи.
        """
        # Получаем текст ответа из соответствующего поля
        answer_text = self.answer_line_edit.text().strip()

        # Проверяем, чтобы поле ответа не было пустым
        if not answer_text:
            QMessageBox.warning(self, 'Ошибка', 'Ответ не должен быть пустым.')
            return

        if self.is_saved:
            # Обновляем существующую запись в базе данных
            self.icon_question.cur.execute(
                'UPDATE answers SET answer = ? WHERE student_id = ?',
                (answer_text, self.icon_question.creator.student_id)
            )
            self.icon_question.con.commit()

            self.forced_close()
            return

        # Добавляем новую запись в базу данных
        self.icon_question.cur.execute(
            'INSERT INTO answers (question_main_id, student_id, answer) VALUES (?, ?, ?)',
            (self.main_id, self.icon_question.creator.student_id, answer_text)
        )
        self.icon_question.con.commit()

        # Уведомляем пользователя об успешном сохранении
        QMessageBox.information(self, 'Сохранение', 'Вопрос успешно сохранен!')
        self.is_saved = True
        self.forced_close()

    def forced_close(self):
        """
        Принудительно закрывает окно, устанавливая соответствующий флаг.
        """
        self.is_forced_close = True
        self.close()

    def closeEvent(self, event):
        """
        Переопределяет событие закрытия окна. Если пользователь пытается закрыть окно,
        выводится предупреждение о несохраненных изменениях.
        """
        if self.is_forced_close:
            # Если окно закрывается принудительно, подтверждение не требуется
            self.is_forced_close = False
            event.accept()
            return

        # Показываем сообщение с запросом подтверждения закрытия
        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно?'
            ' Изменения внесенные после нажатия кнопки "сохранить" не будут сохранены',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # Если пользователь подтвердил закрытие
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Закрываем окно
        else:
            event.ignore()  # Отменяем закрытие окна

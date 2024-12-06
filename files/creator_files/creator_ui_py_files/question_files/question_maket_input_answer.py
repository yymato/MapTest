from files.creator_files.creator_ui_py_files.choosing_maket_ui import ChoosingMaketWindow
from PyQt6.QtWidgets import QMessageBox, QDialog
from PyQt6.QtWidgets import QMainWindow
from files.main_files.database.database_images import save_pixmap_to_db
from files.creator_files.creator_ui_py_files.question_ui_py_files.question_ui_maket_input_answer import Ui_Form


class QuestionUiMaketInputAnswer(QMainWindow, Ui_Form):
    def __init__(self, parent=None, icon_question=None):
        """
        :param parent: Родительский объект, если есть.
        :param icon_question: Объект, представляющий вопрос в виде иконки на главном окне
        """
        super().__init__(parent)
        self.setupUi(self)
        self.main_id = None  # Идентификатор текущего вопроса в базе данных

        # Ссылка на объект IconQuestion, отвечающий за управление текущим макетом
        self.icon_question = icon_question

        # Привязка кнопки "Изменить макет" к соответствующему методу
        self.choosing_maket_button.clicked.connect(self.change_maket)
        # Привязка кнопки "Сохранить" к методу сохранения данных
        self.save_button.clicked.connect(self.save_question)

        self.value_spinbox.setValue(1)  # Ставим начальное значение ценности вопроса
        self.is_forced_close = True  # Флаг, указывающий, что окно можно закрыть без предупреждения

        self.forced_close()

    def save_question(self):
        """Сохраняет текст вопроса и правильный ответ."""
        # Получаем текст вопроса из текстового поля
        question_text = self.question_plain_text.toPlainText().strip()
        # Получаем текст правильного ответа из текстового поля
        correct_answer = self.answer_line_edit.text().strip()

        # Проверяем, чтобы текст вопроса и правильный ответ не были пустыми
        if not question_text or not correct_answer:
            QMessageBox.warning(self, 'Ошибка', 'Текст вопроса и правильный ответ не должны быть пустыми.')
            return

        # Получаем позицию иконки вопроса
        pos = self.icon_question.creator.icon_positions[self.icon_question]

        # Если вопрос уже существует в базе данных, обновляем его
        if self.main_id is not None:
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('UPDATE question_data SET x = ?, y = ?, quest = ?,'
                                               ' answer = ?, type = ?, image = ? WHERE id = ?',
                                               (pos[0], pos[1], question_text, correct_answer, 2,
                                                save_pixmap_to_db(self.image_label.pixmap()), *quest_id))
                break
            self.icon_question.cur.execute('UPDATE question_values SET value = ? WHERE question_main_id = ?',
                                           (self.value_spinbox.value(), self.main_id))
            self.icon_question.con.commit()
            # Уведомляем пользователя об успешном сохранении
            QMessageBox.information(self, 'Сохранение', 'Вопрос и ответ успешно сохранены!')
            self.forced_close()
            return

        # Если вопрос новый, добавляем его в базу данных
        self.icon_question.cur.execute('INSERT INTO question_data (x, y, quest,'
                                       ' answer, type, image) VALUES (?, ?, ?, ?, ?, ?)',
                                       (pos[0], pos[1], question_text, correct_answer, 2,
                                        save_pixmap_to_db(self.image_label.pixmap())))

        # Получаем идентификатор нового вопроса и сохраняем его в таблицу `main_ids`
        for i in self.icon_question.cur.execute('SELECT id FROM question_data WHERE x = ?'
                                                ' AND y = ? AND quest = ? AND answer = ? AND type = ?',
                                                (pos[0], pos[1], question_text, correct_answer, 2)):
            self.icon_question.cur.execute('INSERT INTO main_ids (quest_id, type) VALUES (?, ?)', (*i, 2))
            for main_id in self.icon_question.cur.execute('SELECT main_id FROM main_ids WHERE quest_id = ?', (*i,)):
                self.main_id = int(*main_id)  # Сохраняем `main_id` для дальнейшего использования
            break

        self.icon_question.cur.execute('INSERT INTO question_values (question_main_id, value) VALUES (?, ?)',
                                       (self.main_id, self.value_spinbox.value()))

        self.icon_question.con.commit()

        # Уведомляем пользователя об успешном сохранении
        QMessageBox.information(self, 'Сохранение', 'Вопрос и ответ успешно сохранены!')
        self.forced_close()

    def sql_delete(self):
        """Удаляет вопрос из базы данных."""
        # Если `main_id` определен, удаляем связанный вопрос и идентификатор из базы данных
        if self.main_id is not None:
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('DELETE FROM question_data WHERE id = ?', (*quest_id,))
                self.icon_question.cur.execute('DELETE FROM main_ids WHERE main_id = ?', (self.main_id,))
                break
            self.icon_question.con.commit()
            self.deleteLater()  # Удаляем объект из памяти

    def change_maket(self):
        """Открывает окно выбора макета и обновляет макет вопроса в IconQuestion."""
        # Создаем окно выбора макета
        choosing_maket_window = ChoosingMaketWindow(self)

        # Открываем окно выбора макета и ждем его завершения
        if choosing_maket_window.exec() == QDialog.DialogCode.Accepted:
            # Если пользователь подтвердил выбор, обновляем макет
            selected_maket = choosing_maket_window.selected_maket
            self.icon_question.set_question_maket(selected_maket)

    def forced_close(self):
        """Принудительно закрывает окно без предупреждения."""
        self.is_forced_close = True
        self.close()

    def closeEvent(self, event):
        """Отображает предупреждение при попытке закрытия окна."""
        # Если флаг принудительного закрытия установлен, закрываем окно без предупреждения
        if self.is_forced_close:
            self.is_forced_close = False
            event.accept()
            return

        # Показываем диалоговое окно подтверждения закрытия
        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно?'
            ' Изменения внесенные после нажатия кнопки "сохранить" не будут сохранены',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # Если пользователь согласился, закрываем окно
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            # Иначе отменяем закрытие окна
            event.ignore()

from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
from files.main_files.database.database_images import save_pixmap_to_db
from files.creator_files.creator_ui_py_files.choosing_maket_ui import ChoosingMaketWindow
from files.creator_files.creator_ui_py_files.question_ui_py_files.question_ui_maket_open_answer import Ui_Form


class QuestionUiMaketOpenAnswer(QMainWindow, Ui_Form):
    def __init__(self, parent=None, icon_question=None):
        """
        :param parent: Родительский объект, если есть.
        :param icon_question: Объект, представляющий вопрос, для взаимодействия с макетом.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Ссылка на объект IconQuestion для замены макета
        self.icon_question = icon_question
        self.main_id = None

        # Привязка кнопки "Сохранить" к методу сохранения вопроса
        self.save_button.clicked.connect(self.save_question)

        # Привязка кнопки "Изменить макет" к методу изменения макета
        self.choosing_maket_button.clicked.connect(self.change_maket)

        # Флаг для отслеживания принудительного закрытия окна
        self.is_forced_close = True
        self.close()

    def change_maket(self):
        """
        Открывает окно выбора макета и обновляет макет вопроса в IconQuestion,
        если пользователь подтвердил выбор.
        """
        choosing_maket_window = ChoosingMaketWindow(self)

        # Открываем окно выбора макета и ожидаем завершения действия пользователя
        if choosing_maket_window.exec() == QDialog.DialogCode.Accepted:
            # Получаем выбранный макет и обновляем его в объекте IconQuestion
            selected_maket = choosing_maket_window.selected_maket
            self.icon_question.set_question_maket(selected_maket)

    def save_question(self):
        """
        Сохраняет текст вопроса, его параметры и изображение в базу данных.
        Проверяет, чтобы поля не были пустыми, и выполняет соответствующие запросы.
        """
        # Получаем текст вопроса
        question_text = self.question_plain_text.toPlainText().strip()

        # Проверяем, чтобы текст вопроса не был пустым
        if not question_text:
            QMessageBox.warning(self, 'Ошибка', 'Текст вопроса не должен быть пустым.')
            return

        # Получаем координаты позиции вопроса
        pos = self.icon_question.creator.icon_positions[self.icon_question]

        # Если main_id уже существует, обновляем запись в базе данных
        if self.main_id is not None:
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('UPDATE question_data SET x = ?, y = ?, quest = ?,'
                                               ' answer = ?, type = ?, image = ? WHERE id = ?',
                                               (pos[0], pos[1], question_text, '', 1,
                                                save_pixmap_to_db(self.image_label.pixmap()), *quest_id))
                break
            self.icon_question.con.commit()
            self.forced_close()
            return

        # Если main_id отсутствует, создаем новую запись в базе данных
        self.icon_question.cur.execute('INSERT INTO question_data (x, y, quest,'
                                       ' answer, type, image) VALUES (?, ?, ?, ?, ?, ?)',
                                       (pos[0], pos[1], question_text, '', 1,
                                        save_pixmap_to_db(self.image_label.pixmap())))

        # Получаем ID созданного вопроса и добавляем в таблицу идентификаторов
        for i in self.icon_question.cur.execute('SELECT id FROM question_data WHERE x = ?'
                                                ' AND y = ? AND quest = ? AND type = ?',
                                                (pos[0], pos[1], question_text, 1)):
            self.icon_question.cur.execute('INSERT INTO main_ids (quest_id, type) VALUES (?, ?)', (*i, 1))
            for main_id in self.icon_question.cur.execute('SELECT main_id FROM main_ids WHERE quest_id = ?', (*i,)):
                self.main_id = str(*main_id)
            break

        self.icon_question.con.commit()
        QMessageBox.information(self, 'Сохранение', 'Вопрос успешно сохранен!')
        self.forced_close()

    def sql_delete(self):
        """
        Удаляет вопрос из базы данных и очищает связанные записи.
        """
        if self.main_id is not None:
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('DELETE FROM question_data WHERE id = ?', (*quest_id,))
                self.icon_question.cur.execute('DELETE FROM main_ids WHERE main_id = ?', (self.main_id,))
                break
            self.icon_question.con.commit()
            self.deleteLater()

    def forced_close(self):
        """
        Выполняет принудительное закрытие окна без дополнительных предупреждений.
        """
        self.is_forced_close = True
        self.close()

    def closeEvent(self, event):
        """
        Переопределяет событие закрытия окна. Предупреждает пользователя
        о несохраненных изменениях, если закрытие не принудительное.

        :param event: Событие закрытия окна.
        """
        if self.is_forced_close:
            # Если закрытие принудительное, пропускаем предупреждение
            self.is_forced_close = False
            event.accept()
            return

        # Отображаем диалог подтверждения закрытия окна
        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно?'
            ' Изменения, внесенные после нажатия кнопки "Сохранить", не будут сохранены.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Закрываем окно, если пользователь подтвердил действие
            event.accept()
        else:
            # Отменяем закрытие, если пользователь отказался
            event.ignore()

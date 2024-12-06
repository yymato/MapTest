from files.main_files.database.database_images import save_pixmap_to_db
from files.creator_files.creator_ui_py_files.choosing_maket_ui import ChoosingMaketWindow
from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
from files.creator_files.creator_ui_py_files.question_ui_py_files.question_ui_maket_choice_answer import Ui_Form
from PyQt6 import QtGui


class QuestionUiMaketChoiceAnswer(Ui_Form, QMainWindow):
    def __init__(self, parent=None, icon_question=None):
        """
        :param parent: Родительский объект, если есть.
        :param icon_question: Объект, представляющий вопрос в виде иконки на главном окне
        """

        super().__init__(parent)
        self.setupUi(self)

        self.main_id = None  # Идентификатор текущего вопроса в базе данных

        # Ссылка на объект IconQuestion для управления макетом вопроса
        self.icon_question = icon_question

        # Привязка кнопки "Изменить макет" к методу изменения макета
        self.choosing_maket_button.clicked.connect(self.change_maket)

        # Привязка кнопки "Добавить ответ" к методу добавления нового варианта ответа
        self.add_variant_button.clicked.connect(self.add_variant)

        # Инициализация модели для отображения списка ответов
        self.variant_list_model = QtGui.QStandardItemModel()
        self.variant_list_view.setModel(self.variant_list_model)

        # Привязка кнопки "Сохранить" к методу сохранения вопроса
        self.save_button.clicked.connect(self.save_question)

        # Ставим начальное значение ценности вопроса
        self.value_spinbox.setValue(1)

        # Флаг для принудительного закрытия окна
        self.is_forced_close = True

        self.forced_close()

    def save_question(self):
        """
        Сохраняет текст вопроса и ответы в базу данных.
        """
        # Получение текста вопроса
        question_text = self.question_plain_text.toPlainText().strip()

        # Разделение ответов на правильные и неправильные
        correct_answer = []
        incorrect_answer = []
        for row in range(self.variant_list_model.rowCount()):
            ans = self.variant_list_model.item(row)
            if '(!Правильный!)' in ans.text():
                correct_answer.append(ans.text()[:-len('(!Правильный!)')])  # Убираем разделитель
            else:
                incorrect_answer.append(ans.text())

        # Проверка наличия хотя бы одного правильного ответа
        if not correct_answer:
            QMessageBox.warning(self, 'Ошибка', 'Должен быть хотя бы один правильный ответ.')
            return

        # Проверка на пустой текст вопроса
        if not question_text:
            QMessageBox.warning(self, 'Ошибка', 'Текст вопроса не должен быть пустым.')
            return

        # Координаты и макет текущего вопроса
        pos = self.icon_question.creator.icon_positions[self.icon_question]

        if self.main_id is not None:
            # Обновление существующего вопроса в базе данных
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('UPDATE choice_question_data SET x = ?, y = ?, quest = ?,'
                                               ' correct_answers = ?, incorrect_answers = ?, image = ? WHERE id = ?',
                                               (pos[0], pos[1], question_text, '↑♛'.join(correct_answer),
                                                '↑♛'.join(incorrect_answer),
                                                save_pixmap_to_db(self.image_label.pixmap()), *quest_id))
                break
            self.icon_question.cur.execute('UPDATE question_values SET value = ? WHERE question_main_id = ?',
                                           (self.value_spinbox.value(), self.main_id))
            self.icon_question.con.commit()
            self.forced_close()
            return

        # Вставка нового вопроса в базу данных
        self.icon_question.cur.execute('INSERT INTO choice_question_data (x, y, quest,'
                                       ' correct_answers, incorrect_answers, image) VALUES (?, ?, ?, ?, ?, ?)',
                                       (pos[0], pos[1], question_text, '↑♛'.join(correct_answer),
                                        '↑♛'.join(incorrect_answer), save_pixmap_to_db(self.image_label.pixmap())))

        # Получение ID нового вопроса для сохранения в связанную таблицу
        for i in self.icon_question.cur.execute('SELECT id FROM choice_question_data WHERE x = ?'
                                                ' AND y = ? AND quest = ? AND correct_answers = ? AND'
                                                ' incorrect_answers = ?',
                                                (pos[0], pos[1], question_text, '↑♛'.join(correct_answer),
                                                 '↑♛'.join(incorrect_answer))):
            self.icon_question.cur.execute('INSERT INTO main_ids (quest_id, type) VALUES (?, ?)', (*i, 3))

            for main_id in self.icon_question.cur.execute('SELECT main_id FROM main_ids WHERE quest_id = ?', (*i,)):
                self.main_id = str(*main_id)
            break
        self.icon_question.cur.execute('INSERT INTO question_values (question_main_id, value) VALUES (?, ?)',
                                       (self.main_id, self.value_spinbox.value()))
        self.icon_question.con.commit()
        QMessageBox.information(self, 'Сохранение', 'Вопрос и ответ успешно сохранены!')
        self.forced_close()

    def sql_delete(self):
        """
        Удаляет текущий вопрос из базы данных.
        """
        if self.main_id is not None:
            for quest_id in self.icon_question.cur.execute('SELECT quest_id FROM main_ids '
                                                           'WHERE main_id = ?', (self.main_id,)):
                self.icon_question.cur.execute('DELETE FROM question_data WHERE id = ?', (*quest_id,))
                self.icon_question.cur.execute('DELETE FROM main_ids WHERE main_id = ?', (self.main_id,))
                break
            self.icon_question.con.commit()
            self.deleteLater()

    def add_variant(self):
        """
        Добавляет новый вариант ответа в список.
        """
        # Получаем текст из поля ввода и проверяем его корректность
        text = self.answer_plain_text.toPlainText().strip()
        is_correct = self.is_right_check_box.isChecked()

        if text:
            # Формируем текст с пометкой правильного ответа, если требуется
            item_text = f"{text} {'(!Правильный!)' if is_correct else ''}"
            item = QtGui.QStandardItem(item_text)

            # Добавляем вариант в список
            self.variant_list_model.appendRow(item)

            # Очищаем поле ввода ответа и сбрасываем чекбокс
            self.answer_plain_text.clear()
            self.is_right_check_box.setChecked(False)

    def load_variants(self, correct, incorrect):
        """
        Загружает правильные и неправильные варианты в список.
        """
        for cor_answer in correct:
            item_text = f"{cor_answer} {'(!Правильный!)'}"
            item = QtGui.QStandardItem(item_text)
            self.variant_list_model.appendRow(item)

        for incor_answer in incorrect:
            item_text = f"{incor_answer}"
            item = QtGui.QStandardItem(item_text)
            self.variant_list_model.appendRow(item)

    def change_maket(self):
        """
        Открывает окно для выбора нового макета и обновляет его.
        """
        choosing_maket_window = ChoosingMaketWindow(self)

        # Если выбор макета подтвержден, обновляем его в объекте IconQuestion
        if choosing_maket_window.exec() == QDialog.DialogCode.Accepted:
            selected_maket = choosing_maket_window.selected_maket
            self.icon_question.set_question_maket(selected_maket)

    def forced_close(self):
        """
        Принудительно закрывает окно без дополнительных вопросов.
        """
        self.is_forced_close = True
        self.close()

    def closeEvent(self, event):
        """
        Обрабатывает событие закрытия окна, предупреждая о несохраненных изменениях.
        """
        if self.is_forced_close:
            self.is_forced_close = False
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение закрытия',
            'Вы действительно хотите закрыть окно? '
            'Изменения, внесенные после нажатия кнопки "Сохранить", не будут сохранены.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Закрываем окно
        else:
            event.ignore()  # Отменяем закрытие окна

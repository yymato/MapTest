from msilib.schema import tables

import xlsxwriter
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from files.main_files.interpreter_result_files.interpreter_result_ui_py.interpreter_result_ui import Ui_MainWindow
import sqlite3


class InterpreterResultWindow(QMainWindow, Ui_MainWindow):
    close_window = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.test_db_path = None
        self.answers_db_path = None
        self.res_path = None

        self.choose_question_path_button.clicked.connect(self.choose_question_path)

        self.choose_answer_path_button.clicked.connect(self.choose_answer_path)

        self.choose_result_path_button.clicked.connect(self.choose_result_path)

    def choose_question_path(self):
        test_db_path = QFileDialog.getOpenFileName(self, "Открыть файл с тестом", "", "SQL Files (*.sqlite)")[0]
        # Проверям таблицу на то, что это тест
        try:
            conn = sqlite3.connect(test_db_path)
            tables = conn.cursor().execute('SELECT name FROM sqlite_master WHERE type="table"')
            quest_reference = set(['type', 'sqlite_sequence', 'question_data', 'main_ids', 'choice_question_data', 'main_image',
                     'question_values'])
            if set(*tables) & quest_reference != quest_reference:
                raise Exception
        except:
            QMessageBox.warning(self, 'Ошибка', 'Не корректный файл. Возможно, вы выбрали ответы, а не вопросы.')

    def choose_answer_path(self):
        answers_db_path = QFileDialog.getOpenFileName(self, "Открыть файл с ответами", "", "SQL Files (*.sqlite)")[0]
        try:
            conn = sqlite3.connect(answers_db_path)
            tables = conn.cursor().execute('SELECT name FROM sqlite_master WHERE type="table"')
            answer_reference = set(['type', 'sqlite_sequence', 'answers', 'students'])
            if set(*tables) & answer_reference != answer_reference:
                raise Exception
        except:
            QMessageBox.warning(self, 'Ошибка', 'Не корректный файл. Возможно, вы выбрали вопросы, а не ответы.')

    def choose_result_path(self):
        res_path = QFileDialog.getOpenFileName(self, "Сохранить файл", "", "SQL Files (*.sqlite)")[0]
        try:
            conn = sqlite3.connect(res_path)
            tables = conn.cursor().execute('SELECT name FROM sqlite_master WHERE type="table"')
        except:
            pass

    def get_result(self):
        conn_test = sqlite3.connect(self.test_db_path)
        cursor_test = conn_test.cursor()

        question_test_data = []
        for i in cursor_test.execute('SELECT * FROM main_ids').fetchall():
            if i[2] == 3:  # Вопрос с выбором вариантов
                data = list(
                    *cursor_test.execute('SELECT quest, correct_answers FROM choice_question_data WHERE id = ?',
                                         (i[1],)).fetchall())
                question_test_data.append([i[0], i[2], data[0], data[1]])
            else:  # Остальные вопросы
                data = list(
                    *cursor_test.execute('SELECT quest, answer FROM question_data WHERE id = ?',
                                         (i[1],)).fetchall())
                question_test_data.append([i[0], i[2], data[0], data[1]])

        # Получаем стоимость вопросов
        question_values = {row[0]: row[1] for row in
                           cursor_test.execute('SELECT question_main_id, value FROM question_values').fetchall()}

        # Подключаемся к базе данных с ответами
        conn_answers = sqlite3.connect(self.answers_db_path)
        cursor_answers = conn_answers.cursor()

        cursor_answers.execute("SELECT student_id, question_main_id, answer FROM answers")
        answers = cursor_answers.fetchall()

        # Словарь вопросов
        question_data = {}
        for q in question_test_data:
            question_data[q[0]] = {
                'question': q[2],
                'correct_answer': q[3],
                'type': q[1],
                'value': question_values.get(q[0], 1)  # По умолчанию вес 1
            }
        print(question_data)
        # ФИО студентов
        student_fio_id = {}
        for i in cursor_answers.execute('SELECT * FROM students').fetchall():
            student_fio_id[i[0]] = i[1]

        # Создаем Excel
        workbook = xlsxwriter.Workbook(
            QFileDialog.getSaveFileName(self, "Сохранение результата", "", "Excel files (*.xlsx *.xls)")[0])
        format_correct = workbook.add_format({'bg_color': '#C6EFCE'})
        format_incorrect = workbook.add_format({'bg_color': '#FFC7CE'})
        format_partial = workbook.add_format({'bg_color': '#FFEB9C'})  # Желтый для частично правильных

        # --- Лист 1: Типы 2 и 3 ---
        sheet1 = workbook.add_worksheet('Автоматическая проверка')

        # Формируем шапку
        sheet1.write(0, 0, 'ФИО студента')
        col = 1
        question_ids_type2_3 = []
        for q in question_test_data:
            if q[1] in [2, 3]:  # Только вопросы типа 2 и 3
                sheet1.write(0, col, f'ID {q[0]}')
                sheet1.write(0, col + 1, f'Прав. {q[0]}')
                question_ids_type2_3.append(q[0])
                sheet1.set_column(col, col + 1, 15)  # Устанавливаем ширину колонок
                col += 2

        sheet1.write(0, col, 'Процент правильности')

        # Заполняем лист 1
        row = 1
        student_answers = {student_id: {} for student_id in student_fio_id}

        for student_id, question_main_id, student_answer in answers:
            if question_main_id in question_ids_type2_3:
                student_answers[student_id][question_main_id] = student_answer
        print(student_answers)

        for student_id, answers_dict in student_answers.items():
            student_fio = student_fio_id.get(student_id, 'Неизвестно')
            sheet1.write(row, 0, student_fio)

            col = 1
            total_score = 0
            total_value = 0  # Общая стоимость вопросов

            for q_id in question_ids_type2_3:
                correct_answer = question_data[q_id]['correct_answer']
                question_value = question_data[q_id]['value']
                total_value += question_value

                student_answer = answers_dict.get(q_id, '')

                if question_data[q_id]['type'] == 3:
                    # Записываем ответ студента с заменой разделителя
                    formatted_student_answer = ' '.join(student_answer.split('↑♛'))
                    formatted_correct_answer = ' '.join(correct_answer.split('↑♛'))
                    sheet1.write(row, col, formatted_student_answer)
                    sheet1.write(row, col + 1, formatted_correct_answer)

                    # Проверка на частичную правильность по системе штрафов
                    student_answers_set = set(student_answer.split('↑♛'))
                    correct_answers_set = set(correct_answer.split('↑♛'))
                    correct_count = len(student_answers_set & correct_answers_set)
                    incorrect_count = len(student_answers_set - correct_answers_set)
                    total_correct = len(student_answers_set)
                    # Делим разность правильных и не правильных ответов на количество правильных ответов
                    partial_score = ((correct_count - incorrect_count) / total_correct) * question_data[q_id]['value']

                    if ((correct_count - incorrect_count) / total_correct) == 1:  # Полностью правильно
                        sheet1.write(row, col, formatted_student_answer, format_correct)
                        sheet1.write(row, col + 1, formatted_correct_answer, format_correct)
                        total_score += question_data[q_id]['value']
                    elif ((correct_count - incorrect_count) / total_correct) > 0:  # Частично правильно
                        sheet1.write(row, col, formatted_student_answer, format_partial)
                        sheet1.write(row, col + 1, formatted_correct_answer, format_partial)
                        total_score += partial_score
                    else:  # Полностью неправильно
                        sheet1.write(row, col, formatted_student_answer, format_incorrect)
                        sheet1.write(row, col + 1, formatted_correct_answer, format_incorrect)

                else:
                    # Тип 2: обычное сравнение
                    sheet1.write(row, col, student_answer)
                    sheet1.write(row, col + 1, correct_answer)
                    if student_answer.lower() == correct_answer.lower():
                        sheet1.write(row, col, student_answer, format_correct)
                        sheet1.write(row, col + 1, correct_answer, format_correct)
                        total_score += question_value
                    else:
                        sheet1.write(row, col, student_answer, format_incorrect)
                        sheet1.write(row, col + 1, correct_answer, format_incorrect)

                col += 2

            # Рассчитываем процент
            if total_value > 0:
                score_percentage = (total_score / total_value) * 100
            else:
                score_percentage = 0
            sheet1.write(row, col, f"{score_percentage:.2f}%")
            row += 1

        # --- Лист 2: Тип 1 ---
        sheet2 = workbook.add_worksheet('Ручная проверка')

        # Формируем шапку
        sheet2.write(0, 0, 'ФИО студента')
        col = 1
        question_ids_type1 = []
        for q in question_test_data:
            if q[1] == 1:  # Только вопросы типа 1
                sheet2.write(0, col, f'ID {q[0]}')
                question_ids_type1.append(q[0])
                sheet2.set_column(col, col, 15)
                col += 1

        # Заполняем лист 2
        row = 1
        for student_id, question_main_id, student_answer in answers:
            if question_main_id in question_ids_type1:
                student_fio = student_fio_id.get(student_id, 'Неизвестно')
                sheet2.write(row, 0, student_fio)
                col = question_ids_type1.index(question_main_id) + 1
                sheet2.write(row, col, student_answer)
                row += 1

        # --- Лист 3: Вопросы ---
        sheet3 = workbook.add_worksheet('Вопросы')
        sheet3.write(0, 0, 'ID вопроса')
        sheet3.write(0, 1, 'Текст вопроса')
        sheet3.write(0, 2, 'Стоимость')

        row = 1
        for q in question_test_data:
            sheet3.write(row, 0, q[0])
            sheet3.write(row, 1, q[2])
            sheet3.write(row, 2, question_data[q[0]]['value'])
            row += 1

        # Закрываем файл
        workbook.close()
        conn_test.close()
        conn_answers.close()

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
            event.accept()  # Закрываем окно
            self.close_window.emit()
        else:
            event.ignore()  # Отменяем закрытие

import sys
import sqlite3
import xlsxwriter
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from files.testing_system_files.main_testing_window import MainTestingWindow
from files.main_files.ui_py_files.main_ui import Ui_MainWindow
from files.creator_files.creator import CreatorWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Главное окно приложения для работы с тестами.
    """

    def __init__(self):
        """
        Инициализация главного окна приложения.
        """
        super().__init__()
        self.setupUi(self)

        self.creator = None
        self.test = None
        self.create_testButton.clicked.connect(self.create_test)
        self.starting_testButton.clicked.connect(self.starting_test)
        self.interpreter_result_button.clicked.connect(self.interpreter_result)

        self.is_open = False

    def create_test(self):
        """
        Открывает окно для создания нового теста.
        """
        if not self.is_open:
            self.creator = CreatorWindow(self)
            self.creator.close_window.connect(self.closed_window)

            self.creator.show()
            self.is_open = True

    def starting_test(self):
        """
        Открывает окно для прохождения теста.
        """
        if not self.is_open:
            self.test = MainTestingWindow(self)
            self.test.close_window.connect(self.closed_window)
            self.test.connect_to_bds()
            self.test.show()
            self.is_open = True

    def closed_window(self):
        """
        Закрывает окна редактора и теста.
        """
        self.is_open = False

    def interpreter_result(self):
        # Путь к файлам с тестом и результатами
        test_db_path = QFileDialog.getOpenFileName(self, "Открыть файл с тестом", "", "SQL Files (*.sqlite)")[0]
        answers_db_path = QFileDialog.getOpenFileName(self, "Открыть файл с ответами", "", "SQL Files (*.sqlite)")[0]

        # Подключаемся к базе данных с тестами
        conn_test = sqlite3.connect(test_db_path)
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
        conn_answers = sqlite3.connect(answers_db_path)
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


def except_hook(cls, exception, traceback):
    """
    Обработчик исключений для корректной работы PyQt.
    """
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    """
    Основная точка входа приложения.
    """
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())

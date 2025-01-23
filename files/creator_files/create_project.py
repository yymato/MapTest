import io

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from files.CONSTANT import HISTORY_PATH_QUESTION, HISTORY_PATH_IMAGES, HISTORY_PATH_PROJECT
from files.creator_files.creator_ui_py_files.create_project_ui import Ui_MainWindow


class ProjectCreateWindow(Ui_MainWindow, QMainWindow):
    
    successful_save_project = pyqtSignal()
    cancel_save_project = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)    
        
        self.project_path = None

        self.image_path = None

        self.choose_project_path_button.clicked.connect(self.choose_project_path)
        self.choose_image_path_button.clicked.connect(self.choose_image_path)
        self.accept_button.clicked.connect(self.save_project)
        self.cancel_button.clicked.connect(self.close)

        self.project_path_combo_box.currentIndexChanged.connect(self.on_project_path_changed)
        self.image_path_combo_box.currentIndexChanged.connect(self.on_image_path_changed)

        self.update_project_history('init')
        self.update_image_history('init')

    def update_project_history(self, data):
        if data != 'init':
            # Обновляем историю для проекта
            if data:
                if self.project_path != data:  # Предотвращаем повторную запись одинакового пути
                    self.project_path = data
                    with open(HISTORY_PATH_QUESTION, 'a+') as history_path:
                        history_path.seek(0)  # Перемещаем указатель в начало файла
                        paths = history_path.readlines()
                        if self.project_path + '\n' not in paths:  # Если путь еще не в истории
                            history_path.write(self.project_path + '\n')

            # Загружаем и обновляем QComboBox для проектов
        try:
            with open(HISTORY_PATH_QUESTION, 'r') as history_path:
                paths = [line.strip() for line in history_path.readlines()]

            # Удаляем старые элементы и добавляем уникальные последние 10 путей
            self.project_path_combo_box.clear()
            for path in paths[-10:][::-1]:
                if path.strip():
                    self.project_path_combo_box.addItem(path.strip())

            if data == 'init' or self.project_path is None:
                self.project_path_combo_box.setCurrentIndex(-1)
        except io.UnsupportedOperation:
            pass

    def update_image_history(self, data):
        if data != 'init':
            if data:
                if self.image_path != data:  # Предотвращаем повторную запись одинакового пути
                    self.image_path = data
                    with open(HISTORY_PATH_IMAGES, 'a+') as history_path:
                        history_path.seek(0)  # Перемещаем указатель в начало файла
                        paths = history_path.readlines()
                        if self.image_path + '\n' not in paths:  # Если путь еще не в истории
                            history_path.write(self.image_path + '\n')

        # Загружаем и обновляем QComboBox для изображений
        try:
            with open(HISTORY_PATH_IMAGES, 'r') as history_path:
                paths = [line.strip() for line in history_path.readlines()]

            # Удаляем старые элементы и добавляем уникальные последние 10 путей
            self.image_path_combo_box.clear()
            for path in paths[-10:][::-1]:
                if path.strip():
                    self.image_path_combo_box.addItem(path.strip())

            if self.image_path is None or data == 'init':
                self.image_path_combo_box.setCurrentIndex(-1)
        except io.UnsupportedOperation:
            pass

    def choose_project_path(self):
        project_path = QFileDialog.getSaveFileName(self, 'Сохранить тест',
        self.name_line_edit.text(), 'Тесты (*.sqlite)')[0]
        if project_path:
            self.update_project_history(project_path)

    def choose_image_path(self):
        image_path = QFileDialog.getOpenFileName(self, 'Открыть изображение', '',
                                                      'Изображения (*.jpeg, *.jpg, *.png)')[0]
        if image_path:
            if image_path.split('.')[-1] in ['jpeg', 'jpg', 'png']:
                self.update_image_history(image_path)
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не корректный формат изображения')

    def save_project(self):
        if self.project_path and self.image_path and self.name_line_edit.text():
            self.successful_save_project.emit()
            self.close()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')

    def get_project_path(self):
        return self.project_path

    def get_image_path(self):
        return self.image_path

    def get_name_project(self):
        return self.name_line_edit.text()

    def closeEvent(self, event):
        if not (self.project_path and self.image_path and self.name_line_edit.text()):
            self.cancel_save_project.emit()
        else:
            with open(HISTORY_PATH_PROJECT, 'a+') as history_path:
                history_path.seek(0)  # Перемещаем указатель в начало файла
                paths = history_path.readlines()
                if self.project_path + '\n' not in paths:  # Если путь еще не в истории
                    history_path.write(self.project_path + '\n')
                else:
                    # Удаляем путь из списка и добавляем его в конец
                    paths.remove(self.project_path + '\n')
                    paths.append(self.project_path + '\n')
                    # Перемещаем указатель в начало и перезаписываем файл
                    history_path.seek(0)
                    history_path.truncate()
                    history_path.writelines(paths)

        event.accept()

    def on_project_path_changed(self):
        # Устанавливаем путь проекта при изменении комбобокса
        self.project_path = self.project_path_combo_box.currentText()

    def on_image_path_changed(self):
        # Устанавливаем путь изображения при изменении комбобокса
        self.image_path = self.image_path_combo_box.currentText()

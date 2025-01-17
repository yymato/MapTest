from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

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

    def choose_project_path(self):
        self.project_path = QFileDialog.getSaveFileName(self, 'Сохранить тест',
        self.name_line_edit.text(), 'Тесты (*.sqlite)')[0]

    def choose_image_path(self):
        image_path = QFileDialog.getOpenFileName(self, 'Открыть изображение', '',
                                                      'Изображения (*.jpeg, *.jpg, *.png)')[0]

        if image_path.split('.')[-1] in ['jpeg', 'jpg', 'png']:
            self.image_path = image_path
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

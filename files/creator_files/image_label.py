from PyQt6.QtCore import Qt, pyqtSignal  # Основные константы и сигналы Qt
from PyQt6.QtGui import QPixmap, QMouseEvent, QContextMenuEvent, QAction  # Работа с изображениями и событиями мыши
from PyQt6.QtWidgets import QFileDialog, QMenu  # Диалоговое окно для выбора файлов
from PyQt6.QtWidgets import QLabel  # Виджет для отображения текста или изображений


class ImageLabel(QLabel):
    # Определение пользовательского сигнала, который будет испускаться при установке изображения
    UpdateImage = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.type == QMouseEvent:
            self.replace_image_action_triggered()

    def contextMenuEvent(self, event):
        if isinstance(event, QContextMenuEvent):
            # Создать контекстное меню
            menu = QMenu(self)

            # Добавить действия в контекстное меню и связать их с сигналами
            replace_image_action = QAction("Заменить", self)
            change_image_action = QAction("Редактировать (В разработке)", self)

            replace_image_action.triggered.connect(self.replace_image_action_triggered)
            change_image_action.triggered.connect(self.change_image_action_triggered)

            # Добавить действия в меню
            menu.addAction(replace_image_action)
            menu.addAction(change_image_action)

            change_image_action.setEnabled(False)  # Редактирование в разаработке

            # Показать контекстное меню в позиции курсора
            menu.exec(event.globalPos())

    def change_image_action_triggered(self):
        # TODO Реализовать редактор изображения
        pass

    def replace_image_action_triggered(self):
        """Обработка события двойного клика мыши по QLabel."""
        # Открываем диалоговое окно для выбора изображения
        file_name = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if file_name and file_name.split('.') in ['jpeg', 'jpg', 'png']:  # Если пользователь выбрал файл
            self.set_my_image(file_name)

    def set_my_image(self, filename):
        """Установка изображения в QLabel по указанному пути."""
        if filename:  # Проверяем, что путь к файлу не пустой
            pixmap = filename
            if not isinstance(filename, QPixmap):
                pixmap = QPixmap(filename)  # Создаем QPixmap из файла


            # Масштабируем изображение, чтобы оно пропорционально вписалось в размеры QLabel
            scaled_pixmap = pixmap.scaled(
                self.size(),  # Размеры QLabel
                Qt.AspectRatioMode.KeepAspectRatio,  # Сохранение пропорций изображения
                Qt.TransformationMode.SmoothTransformation  # Плавное масштабирование
            )

            # Рассчитываем отступы, чтобы изображение оказалось по центру, если оно меньше QLabel
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = (self.height() - scaled_pixmap.height()) // 2

            # Устанавливаем изображение в QLabel
            self.setPixmap(scaled_pixmap)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем изображение внутри QLabel
            # Устанавливаем отступы для центрирования, если изображение меньше QLabel
            self.setContentsMargins(x_offset, y_offset, x_offset, y_offset)
            self.UpdateImage.emit()

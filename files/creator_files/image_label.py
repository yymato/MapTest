from PyQt6.QtCore import Qt, pyqtSignal  # Основные константы и сигналы Qt
from PyQt6.QtGui import QPixmap, QMouseEvent  # Работа с изображениями и событиями мыши
from PyQt6.QtWidgets import QFileDialog  # Диалоговое окно для выбора файлов
from PyQt6.QtWidgets import QLabel  # Виджет для отображения текста или изображений


class ImageLabel(QLabel):
    # Определение пользовательского сигнала, который будет испускаться при установке изображения
    UpdateImage = pyqtSignal()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Обработка события двойного клика мыши по QLabel."""
        if event.button() == Qt.MouseButton.LeftButton:  # Проверяем, что двойной клик был левой кнопкой мыши
            # Открываем диалоговое окно для выбора изображения
            fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
            if fname:  # Если пользователь выбрал файл
                pixmap = QPixmap(fname)  # Создаем QPixmap из выбранного файла

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

                # Испускаем пользовательский сигнал, чтобы уведомить об установке изображения
                self.UpdateImage.emit()

    def set_my_image(self, fname):
        """Установка изображения в QLabel по указанному пути."""
        if fname:  # Проверяем, что путь к файлу не пустой
            pixmap = fname
            if not isinstance(fname, QPixmap):
                pixmap = QPixmap(fname)  # Создаем QPixmap из файла


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

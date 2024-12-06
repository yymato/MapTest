from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap


class TestImageLabel(QLabel):
    def my_pixmap(self, fname):
        if fname:
            pixmap = QPixmap(fname)

            # Масштабируем изображение, чтобы оно поместилось в QLabel
            scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)

            # Центрируем изображение
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = (self.height() - scaled_pixmap.height()) // 2

            # Устанавливаем изображение в QLabel с учетом центрирования
            self.setPixmap(scaled_pixmap)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем изображение внутри QLabel
            # Применяем смещение, если изображение меньше QLabel
            self.setContentsMargins(x_offset, y_offset, x_offset, y_offset)

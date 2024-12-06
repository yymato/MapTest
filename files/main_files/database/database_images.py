from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap


def save_pixmap_to_db(pixmap: QPixmap) -> bytes:
    """
    Конвертирует картинку в BLOB для сохранения в SQL-БД
    :param pixmap: Картинка.
    """

    if pixmap is not None:
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)  # Используем OpenModeFlag.WriteOnly
        pixmap.save(buffer, "PNG")  # Сохраняем изображение в формате PNG
        buffer.close()
        return byte_array.data()  # Возвращаем данные в виде байтов
    else:
        return bytes()


def load_pixmap_from_db(byte_image: bytes) -> QPixmap:
    """
    Преобразуем данные из BLOB в QPixmap
    :param byte_image: Картинка в бинарном виде.
    """
    if byte_image is None:
        return QPixmap()

    if isinstance(byte_image, bytes):
        byte_array = QByteArray(byte_image)
    else:
        byte_array = byte_image  # Если это уже QByteArray, используем его напрямую

    pix_image = QPixmap()
    pix_image.loadFromData(byte_array, "PNG")  # Загружаем изображение из данных

    return pix_image

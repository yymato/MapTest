import os
import sys


def resource_path(relative_path):
    """Возвращает путь к ресурсам в скомпилированном приложении."""
    try:
        # Для скомпилированного файла PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Для обычной разработки
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

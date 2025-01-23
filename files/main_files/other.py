from PyQt6.QtWidgets import QPushButton


class ListWidgetButton(QPushButton):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data

    def get_data(self) -> str:
        return self.data

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QWidget, QMessageBox
)

from function import util


class ThemeButton(QPushButton):
    def __init__(self, name, color, parent=None):
        super().__init__(name, parent)
        self.name = name
        self.color = color
        if color == "#FFFFFF":  # 如果是亮色主题，使用黑色文字
            self.setStyleSheet(f"background-color: {color}; color: black; padding: 20px; font-size: 14px;")
        else:  # 暗色主题使用白色文字
            self.setStyleSheet(f"background-color: {color}; color: white; padding: 20px; font-size: 14px;")


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("主题设置")
        self.setFixedSize(300, 200)  # 设置固定窗口大小

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Title
        title_label = QLabel("选择主题", self)
        title_label.setStyleSheet("font-size: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        # 主题按钮
        self.dark_button = ThemeButton("暗色主题", "#272C35", self)
        self.light_button = ThemeButton("亮色主题", "#FFFFFF", self)

        self.dark_button.clicked.connect(lambda: self.apply_theme("dark"))
        self.light_button.clicked.connect(lambda: self.apply_theme("light"))

        self.main_layout.addWidget(self.dark_button)
        self.main_layout.addWidget(self.light_button)

    def apply_theme(self, theme_type):
        if self.parent:
            # 保存主题设置到配置文件
            file_path = util.get_config_path('theme.json')
            data = util.read_json(file_path)
            
            if theme_type == "dark":
                self.parent.setDarkTheme()
                data['theme'] = "暗色主题"
                data['theme_color'] = "#272C35"
            else:
                self.parent.setLightTheme()
                data['theme'] = "亮色主题"
                data['theme_color'] = "#FFFFFF"
            
            # 将修改后的数据写回 JSON 文件
            util.write_json(file_path, data)
            util.THEME = data
            
            #QMessageBox.information(self, "切换主题", "主题切换成功")
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

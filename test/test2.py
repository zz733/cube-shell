import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题
        self.setWindowTitle("File Upload Example")

        # 创建布局
        layout = QVBoxLayout()

        # 创建 QLabel 用于显示文件路径
        self.file_path_label = QLabel()
        layout.addWidget(self.file_path_label)

        # 创建上传按钮
        upload_button = QPushButton("Upload")
        upload_button.clicked.connect(self.upload_file)

        # 添加控件到布局
        layout.addWidget(upload_button)

        # 创建主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def upload_file(self):
        # 假设文件路径已经预先设定
        file_path = "/path/to/your/file.txt"

        # 显示文件路径
        self.file_path_label.setText(file_path)

        # 在这里实现上传文件的功能
        print(f"Uploading file: {file_path}")


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFileDialog
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题
        self.setWindowTitle("上传文件")

        # 创建布局
        layout = QVBoxLayout()

        # 创建按钮
        select_files_button = QPushButton("选择文件")

        # 连接按钮信号
        select_files_button.clicked.connect(self.select_files)

        # 添加控件到布局
        layout.addWidget(select_files_button)

        # 创建主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def select_files(self):
        # 打开文件对话框让用户选择文件
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        if files:
            # 显示所选文件的路径
            print(files)
            # self.file_path_edit.setText(", ".join(files))

    def upload_files(self):
        # 在这里实现上传文件的功能
        file_paths = self.file_path_edit.text().split(", ")
        for file_path in file_paths:
            print(f"Uploading file: {file_path}")


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QPushButton, QVBoxLayout, QWidget


def choose_directory():
    directory = QFileDialog.getExistingDirectory(
        None,  # 父窗口，这里为None表示没有父窗口
        '选择保存文件夹',  # 对话框标题
        '',  # 默认打开目录
        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks  # 显示选项
    )
    if directory:
        print(f"Selected directory: {directory}")


app = QApplication(sys.argv)

# 创建一个简单的界面，包含一个按钮
window = QWidget()
layout = QVBoxLayout(window)
button = QPushButton("Choose Directory")
button.clicked.connect(choose_directory)
layout.addWidget(button)

window.show()

sys.exit(app.exec())

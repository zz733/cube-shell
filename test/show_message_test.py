from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer


def show_message():
    msg_box = QMessageBox()
    msg_box.setWindowTitle("提示")
    msg_box.setText("这是一个简单的提示信息！")
    msg_box.setStandardButtons(QMessageBox.NoButton)  # 不显示任何按钮

    # 使用 QTimer 单次触发来自动关闭消息框
    timer = QTimer(msg_box)
    timer.singleShot(1000, msg_box.close)  # 1000毫秒后关闭消息框
    msg_box.exec_()


if __name__ == "__main__":
    app = QApplication([])

    show_message()

    app.exec_()

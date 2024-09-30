from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from function import util


class AboutDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("关于 cubeShell")
        # self.setGeometry(300, 300, 400, 300)
        # 设置窗口大小固定
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Logo
        logo_label = QLabel(self)
        logo_pixmap = QPixmap("docs/images/docs-log.png")
        # 调整图片大小
        scaled_pixmap = logo_pixmap.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # 版本号
        version_label = QLabel(f"版本：  {util.THEME['version']}\n\n作者：     寒暄\n\n\r\r\r\r公众号：  IT技术小屋", self)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # 简洁信息
        info_label = QLabel("cubeShell 是 Linux 服务器远程管理工具。"
                            "\n可以代替 Xshell、XSftp 等工具，对远程服务器进行管理。"
                            "\n 简洁、方便、强大", self)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        self.setLayout(layout)

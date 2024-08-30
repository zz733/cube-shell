import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题
        self.setWindowTitle("QTreeWidget Multi-Column Example")

        # 创建 QTreeWidget
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["文件名", "文件大小", "修改日期", "权限", "所有者/组"])

        # 添加根节点
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, "Root Item噩耗推背图河北他和融合Berger二个人  二个人感染")
        root_item.setText(1, "1kb")
        root_item.setText(2, "2024-08-28")
        root_item.setText(3, "root")
        root_item.setText(4, "root2")


        root_item1 = QTreeWidgetItem(self.tree_widget)
        root_item1.setText(0, "Root Item2")
        root_item1.setText(1, "1kb")
        root_item1.setText(2, "2024-08-28")
        root_item1.setText(3, "root")
        root_item1.setText(4, "root")

        # 启用排序
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.sortItems(0, Qt.AscendingOrder)  # 默认按第一列升序排列
        self.tree_widget.resizeColumnToContents(0)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)

        # 创建主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

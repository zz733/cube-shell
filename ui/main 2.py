# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton,
    QSizePolicy, QSplitter, QTabWidget, QTextBrowser, QTextEdit,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1303, 837)
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        
        # 主布局
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        
        # 主分割器
        self.splitter_3 = QSplitter(Qt.Horizontal)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setCursor(Qt.ArrowCursor)
        
        # 设备列表
        self.gridLayoutWidget = QWidget()
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.treeWidget = QTreeWidget(self.gridLayoutWidget)
        self.treeWidget.setMinimumWidth(200)
        self.treeWidget.setHeaderLabels(["设备列表"])
        self.treeWidget.setCursor(Qt.ArrowCursor)
        self.gridLayout.addWidget(self.treeWidget, 1, 0)
        self.splitter_3.addWidget(self.gridLayoutWidget)
        
        # 中间分割器
        self.splitter_255 = QSplitter(Qt.Horizontal)
        self.splitter_255.setObjectName(u"splitter_255")
        self.splitter_255.setCursor(Qt.ArrowCursor)
        
        # Shell标签页区域
        self.gridLayoutWidget_3 = QWidget()
        self.gridLayout_6 = QGridLayout(self.gridLayoutWidget_3)
        
        # 垂直分割器
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setCursor(Qt.ArrowCursor)
        self.splitter.setMinimumWidth(888)
        
        # Shell标签页
        self.verticalLayoutWidget = QWidget()
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.ShellTab = QTabWidget(self.verticalLayoutWidget)
        self.ShellTab.setObjectName(u"ShellTab")
        self.ShellTab.setStyleSheet(u"QTabWidget::tab-bar { left: 0px; }")
        self.ShellTab.setCursor(Qt.ArrowCursor)
        
        # 首页标签
        self.index = QWidget()
        self.index.setObjectName(u"index")
        self.verticalLayout_5 = QVBoxLayout(self.index)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        
        # 首页内容
        self.verticalLayout_6 = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setMinimumHeight(517)
        self.gridLayout_2 = QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 117, 0, 117)
        self.gridLayout_2.setSpacing(0)
        
        # 快捷键标签
        labels = [
            ("添加配置 Shift+Command+A", 0),
            ("添加隧道 Shift+Command+S", 1),
            ("帮助 Shift+Command+P", 2),
            ("关于 Shift+Command+B", 4),
            ("查找命令行 Shift+Command+C", 6),
            ("导入配置 Shift+Command+I", 7),
            ("导出配置 Shift+Command+E", 8)
        ]
        
        for text, row in labels:
            label = QLabel(self.widget)
            label.setText(text)
            label.setCursor(Qt.ArrowCursor)
            self.gridLayout_2.addWidget(label, row, 0)
        
        self.verticalLayout_6.addWidget(self.widget, 0, Qt.AlignVCenter)
        self.verticalLayout_5.addLayout(self.verticalLayout_6)
        
        self.ShellTab.addTab(self.index, "首页")
        
        self.verticalLayout.addWidget(self.ShellTab)
        self.splitter.addWidget(self.verticalLayoutWidget)
        
        # 状态显示区域
        self.verticalLayoutWidget_2 = QWidget()
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setContentsMargins(3, 0, 3, 0)
        
        # CPU监控
        self.label = QLabel(self.verticalLayoutWidget_2)
        self.label.setText("CPU监控")
        self.label.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label, 0, 0)
        
        self.cpuRate = QProgressBar(self.verticalLayoutWidget_2)
        self.cpuRate.setObjectName(u"cpuRate")
        self.cpuRate.setValue(0)
        self.cpuRate.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.cpuRate, 0, 1)
        
        # 网络上行
        self.label_6 = QLabel(self.verticalLayoutWidget_2)
        self.label_6.setText("网络上行")
        self.label_6.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label_6, 0, 2)
        
        self.networkUpload = QLineEdit(self.verticalLayoutWidget_2)
        self.networkUpload.setObjectName(u"networkUpload")
        self.networkUpload.setReadOnly(True)
        self.networkUpload.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.networkUpload, 0, 3)
        
        # 内存监控
        self.label_2 = QLabel(self.verticalLayoutWidget_2)
        self.label_2.setText("内存监控")
        self.label_2.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label_2, 1, 0)
        
        self.memRate = QProgressBar(self.verticalLayoutWidget_2)
        self.memRate.setObjectName(u"memRate")
        self.memRate.setValue(0)
        self.memRate.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.memRate, 1, 1)
        
        # 网络下行
        self.label_5 = QLabel(self.verticalLayoutWidget_2)
        self.label_5.setText("网络下行")
        self.label_5.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label_5, 1, 2)
        
        self.networkDownload = QLineEdit(self.verticalLayoutWidget_2)
        self.networkDownload.setObjectName(u"networkDownload")
        self.networkDownload.setReadOnly(True)
        self.networkDownload.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.networkDownload, 1, 3)
        
        # 磁盘监控
        self.label_3 = QLabel(self.verticalLayoutWidget_2)
        self.label_3.setText("磁盘监控")
        self.label_3.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label_3, 2, 0)
        
        self.diskRate = QProgressBar(self.verticalLayoutWidget_2)
        self.diskRate.setObjectName(u"diskRate")
        self.diskRate.setValue(0)
        self.diskRate.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.diskRate, 2, 1)
        
        # 操作系统
        self.label_4 = QLabel(self.verticalLayoutWidget_2)
        self.label_4.setText("操作系统")
        self.label_4.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.label_4, 2, 2)
        
        self.operatingSystem = QLineEdit(self.verticalLayoutWidget_2)
        self.operatingSystem.setObjectName(u"operatingSystem")
        self.operatingSystem.setReadOnly(True)
        self.operatingSystem.setCursor(Qt.ArrowCursor)
        self.gridLayout_8.addWidget(self.operatingSystem, 2, 3)
        
        self.verticalLayout_2.addLayout(self.gridLayout_8)
        self.splitter.addWidget(self.verticalLayoutWidget_2)
        
        self.gridLayout_6.addWidget(self.splitter, 0, 0)
        self.splitter_255.addWidget(self.gridLayoutWidget_3)
        self.splitter_3.addWidget(self.splitter_255)
        
        # 添加主分割器到主布局
        self.gridLayout_5.addWidget(self.splitter_3, 0, 0)
        
        # 聊天区域布局
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        
        # 聊天历史记录
        self.chatHistoryTextEdit = QTextEdit(self.centralwidget)
        self.chatHistoryTextEdit.setObjectName(u"chatHistoryTextEdit")
        self.chatHistoryTextEdit.setReadOnly(True)
        self.chatHistoryTextEdit.setMinimumWidth(250)
        self.chatHistoryTextEdit.setMaximumWidth(250)
        self.chatHistoryTextEdit.setPlaceholderText("聊天记录将显示在这里...")
        self.chatHistoryTextEdit.setCursor(Qt.ArrowCursor)
        self.verticalLayout_3.addWidget(self.chatHistoryTextEdit)
        
        # 输入区域布局
        self.chatInputLayout = QHBoxLayout()
        self.chatInputLayout.setObjectName(u"chatInputLayout")
        
        # 聊天输入框
        self.chatInputLineEdit = QLineEdit(self.centralwidget)
        self.chatInputLineEdit.setObjectName(u"chatInputLineEdit")
        self.chatInputLineEdit.setMinimumHeight(30)
        self.chatInputLineEdit.setPlaceholderText(u"请输入消息...")
        self.chatInputLineEdit.setCursor(Qt.ArrowCursor)
        self.chatInputLayout.addWidget(self.chatInputLineEdit)
        
        # 发送按钮
        self.sendMessageButton = QPushButton(self.centralwidget)
        self.sendMessageButton.setObjectName(u"sendMessageButton")
        self.sendMessageButton.setMinimumSize(QSize(80, 30))
        self.sendMessageButton.setText(u"发送")
        self.sendMessageButton.setCursor(Qt.ArrowCursor)
        self.chatInputLayout.addWidget(self.sendMessageButton)
        
        # 将输入区域添加到聊天区域布局
        self.verticalLayout_3.addLayout(self.chatInputLayout)
        
        # 将聊天区域添加到主布局
        self.gridLayout_5.addLayout(self.verticalLayout_3, 0, 1)
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        pass

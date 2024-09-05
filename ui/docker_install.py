# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'docker_install.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
                               QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
                               QSizePolicy, QTextBrowser, QVBoxLayout, QWidget, QPushButton)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(597, 551)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_labels = QLineEdit(Dialog)
        self.lineEdit_labels.setObjectName(u"lineEdit_labels")
        font = QFont()
        font.setPointSize(16)
        self.lineEdit_labels.setFont(font)

        self.gridLayout.addWidget(self.lineEdit_labels, 5, 1, 1, 1)

        self.lineEdit_environmentVariables = QLineEdit(Dialog)
        self.lineEdit_environmentVariables.setObjectName(u"lineEdit_environmentVariables")
        self.lineEdit_environmentVariables.setFont(font)

        self.gridLayout.addWidget(self.lineEdit_environmentVariables, 4, 1, 1, 1)

        self.label_ports = QLabel(Dialog)
        self.label_ports.setObjectName(u"label_ports")
        self.label_ports.setFont(font)

        self.gridLayout.addWidget(self.label_ports, 2, 0, 1, 1)

        self.lineEdit_ports = QLineEdit(Dialog)
        self.lineEdit_ports.setObjectName(u"lineEdit_ports")
        self.lineEdit_ports.setFont(font)

        self.gridLayout.addWidget(self.lineEdit_ports, 2, 1, 1, 1)

        self.label_containerName = QLabel(Dialog)
        self.label_containerName.setObjectName(u"label_containerName")
        self.label_containerName.setFont(font)

        self.gridLayout.addWidget(self.label_containerName, 0, 0, 1, 1)

        self.label_labels = QLabel(Dialog)
        self.label_labels.setObjectName(u"label_labels")
        self.label_labels.setFont(font)

        self.gridLayout.addWidget(self.label_labels, 5, 0, 1, 1)

        self.label_Image = QLabel(Dialog)
        self.label_Image.setObjectName(u"label_Image")
        self.label_Image.setFont(font)

        self.gridLayout.addWidget(self.label_Image, 1, 0, 1, 1)

        self.label_environmentVariables = QLabel(Dialog)
        self.label_environmentVariables.setObjectName(u"label_environmentVariables")
        self.label_environmentVariables.setFont(font)

        self.gridLayout.addWidget(self.label_environmentVariables, 4, 0, 1, 1)

        self.lineEdit_containerName = QLineEdit(Dialog)
        self.lineEdit_containerName.setObjectName(u"lineEdit_containerName")
        self.lineEdit_containerName.setFont(font)

        self.gridLayout.addWidget(self.lineEdit_containerName, 0, 1, 1, 1)

        self.label_privileged = QLabel(Dialog)
        self.label_privileged.setObjectName(u"label_privileged")
        self.label_privileged.setFont(font)

        self.gridLayout.addWidget(self.label_privileged, 6, 0, 1, 1)

        self.lineEdit_Image = QLineEdit(Dialog)
        self.lineEdit_Image.setObjectName(u"lineEdit_Image")
        self.lineEdit_Image.setFont(font)

        self.gridLayout.addWidget(self.lineEdit_Image, 1, 1, 1, 1)

        self.checkBox_privileged = QCheckBox(Dialog)
        self.checkBox_privileged.setObjectName(u"checkBox_privileged")
        self.checkBox_privileged.setFont(font)

        self.gridLayout.addWidget(self.checkBox_privileged, 6, 1, 1, 1)

        self.label_volumes = QLabel(Dialog)
        self.label_volumes.setObjectName(u"label_volumes")

        self.gridLayout.addWidget(self.label_volumes, 3, 0, 1, 1)

        self.lineEdit_volumes = QLineEdit(Dialog)
        self.lineEdit_volumes.setObjectName(u"lineEdit_volumes")

        self.gridLayout.addWidget(self.lineEdit_volumes, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.textBrowserDockerInout = QTextBrowser(Dialog)
        self.textBrowserDockerInout.setObjectName(u"textBrowserDockerInout")
        self.verticalLayout.addWidget(self.textBrowserDockerInout)

        self.buttonBoxDockerInstall = QDialogButtonBox(Dialog)
        self.buttonBoxDockerInstall.setObjectName(u"buttonBoxDockerInstall")
        self.buttonBoxDockerInstall.setOrientation(Qt.Orientation.Horizontal)
       # self.buttonBoxDockerInstall.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        cancel_button = QPushButton("取消")
        ok_button = QPushButton("安装")
        # 将自定义按钮添加到按钮框
        self.buttonBoxDockerInstall.addButton(ok_button, QDialogButtonBox.AcceptRole)
        self.buttonBoxDockerInstall.addButton(cancel_button, QDialogButtonBox.RejectRole)

        self.verticalLayout.addWidget(self.buttonBoxDockerInstall)


        self.retranslateUi(Dialog)
        self.buttonBoxDockerInstall.accepted.connect(Dialog.accept)
        self.buttonBoxDockerInstall.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_ports.setText(QCoreApplication.translate("Dialog", u"\u7aef\u53e3\u6620\u5c04", None))
        self.label_containerName.setText(QCoreApplication.translate("Dialog", u"\u5bb9\u5668\u540d\u79f0", None))
        self.label_labels.setText(QCoreApplication.translate("Dialog", u"\u9644\u52a0\u53c2\u6570", None))
        self.label_Image.setText(QCoreApplication.translate("Dialog", u"\u955c\u50cf\u540d\u79f0", None))
        self.label_environmentVariables.setText(QCoreApplication.translate("Dialog", u"\u73af\u5883\u53d8\u91cf", None))
        self.label_privileged.setText(QCoreApplication.translate("Dialog", u"\u5f00\u542fPrivileged\u7279\u6743", None))
        self.checkBox_privileged.setText("")
        self.label_volumes.setText(QCoreApplication.translate("Dialog", u"\u6302\u8f7d\u6587\u4ef6", None))
    # retranslateUi


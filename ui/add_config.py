# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QSizePolicy, QWidget)

from style.style import PrimaryButtonStyle


class Ui_addConfig(object):
    def setupUi(self, addConfig):
        if not addConfig.objectName():
            addConfig.setObjectName(u"addConfig")
        addConfig.resize(300, 300)
        self.layoutWidget = QWidget(addConfig)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 40, 251, 238))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTabletTracking(False)

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setTabletTracking(False)

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.pushButton = QPushButton(self.layoutWidget)
        self.pushButton.setStyleSheet(PrimaryButtonStyle)
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 5, 0, 1, 2)

        self.ipEdit = QLineEdit(self.layoutWidget)
        self.ipEdit.setObjectName(u"ipEdit")
        self.ipEdit.setTabletTracking(False)
        self.ipEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.gridLayout.addWidget(self.ipEdit, 3, 1, 1, 2)

        self.usernamEdit = QLineEdit(self.layoutWidget)
        self.usernamEdit.setObjectName(u"usernamEdit")
        self.usernamEdit.setTabletTracking(False)
        self.usernamEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.gridLayout.addWidget(self.usernamEdit, 1, 1, 1, 2)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setTabletTracking(False)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setTabletTracking(False)

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.passwordEdit = QLineEdit(self.layoutWidget)
        self.passwordEdit.setObjectName(u"passwordEdit")
        self.passwordEdit.setTabletTracking(False)
        self.passwordEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.passwordEdit, 2, 1, 1, 2)

        self.configName = QLineEdit(self.layoutWidget)
        self.configName.setObjectName(u"configName")
        self.configName.setTabletTracking(False)
        self.configName.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.gridLayout.addWidget(self.configName, 0, 1, 1, 2)

        self.pushButton_2 = QPushButton(self.layoutWidget)
        self.pushButton_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 5, 2, 1, 1)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.protEdit = QLineEdit(self.layoutWidget)
        self.protEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.protEdit, 4, 1, 1, 2)

        self.retranslateUi(addConfig)

        QMetaObject.connectSlotsByName(addConfig)

    # setupUi

    def retranslateUi(self, addConfig):
        addConfig.setWindowTitle(QCoreApplication.translate("addConfig", u"\u6dfb\u52a0\u8bbe\u5907", None))
        self.label_3.setText(QCoreApplication.translate("addConfig", u"IP\u5730\u5740\uff1a", None))
        self.label_4.setText(QCoreApplication.translate("addConfig", u"\u914d\u7f6e\u540d\uff1a", None))
        self.pushButton.setText(QCoreApplication.translate("addConfig", u"\u786e\u8ba4", None))
        self.ipEdit.setText("")
        self.ipEdit.setPlaceholderText(
            QCoreApplication.translate("addConfig", u"\u8bf7\u8f93\u5165\u7ec8\u7aef\u5730\u5740", None))
        self.usernamEdit.setText("")
        self.usernamEdit.setPlaceholderText(
            QCoreApplication.translate("addConfig", u"\u8bf7\u8f93\u5165\u7ec8\u7aef\u7528\u6237\u540d", None))
        self.label.setText(QCoreApplication.translate("addConfig", u"\u7528\u6237\u540d\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("addConfig", u"\u5bc6  \u7801\uff1a", None))
        self.passwordEdit.setText("")
        self.passwordEdit.setPlaceholderText(
            QCoreApplication.translate("addConfig", u"\u8bf7\u8f93\u5165\u7ec8\u7aef\u5bc6\u7801", None))
        self.configName.setText("")
        self.configName.setPlaceholderText(
            QCoreApplication.translate("addConfig", u"\u8bf7\u8f93\u5165\u914d\u7f6e\u540d\u79f0", None))
        self.pushButton_2.setText(QCoreApplication.translate("addConfig", u"\u53d6\u6d88", None))
        self.label_5.setText(QCoreApplication.translate("addConfig", u"\u7aef\u53e3", None))
        self.protEdit.setText(QCoreApplication.translate("addConfig", u"22", None))
        self.protEdit.setPlaceholderText(
            QCoreApplication.translate("addConfig", u"\u8bf7\u8f93\u5165\u7aef\u53e3", None))
    # retranslateUi

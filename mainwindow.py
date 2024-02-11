from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import *
from subwindow import SubWindow

class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow,self).__init__()
        # 总体界面
        self.setWindowTitle("相机标定程序")
        self.resize(525,425)
        # 元素
        # 两个按钮
        self.OpenButton = QPushButton("加载图像")
        self.HelpButton = QPushButton("帮助")
        # 三个标签
        self.label_h = QLabel("棋盘格长：")
        self.label_w = QLabel("棋盘格宽：")
        self.label_s = QLabel("棋盘格尺寸：")
        # 三个数字输入框
        self.spin_h = QSpinBox()
        self.spin_w = QSpinBox()
        self.spin_s = QSpinBox()
        # 布局初始化
        self.layout_init()
        # 按钮初始化
        self.button_init()

    def button_init(self):
        self.OpenButton.clicked.connect(self.readImgae)
        self.HelpButton.clicked.connect(self.help)

    def layout_init(self):

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(330, 30, 121, 321))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget_1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout_1")

        self.verticalLayout.addWidget(self.OpenButton)
        self.verticalLayout.addWidget(self.HelpButton)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(50, 30, 202, 321))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout_h = QtWidgets.QHBoxLayout()
        self.horizontalLayout_h.addWidget(self.label_h)
        self.horizontalLayout_h.addWidget(self.spin_h)
        self.verticalLayout_2.addLayout(self.horizontalLayout_h)

        self.horizontalLayout_w = QtWidgets.QHBoxLayout()
        self.horizontalLayout_w.addWidget(self.label_w)
        self.horizontalLayout_w.addWidget(self.spin_w)
        self.verticalLayout_2.addLayout(self.horizontalLayout_w)

        self.horizontalLayout_s = QtWidgets.QHBoxLayout()
        self.horizontalLayout_s.addWidget(self.label_s)
        self.horizontalLayout_s.addWidget(self.spin_s)
        self.verticalLayout_2.addLayout(self.horizontalLayout_s)

    def readImgae(self):

        if self.spin_w.value() == 0 or self.spin_h.value() == 0 or self.spin_s.value() == 0:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setText("错误")
            error_message.setInformativeText("请正确填写标定板数据。")
            error_message.setWindowTitle("错误")
            error_message.exec_()
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_dialog = QFileDialog()
            selected_files, _ = file_dialog.getOpenFileNames(None, "选择图片", "",
                                                             "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
                                                             options=options)
            if selected_files:
                subWin = SubWindow(self.spin_w.value(), self.spin_h.value(), self.spin_s.value())
                subWin.load_from_paths(selected_files)
                subWin.show()
                subWin.exec_()
            else:
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Critical)
                error_message.setText("错误")
                error_message.setInformativeText("没有选择文件，请重新选择。")
                error_message.setWindowTitle("错误")
                error_message.exec_()

    def help(self):
        help_message = QMessageBox()
        help_message.setIcon(QMessageBox.Question)
        help_message.setText("帮助")
        help_message.setInformativeText("这是一个相机标定软件，输入棋盘格的长和宽以及方格尺寸后，点击加载图像，选择相应图像后即可完成标定。")
        help_message.setWindowTitle("帮助")
        help_message.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 实例父页面
    window = MyWindow()
    window.show()
    sys.exit(app.exec())








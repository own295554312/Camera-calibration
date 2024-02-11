from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from Calibration import *

class ImageListWidget(QListWidget):
    def __init__(self):
        super(ImageListWidget, self).__init__()
        self.setFlow(QListView.Flow(1))#0: left to right,1: top to bottom
        self.setIconSize(QSize(150,100))

    def add_image_items(self,image_paths=[]):
        for img_path in image_paths:
            if os.path.isfile(img_path):
                img_name = os.path.basename(img_path)
                item = QListWidgetItem(QIcon(img_path),img_name)
                self.addItem(item)

class SubWindow(QDialog):
    def __init__(self,w,h,s):
        super(SubWindow, self).__init__()
        self.w = w
        self.h = h
        self.s = s
        # 总体界面
        self.setWindowTitle("相机标定程序")
        self.resize(1000, 800)

        self.list_widget = ImageListWidget()
        self.list_widget.setMinimumWidth(200)

        self.show_label = QLabel(self)
        self.show_label.setFixedSize(600, 400)
        self.image_paths = []
        self.currentImgIdx = 0
        self.currentImg = None

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(270, 500, 121, 321))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget_1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout_1")

        self.CalButton = QPushButton("开始标定")
        self.CalButton.clicked.connect(self.Calibration)

        self.verticalLayout.addWidget(self.CalButton)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.show_label)
        self.layout.addWidget(self.list_widget)

        self.list_widget.itemSelectionChanged.connect(self.loadImage)

    def load_from_paths(self, img_paths=[]):
        self.image_paths = img_paths
        self.list_widget.add_image_items(img_paths)

    def loadImage(self):
        self.currentImgIdx = self.list_widget.currentIndex().row()
        if self.currentImgIdx in range(len(self.image_paths)):
            self.currentImg = QPixmap(self.image_paths[self.currentImgIdx]).scaledToHeight(400)
            self.show_label.setPixmap(self.currentImg)

    def Calibration(self):

        HandP = [calculationHomography(image_path, self.h, self.w, self.s) for image_path in self.image_paths]
        H_matrices = [item[0] for item in HandP]
        img_points = [item[1] for item in HandP]
        H_matrices = np.array(H_matrices)
        img_points = np.array(img_points)
        # 通过单应矩阵计算内参矩阵
        K, lambda1 = compute_K(H_matrices)
        rank = np.linalg.matrix_rank(K)
        # 计算外参矩阵
        RT_mats = np.array(compute_RT(H_matrices, K, lambda1))
        # 内参矩阵齐次化
        K = np.hstack([K, np.zeros((3, 1))])
        # 计算重投影误差
        dis = reprojectError(K, RT_mats, img_points, self.w, self.h, self.s)
        print("相机内参为：")
        print(K)
        print("平均重投影误差为：")
        print(dis)




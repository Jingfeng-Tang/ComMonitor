from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt as qwe, pyqtSignal, QPoint
#起别名qwe,防止与Pyqt5.qt冲突
from PyQt5 import QtGui
from PyQt5 import QtCore
'''由于软件界面继承QMainWindow，不能重写mouseEvent，所以在
软件上方画了一个widget对象，写一个widget类，重写mouseEvent'''
class widgetdrag(QWidget):

    pressDragFlag = 0
    globalPos = QPoint()
    pressPos = QPoint()

    getMovePosSignal = pyqtSignal(int,int)

    def mousePressEvent(self, QMouseEvent):
        global pressDragFlag
        global pressPos
        print("mousePressEvent")
        try:
            # 鼠标左键
            if QMouseEvent.button() == qwe.LeftButton:
                pressDragFlag = 1
                self.setCursor(QtGui.QCursor(qwe.ClosedHandCursor))
                pressPos = self.mapToGlobal(QMouseEvent.pos())  # 屏幕坐标
                print("左键按下")
            else:
                print("右键按下")
        except Exception as e:
            print("except:", e)

    def mouseMoveEvent(self, QMouseEvent):
        global pressDragFlag
        global globalPos

        globalPos = self.mapToGlobal(QMouseEvent.pos())#屏幕坐标
        #print(x, y)
        #获取当前鼠标指针在软件界面中的坐标
        #根据鼠标指针偏移量计算QRect，对当前软件界面重新绘制？
        print("mouseMoveEvent")
        pressDragFlag = 1
        '''try:
            # 鼠标左键
            if QMouseEvent.button() == qwe.LeftButton:
                pressDragFlag = 1
                print("左键移动")
            else:
                print(456)
        except Exception as e:
            print("except:", e)'''

    def mouseReleaseEvent(self, QMouseEvent):
        global pressDragFlag
        global globalPos
        global pressPos
        print("mouseReleaseEvent")
        try:
            # 鼠标左键
            if QMouseEvent.button() == qwe.LeftButton:
                pressDragFlag = 0
                self.setCursor(QtGui.QCursor(qwe.OpenHandCursor))
                print(1)
                print(pressPos.x(),pressPos.y())
                print(2)
                print(globalPos.x(), globalPos.y())
                chazhi = QPoint
                chazhi = pressPos-globalPos
                self.getMovePosSignal.emit(chazhi.x(),chazhi.y())#发送信号
                print("左键放开")
            else:
                print("右键放开")
        except Exception as e:
            print("except:", e)


"""@name:     ComMonitor
   @author:   tangjf
   @date:     2022/5/7"""


#显示ui
import gui
import sys
import time
import identifySerialPort as isp
from PyQt5 import QtCore
from PyQt5.Qt import *
from PyQt5.QtCore import Qt, QFile, QTextStream, QIODevice, QByteArray, QUrl
from binascii import unhexlify, hexlify
import csv
import re
import organizeMessage
import crcmod


#初始化
windowMaximinzedFlag = 0
#列表记录comboBox_port的序号到端口号的映射
comboBoxPortNoToportNo = []
msgNumber = 0
portStateFlag = 0

#添加校验码flag
addCheckFlag = False


#串口信息
#创建一个字典存储串口默认信息
comPortInfo = { "portNo":1,
                "Baud":115200,
                "dataBit":8,
                "parityBit":0,
                "stopBit":1
                }
#创建元组存储波特率数值
baudAllInfo = (115200, 57600, 56000, 38400, 19200, 14400, 9600, 4800, 2400, 1200, 600, 300, 110)

#创建元组存储数据位
dataBitsAllInfo = (8, 7, 6)

#创建元组存储校验位
parityBitAllInfo = (8, 7, 6)

#创建元组存储停止位
stopBitsAllInfo = (1, 1.5, 2)

#创建一个串口test对象
ispInstance = isp.Communication("COM1", 115200, 0)

#slotMethod 槽函数

#------------------------------------------------------
#关闭窗口
def closeWindow():
    sys.exit(app.exec_())

#窗口最大化
def windowMaximized():
    global windowMaximinzedFlag
    if windowMaximinzedFlag!=1:
        windowMaximinzedFlag = 1
        MainWindow.showMaximized()
    else:
        windowMaximinzedFlag = 0
        MainWindow.showNormal()

#窗口最小化
def windowminimized():
    MainWindow.showMinimized()

#------------------------------------------------------



#------------------------------------------------------串口信息
def updateChoosenPortInfo():
    #print("-"*20)
    #更新选中串口号
    portNo = ui.comboBox_port.currentText()
    comPortInfo["portNo"] = portNo
    #print(comPortInfo["portNo"])
    #更新波特率
    baudNo = ui.comboBox_Baud.currentIndex()
    comPortInfo["Baud"] = baudAllInfo[baudNo]
    #print(comPortInfo["Baud"])
    # 更新数据位
    dataBitNo = ui.comboBox_dataBit.currentIndex()
    comPortInfo["dataBit"] = dataBitsAllInfo[dataBitNo]
    #print(comPortInfo["dataBit"])
    # 更新校验位
    parityBitNo = ui.comboBox_parityBit.currentIndex()
    comPortInfo["parityBit"] = parityBitAllInfo[parityBitNo]
    #print(comPortInfo["parityBit"])
    # 更新停止位
    stopBitNo = ui.comboBox_stopBit.currentIndex()
    comPortInfo["stopBit"] = stopBitsAllInfo[stopBitNo]
    #print(comPortInfo["stopBit"])

#清除发送串口数据
def clearSendMessage():
    ui.textEdit_sendMessage.clear()

#打开串口
def openOrClosePort():
    global portStateFlag
    try:
        if portStateFlag == 0:
            isopen = openPort()
            if isopen:
                portStateFlag = 1
            else:
                portStateFlag = 0
            print("openOrClosePort---openPort")
        else:
            closePort()
            portStateFlag = 0
            print("openOrClosePort---closePort")
    except Exception as e:
        print("---异常---：", e)

#另一个文件
#接收信息类，使用线程接收
class receievMessage(QThread):
    def run(self):
        global msgNumber
        while True:
            receivedMsg = ispInstance.receievMsg()
            if len(receivedMsg)!=0:
                #如果数据不为空，那么添加到tableview里
                # 时间
                nowtime = time.strftime('%H：%M：%S', time.localtime(time.time()))
                item = QStandardItem(nowtime)
                model.setItem(msgNumber, 0, item)
                # 串口号
                item = QStandardItem(comboBoxPortNoToportNo[ui.comboBox_port.currentIndex()])
                model.setItem(msgNumber, 1, item)
                # 读/写
                item = QStandardItem('read')
                model.setItem(msgNumber, 2, item)
                # 长度
                item = QStandardItem(str(len(receivedMsg)))
                model.setItem(msgNumber, 3, item)
                # hex

                # ascii
                item = QStandardItem(receivedMsg.decode('utf-8'))
                model.setItem(msgNumber, 5, item)

                ui.tableView.setModel(model)
                msgNumber = msgNumber + 1
                print(receivedMsg)

recMsgInstance = receievMessage()


#打开串口
def openPort():
    print("openPort")
    isOpen = ispInstance.Open_Engine(comboBoxPortNoToportNo[ui.comboBox_port.currentIndex()],comPortInfo["Baud"],0)
    if isOpen:
        ui.label_status.setText("状态：串口开启")
        ui.label_status.setStyleSheet("color:green")
        ui.pushButton_openPort.setText("关闭串口")
        recMsgInstance.start()
        return True
    else:
        QMessageBox.warning(MainWindow, "警告", "串口打开失败！提示：串口可能已经被占用。", QMessageBox.Yes)
        return False

#关闭串口
def closePort():
    try:
        recMsgInstance.terminate()
        while True:
            if recMsgInstance.isFinished():
                print("线程已关闭")
                ispInstance.Close_Engine()
                break
            else:
                print("线程未关闭")
        ui.label_status.setText("状态：串口关闭")
        ui.label_status.setStyleSheet("color:red")
        ui.pushButton_openPort.setText("打开串口")
        print("closePort")
    except Exception as e:
        print("---关闭异常---：", e)

def chooseHexadecimalFormat():
    flag = ui.checkBox_hexadecimal.isChecked()
    if flag:
        ispInstance.hexadecimalFlag = 1
    else:
        ispInstance.hexadecimalFlag = 0



hexORasciiMessage = []
#发送串口数据
def slot_sendMessage():
    global msgNumber,addCheckFlag
    message = ui.textEdit_sendMessage.toPlainText()
    global hexORasciiMessage
    if addCheckFlag == False:
        #没有添加校验码
        #hex
        if ui.checkBox_hexadecimal.isChecked() == 1:
            #先检查非法字符
            islegal = organizeMessage.hexIsLegal(message)
            if islegal == False :
                QMessageBox.warning(MainWindow, "警告", "发送失败！提示：您的发送信息中含有非十六进制字符。", QMessageBox.Yes)
                return
            #字符合法，组织数据
            finalmsg,org_msg = organizeMessage.organizeMsg(message)
            #界面显示的hex信息
            text_list = re.findall(".{2}", org_msg)
            showhexmessage = " ".join(text_list)
            #最终hex数据进入发送数据缓存
            hexORasciiMessage.append(finalmsg)
        #str
        else:
            # 最终str数据进入发送数据缓存
            hexORasciiMessage.append(message)
    else:
        #添加校验码
        pass
    #------------------------------界面显示发送信息-------------------------
    # 时间
    nowtime = time.strftime('%H：%M：%S', time.localtime(time.time()))
    item = QStandardItem(nowtime)
    model.setItem(msgNumber, 0, item)
    # 串口号
    item = QStandardItem(comboBoxPortNoToportNo[ui.comboBox_port.currentIndex()])
    model.setItem(msgNumber, 1, item)
    #读/写
    item = QStandardItem('write')
    model.setItem(msgNumber, 2, item)
    # 长度
    item = QStandardItem(str(len(hexORasciiMessage[0])))
    model.setItem(msgNumber, 3, item)
    #如果是str信息，那么显示
    if ui.checkBox_hexadecimal.isChecked() == 0:
        if addCheckFlag == False:
            # str显示
            item = QStandardItem(hexORasciiMessage[0])
            model.setItem(msgNumber, 5, item)
            # str转hex显示
            h = hexlify(hexORasciiMessage[0].encode())
            newh = ''
            for i in range(0,len(h),2):
                newh+=h[i:i+2].decode('utf-8')
                newh+=' '
            item = QStandardItem(str(newh))
            model.setItem(msgNumber, 4, item)
        else:
            # str显示
            item = QStandardItem(hexORasciiMessage[0])
            model.setItem(msgNumber, 5, item)
            # str转hex显示
            h = hexlify(hexORasciiMessage[0].encode()+hexORasciiMessage[1])
            newh = ''
            for i in range(0, len(h), 2):
                newh += h[i:i + 2].decode('utf-8')
                newh += ' '
            item = QStandardItem(str(newh))
            model.setItem(msgNumber, 4, item)
    #如果是hex信息，那么显示
    else:
        if addCheckFlag == False:
            # hex显示
            textMsg = ui.textEdit_sendMessage.toPlainText()
            item = QStandardItem(textMsg)
            model.setItem(msgNumber, 4, item)
            # hex转ascii显示
            str_data = hexORasciiMessage[0].decode('utf-8')
            print(str_data)
            print(type(str_data))
            item = QStandardItem(str_data)
            model.setItem(msgNumber, 5, item)
        else:
            # hex显示
            textMsg = ui.textEdit_sendMessage.toPlainText()
            item = QStandardItem(textMsg)
            model.setItem(msgNumber, 4, item)
            # hex转ascii显示
            str_data = hexORasciiMessage[0].decode('utf-8')
            #str_data1 = hexORasciiMessage[1].decode('utf-8')
            item = QStandardItem(str_data)
            model.setItem(msgNumber, 5, item)
    ui.tableView.setModel(model)
    ispInstance.sendMessage(hexORasciiMessage,ispInstance.hexadecimalFlag,addCheckFlag)
    hexORasciiMessage.clear()
    addCheckFlag = False
    msgNumber = msgNumber + 1

def moveToDragPos(movedPosX,movedPosY):
    nowGe = MainWindow.geometry()
    MainWindow.setGeometry(nowGe.x()-movedPosX,nowGe.y()-movedPosY,nowGe.width(),nowGe.height())

def test():
    print("test123-start")

    print("test123-end")


#添加校验码
def addCheck():
    #获取发送数据
    global hexORasciiMessage,addCheckFlag
    addCheckFlag = True
    hexORasciiMessage.clear()
    sendMsg = ui.textEdit_sendMessage.toPlainText()
    if ui.comboBox_check.currentIndex() == 0:
        #CRC32
        crc_func = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)
    elif ui.comboBox_check.currentIndex() == 1:
        #CRC16/MODBUS
        crc_func = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, xorOut=0x0000)
    elif ui.comboBox_check.currentIndex() == 2:
        #CRC8
        crc_func = crcmod.mkCrcFun(0x107, initCrc=0x00, xorOut=0x00)

    if ui.checkBox_hexadecimal.isChecked():
        # 十六进制形式组织信息
        # 先检查非法字符
        islegal = True
        for i in range(len(sendMsg)):
            if organizeMessage.isHex(sendMsg[i]) == 0:
                islegal = False
                break
        if islegal == False:
            hexFlag = 0
            QMessageBox.warning(MainWindow, "警告", "发送失败！提示：您的发送信息中含有非十六进制字符。", QMessageBox.Yes)
        else:
            list_message = sendMsg.split(" ")  # 先按空格分开
            addedmessage = ''
            showhexmessage = ''
            for spmsg in list_message:
                if len(spmsg) % 2 != 0:
                    newspmsg = list(spmsg)
                    newspmsg.insert(len(spmsg) - 1, '0')
                    spmsg = ''.join(newspmsg)
                addedmessage = addedmessage + spmsg

            finalmsg = bytes.fromhex(addedmessage)
            hexORasciiMessage.append(finalmsg)

            #crc_func = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)
            crcdata = hex(crc_func(finalmsg))
            crcdata = crcdata[2:len(crcdata)]
            newcrcdata = unhexlify(crcdata)
            hexORasciiMessage.append(newcrcdata)
            showMsg = sendMsg + ' ' + hex(crc_func(sendMsg.encode()))
            ui.textEdit_sendMessage.setText(showMsg)
    else:
        # 文本形式加校验码
        #crc_func = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)
        hexORasciiMessage.append(sendMsg)
        crcdata = hex(crc_func(sendMsg.encode()))
        crcdata = crcdata[2:len(crcdata)]
        newcrcdata = unhexlify(crcdata)
        hexORasciiMessage.append(newcrcdata)
        showMsg = sendMsg + ' ' + hex(crc_func(sendMsg.encode()))
        ui.textEdit_sendMessage.setText(showMsg)
    '''
    if ui.comboBox_check.currentIndex() == 0:
        # CRC16/MODBUS
        print("CRC16/MODBUS")
        crcMsg = crc16_modbus(sendMsg)
        newMsg = sendMsg+' '+crcMsg
        ui.textEdit_sendMessage.setText(newMsg)
    elif ui.comboBox_check.currentIndex() == 1:
        # CRC32
        print("CRC32")
        crcMsg = crc32(sendMsg)
        newMsg = sendMsg+' '+crcMsg
        ui.textEdit_sendMessage.setText(newMsg)'''

#以CSV文件保存
def saveCsv():

    headers = ['class', 'name', 'sex', 'height', 'year']

    rows = [
        [1, 'xiaoming', 'male', 168, 23],
        [1, 'xiaohong', 'female', 162, 22],
        [2, 'xiaozhang', 'female', 163, 21],
        [2, 'xiaoli', 'male', 158, 21]
    ]

    with open('test.csv', 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(rows)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    #槽函数
    ui.pushButton_close.clicked.connect(closeWindow)
    ui.pushButton_windowMaximized.clicked.connect(windowMaximized)
    ui.pushButton_windowminimized.clicked.connect(windowminimized)
    ui.pushButton_addCheck.clicked.connect(addCheck)

    # 将事件与槽建立关联
    ui.widget_drag.getMovePosSignal.connect(moveToDragPos)
    txtfile = open('./base.qss')
    qss = txtfile.read()
    MainWindow.setStyleSheet(qss)

    model = QStandardItemModel(20, 6)
    # 设置水平方向四个头标签文本内容
    model.setHorizontalHeaderLabels(['时间','串口号','读/写','长度','HEX','ASCII'])
    ui.tableView.setModel(model)
    ui.tableView.setColumnWidth(0, 90)#时间
    ui.tableView.setColumnWidth(1, 60)#串口号
    ui.tableView.setColumnWidth(2, 60)#读/写
    ui.tableView.setColumnWidth(3, 40)#长度
    ui.tableView.setColumnWidth(4, 200)#hex
    ui.tableView.setColumnWidth(5, 200)#ascii
    ui.label_git.setOpenExternalLinks(1)
    ui.label_git.setText(
        "<a style='color: green; text-decoration: none' href = https://github.com/TjfCCC123/ComMonitor>点击转至开源网址")
    ui.label_status.setText("状态：串口关闭")
    ui.label_status.setStyleSheet("color:red")

    MainWindow.resize(1228,700)
    #开始检测串口
    list_port = isp.Communication.Print_Used_Com()
    if(len(list_port)>0):
        # 建立信号槽函数连接
        ui.comboBox_port.currentIndexChanged.connect(updateChoosenPortInfo)
        ui.comboBox_Baud.currentIndexChanged.connect(updateChoosenPortInfo)
        ui.pushButton_openPort.clicked.connect(updateChoosenPortInfo)
        ui.pushButton_openPort.clicked.connect(openOrClosePort)
        ui.pushButton_send.clicked.connect(slot_sendMessage)
        ui.checkBox_hexadecimal.stateChanged.connect(chooseHexadecimalFormat)
        countPortNum = 0
        for k in list_port:
            ui.comboBox_port.addItem("")
            comboBoxPortNoToportNo.append(k[0])
            ui.comboBox_port.setItemText(countPortNum, QtCore.QCoreApplication.translate("MainWindow", k[0]+"("+k[1]+")"))
            countPortNum += 1
        updateChoosenPortInfo()
    else:
        print("未检测到串口！")
    test()
    MainWindow.setWindowFlags(Qt.FramelessWindowHint)		#隐藏主窗口边界
    MainWindow.show()
    sys.exit(app.exec_())
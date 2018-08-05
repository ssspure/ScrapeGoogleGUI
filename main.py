from PyQt5.QtWidgets import QWidget
from com.MainUI import *
from com.LogicProcess import *
from PyQt5.QtCore import QThread,pyqtSignal


class RunThread(QThread):
    _singal = pyqtSignal(str)

    scrapeEndPrompt = pyqtSignal()

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.scrapeEndPrompt.connect(self.endPrompt)

    def __del__(self):
        self.wait()

    def run(self):
        runProcess(self, self.ui)
        self.scrapeEndPrompt.emit()


    def endPrompt(self):
        QMessageBox.about(self.ui, '提示', '程序运行结束!!!')
        QApplication.processEvents()


class MainProcess(QWidget, Ui_ScrapeGoogle):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 获取当前程序所在的路径
        self.path = os.path.dirname(os.path.abspath(__file__))

        # 设置界面初始值
        setUIInitialValue(self)

        # 执行程序按钮时间监听
        self.runBtn.clicked.connect(self.start_login)

        # 保存数据
        self.saveDataBtn.clicked.connect(lambda :saveData(self))

        # 打开结果文件夹
        self.openResultFileBtn.clicked.connect(lambda :openResultFolder(self))

    def start_login(self):

        # 输入值Check处理
        result = initialProcess(self)

        if result:
            # 创建线程
            self.thread = RunThread(self)
            # 连接信号
            self.thread._singal.connect(self.stateMessage)
            # 开始线程
            self.thread.start()

    def stateMessage(self, msg):
        # 将回调数据输出到文本框
        self.stateText.append(msg)
        QApplication.processEvents()


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    w = MainProcess()
    w.show()
    sys.exit(app.exec_())
import socket
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

class SendVideoThread(QThread):
    progress_signal = pyqtSignal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.stopSending = False

    def run(self):
        # socket 통신 설정
        host = 'localhost'
        port = 5000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)

        # 수신자에게 영상 전송
        conn, addr = s.accept()
        print('Connected by', addr)

        # 영상 프레임을 읽어서 소켓을 통해
        cap = cv2.VideoCapture(self.filename)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 해상도 정보 전송
        conn.sendall(frame_width.to_bytes(4, byteorder='big'))
        conn.sendall(frame_height.to_bytes(4, byteorder='big'))

        while not self.stopSending:
            ret, frame = cap.read()
            if not ret:
                break
            data = frame.tobytes()
            # RGB를 전송
            conn.sendall(len(data).to_bytes(4, byteorder='big'))
            conn.sendall(data)

        # 소켓 닫기
        conn.close()
        s.close()
        cap.release()

        if self.stopSending:
            self.progress_signal.emit('Video transmission canceled.')
        else:
            self.progress_signal.emit('Video transmission complete.')

    def cancelVideo(self):
        self.stopSending = True

class Sender(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 파일 선택 버튼 생성
        self.fileBtn = QPushButton('Choose File', self)
        self.fileBtn.move(20, 20)
        self.fileBtn.clicked.connect(self.showDialog)

        # 전송 시작 버튼 생성
        self.sendBtn = QPushButton('Send', self)
        self.sendBtn.move(20, 60)
        self.sendBtn.clicked.connect(self.sendVideo)

        # 전송 취소 버튼 생성
        self.cancelBtn = QPushButton('Stop sending', self)
        self.cancelBtn.move(120, 60)
        self.cancelBtn.clicked.connect(self.cancelVideo)
        self.cancelBtn.setEnabled(False)

        # 상태 표시줄 생성
        #self.statusBar = QStatusBar()
        layout = QVBoxLayout()
        #layout.addWidget(self.statusBar)
        layout.addWidget(self.fileBtn)
        layout.addWidget(self.sendBtn)
        layout.addWidget(self.cancelBtn)
        self.setLayout(layout)

        # 윈도우 크기 설정 및 화면에 표시
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('PyVideoComm_sender')
        self.show()

    def showDialog(self):
        # 파일 선택 대화 상자 열기
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose a video file", "", "MP4 Files (*.mp4)", options=options)
        if fileName:
            self.filename = fileName
            #print('Selected File:', self.filename)

    def cancelVideo(self):
        self.sendThread.cancelVideo()

    def sendVideo(self):
        if not hasattr(self, 'filename'):
            # 파일을 선택하지 않았으면 에러 메시지 표시
            QMessageBox.critical(self, 'Error', 'Please select a file to send.')
            return

        self.sendThread = SendVideoThread(self.filename)
        self.sendThread.progress_signal.connect(self.updateStatus)
        self.sendThread.finished.connect(self.sendThread.deleteLater)
        self.sendThread.start()

        self.sendBtn.setEnabled(False)
        self.cancelBtn.setEnabled(True)

    def updateStatus(self, message):
        #self.statusBar.showMessage(message)
        if message in ('Video transmission canceled.', 'Video transmission complete.'):
            self.sendBtn.setEnabled(True)
            self.cancelBtn.setEnabled(False)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    sender = Sender()
    sys.exit(app.exec_())


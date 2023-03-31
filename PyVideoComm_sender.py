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
        # Socket communication
        host = 'localhost'
        port = 5000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)

        # Send video to the receiver
        conn, addr = s.accept()
        print('Connected by', addr)

        # Reads the video(by cv2 instance)
        cap = cv2.VideoCapture(self.filename)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Send height and width information
        conn.sendall(frame_width.to_bytes(4, byteorder='big'))
        conn.sendall(frame_height.to_bytes(4, byteorder='big'))

        while not self.stopSending:
            ret, frame = cap.read()
            if not ret:
                break
            data = frame.tobytes()
            # Send RGB
            conn.sendall(len(data).to_bytes(4, byteorder='big'))
            conn.sendall(data)

        # Close socket
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
        # Choose File button
        self.fileBtn = QPushButton('Choose File', self)
        self.fileBtn.move(20, 20)
        self.fileBtn.clicked.connect(self.showDialog)

        # Send buttion
        self.sendBtn = QPushButton('Send', self)
        self.sendBtn.move(20, 60)
        self.sendBtn.clicked.connect(self.sendVideo)

        # Stop Sending buttion
        self.cancelBtn = QPushButton('Stop Sending', self)
        self.cancelBtn.move(120, 60)
        self.cancelBtn.clicked.connect(self.cancelVideo)
        self.cancelBtn.setEnabled(False)

        #self.statusBar = QStatusBar()
        layout = QVBoxLayout()
        #layout.addWidget(self.statusBar)
        layout.addWidget(self.fileBtn)
        layout.addWidget(self.sendBtn)
        layout.addWidget(self.cancelBtn)
        self.setLayout(layout)

        # windows size setting
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('PyVideoComm_sender')
        self.show()

    def showDialog(self):
        # File select, by UI
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
            # Display a error when a file is not selected.
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


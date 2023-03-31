import socket
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QStatusBar, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

# global variables
filename = 'received.mp4'
frames = []

# socket communication settings
host = 'localhost'
port = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#PyQt5 UI setup
class VideoReceiver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyVideoComm_receiver')
        self.setGeometry(100, 100, 640, 480)

        # label to show received frames
        self.video_label = QLabel(self)
        self.video_label.setGeometry(0, 0, 640, 360)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText('Waiting for Video...')

        # button to start receiving frames
        self.receive_button = QPushButton('Start Receiving', self)
        self.receive_button.setGeometry(250, 400, 140, 30)
        self.receive_button.clicked.connect(self.start_receive)

        # status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('')

    # function to update status bar
    def update_status_bar(self, message):
        self.status_bar.showMessage(message)

    def save_file(self):
        global frames, filename
        save_file_dialog = QFileDialog()
        save_file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        save_file_dialog.setDefaultSuffix('mp4')
        save_file_dialog.setNameFilter('MP4 Files (*.mp4)')
        save_file_dialog.setDirectory('.')
        save_file_dialog.setWindowTitle('Save Video File')
        if save_file_dialog.exec_():
            file_path = save_file_dialog.selectedFiles()[0]
            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                height, width, layers = frames[0].shape
                out = cv2.VideoWriter(file_path, fourcc, 20, (width, height))
                for frame in frames:
                    out.write(frame)
                out.release()
                self.update_status_bar(f'Video saved successfully to {file_path}!')
            except Exception as e:
                self.update_status_bar(f'Error saving video file: {e}')
            finally:
                # reset global variables
                filename = 'received.mp4'
                frames = []
                # reset label text and enable button
                self.video_label.setText('Waiting for Video...')
                self.receive_button.setEnabled(True)

    # function to receive frames from socket
    def receive_frames(self):
        global frames
        frames = []  # reset frames list
        #sock.connect((host, port))  # connect to the sender
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create new socket object
        sock.connect((host, port))  # connect to the sender

        # 해상도 정보 받기
        frame_width = int.from_bytes(sock.recv(4), byteorder='big')
        frame_height = int.from_bytes(sock.recv(4), byteorder='big')

        while True:
            # receive data length
            data_len_bytes = sock.recv(4)
            if not data_len_bytes:
                break
            data_len = int.from_bytes(data_len_bytes, byteorder='big')
            # receive image data
            data = b''
            while len(data) < data_len:
                packet = sock.recv(data_len - len(data))
                if not packet:
                    break
                data += packet
            if len(data) != data_len:
                break
            # check if data was actually received
            if len(data) == data_len:
                # convert byte stream to image
                #frame = np.frombuffer(data, dtype=np.uint8).reshape((540, 960, 3))
                frame = np.frombuffer(data, dtype=np.uint8).reshape((frame_height, frame_width, 3))
                # append frame to frames list
                frames.append(frame)
                # update status bar
                self.update_status_bar(f'Received {len(frames)} frames...')
                # update video label
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.video_label.setPixmap(
                    pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                QApplication.processEvents()  # refresh video label
            else:
                # handle data not received
                self.update_status_bar(
                    f'Error receiving data: expected {data_len} bytes, but received {len(data)} bytes')
                break
        # close socket
        sock.close()
        # save video file
        self.save_file()
        # reset frames list
        frames = []

    # # function to start receiving frames
    # def start_receive(self):
    #     self.update_status_bar('Receiving Video...')
    #     self.receive_frames()
    #

    # function to start receiving frames
    def start_receive(self):
        self.receive_button.setEnabled(False)  # disable button to prevent multiple clicks
        self.update_status_bar('Receiving Video...')
        try:
            self.receive_frames()
            self.update_status_bar('Video received and saved successfully!')
        except ConnectionRefusedError:
            self.update_status_bar('Connection refused. Make sure the sender is running.')
        finally:
            self.receive_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication([])
    window = VideoReceiver()
    window.show()
    app.exec_()

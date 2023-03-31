# Python Video Comm (PyVC)
![Python Video Comm image](example.gif "Python Video Comm on the PC")

PyVideoComm is basic start code that makes sending and receiving video in two programs very easy by Python.

## Overview
PyVideoComm consists of two files: 
PyVideoComm_sender.py and PyVideoComm_receiver.py.

Each file corresponds to a transmitter/receiver and provides a basic file selection/saving UI. 
The transmitter allows you to select files to send with a UI.
And the receiver allows you to save files to receive with a UI.

## Additional features
(1) PyVideoComm_sender.py has a "Stop sending" button, so you can stop the transmission of video in the midway.<br>
(2) PyVideoComm_sender.py and PyVideoComm_receiver.py can send and receive repeatedly(unlimitted).<br>
(3) PyVideoComm_receiver.py has a display window that shows the received video in real-time.

## Create your own executables.
You may use some Pyinstaller or etc to create executable exe files for the video sender and video receiver.
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
import socket
import cv2
from PyQt5.QtGui import QImage, QPixmap

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente")
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.label = QLabel("Conectando al servidor...", self)
        self.label.setGeometry(50, 50, 400, 50)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; color: #333; background-color: #fff; border: 1px solid #ccc;")

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(0, 0, 0, 0)
        self.video_label.setStyleSheet("background-color: #fff; border: 1px solid #ccc;")

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.detected_label = QLabel("No se detecta persona", self)
        self.detected_label.setGeometry(50, 150, 400, 20)
        self.detected_label.setAlignment(Qt.AlignCenter)
        self.detected_label.setStyleSheet("font-size: 16px; color: #333; background-color: #fff; border: 1px solid #ccc;")

        self.cap = cv2.VideoCapture(0)
        self.timer_camera = QTimer(self)
        self.timer_camera.timeout.connect(self.detect_face)
        self.timer_camera.start(1000)

        self.timer_no_face = QTimer(self)
        self.timer_no_face.timeout.connect(self.send_notification)
        self.no_face_duration = 0

        self.connect_to_server()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('192.168.80.16', 8888))
            self.label.setText("Conectado al servidor")
        except socket.error as e:
            self.label.setText("Error al conectar al servidor: " + str(e))

    def detect_face(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                self.detected_label.setText("Persona detectada")
                self.no_face_duration = 0
                self.timer_no_face.stop()
            else:
                self.no_face_duration += 1
                if self.no_face_duration >= 7:
                    self.send_notification()
                else:
                    self.detected_label.setText("No se detecta persona")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.video_label.setPixmap(pixmap)

    def send_notification(self):
        try:
            self.client_socket.send(b'No se detecta persona')
            self.timer_no_face.stop()
        except socket.error as e:
            print("Error al enviar notificación al servidor:", e)

    def closeEvent(self, event):
        self.cap.release()
        self.client_socket.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_window = ClientWindow()
    client_window.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QLabel, QMessageBox
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
import socket
import threading
import datetime

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servidor")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.connected_users_label = QLabel("Usuarios Conectados:", self)
        self.connected_users_label.setGeometry(50, 50, 300, 20)
        self.connected_users_label.setAlignment(Qt.AlignCenter)
        self.connected_users_label.setStyleSheet("font-size: 16px; color: #333;")

        self.users_list_widget = QListWidget(self)
        self.users_list_widget.setGeometry(50, 80, 300, 150)
        self.users_list_widget.setStyleSheet("background-color: #fff; border: 1px solid #ccc;")
        self.users_list_widget.itemDoubleClicked.connect(self.show_user_info)

        self.users = {}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('192.168.80.16', 8888))
        self.server_socket.listen(5)

        self.thread = threading.Thread(target=self.accept_connections)
        self.thread.start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            username = client_address[0] + ":" + str(client_address[1])
            self.users[username] = {'socket': client_socket, 'item': None, 'connect_time': datetime.datetime.now(), 'notification_count': 0}
            self.update_users_list()
            threading.Thread(target=self.handle_client, args=(username,)).start()

    def handle_client(self, username):
        while True:
            try:
                data = self.users[username]['socket'].recv(1024)
                if data:
                    message = data.decode('utf-8')
                    print("Mensaje del cliente", username + ":", message)
                    if message == 'No se detecta persona':
                        self.users[username]['item'].setBackground(QColor('red'))
                        self.users[username]['notification_count'] += 1
            except socket.error:
                del self.users[username]
                self.update_users_list()
                break

    def update_users_list(self):
        self.users_list_widget.clear()
        for username, user_info in self.users.items():
            item = QListWidgetItem(username)
            user_info['item'] = item
            self.users_list_widget.addItem(item)

    def show_user_info(self, item):
        username = item.text()
        user_info = self.users[username]
        connect_time = user_info['connect_time'].strftime("%Y-%m-%d %H:%M:%S")
        notification_count = user_info['notification_count']
        packets = divmod(notification_count, 60)
        message = f"Usuario: {username}\nHora de conexión: {connect_time}\nPaquetes de notificaciones (completos, incompletos): {packets}"
        QMessageBox.information(self, "Información de Usuario", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_window = ServerWindow()
    server_window.show()
    sys.exit(app.exec_())

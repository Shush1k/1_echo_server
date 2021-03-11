import socket
import logging
from threading import Thread
import sys
import pickle
from validation import ip_validation, port_validation
from getpass import getpass
from time import sleep

IP_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 9090
logging.basicConfig(filename='log/client.log',
                    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s", level=logging.INFO)


class Client:
    """
    Клиент
    """

    def __init__(self, server_ip, port, status=None):
        """
        @param server_ip - localhost
        @param port - порт сервера
        @param status - текущее состояние программы
        """
        self.server_ip = server_ip
        self.port = port
        self.status = status
        self.server_connection()
        self.start()

    def server_connection(self):
        """
        Соединение пользователя с сервером
        """
        sock = socket.socket()
        sock.setblocking(1)
        sock.connect((self.server_ip, self.port))
        self.sock = sock
        logging.info(
            f"Пользователь подключился к серверу ('{self.server_ip}', {self.port})")

    def start(self):
        """
        Проверяем какой статус приложения
        """
        Thread(target=self.recv).start()
        while self.status != 'finish':
            if self.status:
                if self.status == "auth":
                    self.auth()
                elif self.status == "passwd":
                    self.sendPasswd()
                    logging.info("Пользователь авторизовался")
                elif self.status == "success":
                    self.success()
                else:
                    msg = input("==> ")
                    if msg == "exit":
                        self.status = "finish"
                        logging.info("Пользователь отключился")
                        break
                    sendM = pickle.dumps(["message", msg])
                    self.sock.send(sendM)

        self.sock.close()

    def sendPasswd(self):
        """
        Отправка пароля на сервер
        """
        passwd = getpass(self.data)
        self.sock.send(pickle.dumps(["passwd", passwd]))
        # если убрать sleep ничего работать не будет!!!
        sleep(1.5)

    def auth(self):
        """
        Отправка имени на сервер
        """
        print("Введите имя:")
        name = input()
        self.sock.send(pickle.dumps(["auth", name]))
        # если убрать sleep ничего работать не будет!!!
        sleep(1.5)

    def success(self):
        """
        Вывод приветственного сообщения
        """
        print(self.data)
        self.status = "ready"

    def recv(self):
        """
        Функция получения данных
        Работает в отдельном потоке
        """
        while True:
            try:
                self.data = self.sock.recv(1024)
                if not self.data:
                    sys.exit(0)
                status = pickle.loads(self.data)[0]
                self.status = status
                if self.status == "message":
                    print(pickle.loads(self.data)[1])
                else:
                    self.data = pickle.loads(self.data)[1]
            except OSError:
                break


def main():
    """
    Ввод порта и ip сервера, валидация данных
    """
    user_port = input("Введите порт:")
    if not port_validation(user_port):
        user_port = PORT_DEFAULT
        print(f"Установили порт {user_port} по умолчанию")

    user_ip = input("Введите ip сервера:")
    if not ip_validation(user_ip):
        user_ip = IP_DEFAULT
        print(f"Установили ip-адресс {user_ip} по умолчанию")

    Client(user_ip, int(user_port))


if __name__ == "__main__":
    main()

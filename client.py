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

    def __init__(self, server_ip, port, status = None):
        """
        Args:
            server_ip (str): localhost/ip-адресс сервера
            port (int): порт сервера
            status (str): текущее состояние программы. Defaults to None.
        """
        self.server_ip = server_ip
        self.port = port
        self.status = status
        self.server_connection()
        self.polling()

    def server_connection(self):
        """
        Соединение пользователя с сервером
        """
        sock = socket.socket()
        sock.setblocking(1)
        try:
            sock.connect((self.server_ip, self.port))
        except ConnectionRefusedError:
            print(f"Не удалось присоединиться к серверу {self.server_ip, self.port}")
            sys.exit(0)
        self.sock = sock
        logging.info(
            f"Установлено соединение {self.sock.getsockname()} с сервером ('{self.server_ip}', {self.port})")

    def polling(self):
        """
        Проверяем какой статус приложения
        """
        Thread(target=self.recv).start()
        print("Используйте 'exit', чтобы разорвать соединение")
        while self.status != 'finish':
            if self.status:
                if self.status == "auth":
                    self.auth()
                    logging.info(f"Пользователь {self.sock.getsockname()} зарегистрировался")
                elif self.status == "passwd":
                    self.sendPasswd()
                elif self.status == "success":
                    self.success()
                else:
                    msg = input(f"{self.username}> ")
                    if msg != "":
                        if msg == "exit":
                            self.status = "finish"
                            logging.info(f"Разрыв соединения {self.sock.getsockname()} с сервером")
                            break
                        # Отправляем сообщение и имя клиента
                        sendM = pickle.dumps(["message", msg, self.username])
                        self.sock.send(sendM)
                        logging.info(f"Отправка данных от {self.sock.getsockname()} на сервер: {msg}")
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
        self.username = input()
        self.sock.send(pickle.dumps(["auth", self.username]))
        # если убрать sleep ничего работать не будет!!!
        sleep(1.5)

    def success(self):
        """
        Вывод приветственного сообщения
        """
        print(self.data)
        self.status = "ready"
        self.username = self.data.split(" ")[1]
        logging.info(f"Клиент {self.sock.getsockname()} прошел авторизацию")

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
                    print(f"\n{pickle.loads(self.data)[2]} -->", pickle.loads(self.data)[1])
                    # можно проверить с помощью двух присоединений к серверу
                    logging.info(f"Клиент {self.sock.getsockname()} принял данные от сервера: {pickle.loads(self.data)[1]}")
                else:
                    self.data = pickle.loads(self.data)[1]
            except OSError:
                break


def main():
    """
    Ввод порта и ip сервера, валидация данных
    """
    user_port = input("Введите порт (enter для значения по умолчанию):")
    if not port_validation(user_port):
        user_port = PORT_DEFAULT
        print(f"Установили порт {user_port} по умолчанию")

    user_ip = input("Введите ip сервера (enter для значения по умолчанию):")
    if not ip_validation(user_ip):
        user_ip = IP_DEFAULT
        print(f"Установили ip-адресс {user_ip} по умолчанию")

    Client(user_ip, int(user_port))


if __name__ == "__main__":
    main()

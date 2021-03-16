import socket
from datetime import datetime
import hashlib
import json
import pickle
from threading import Thread
import sys
import logging
from validation import is_free_port, port_validation


PORT_DEFAULT = 9090
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
                    handlers=[logging.FileHandler("log/server.log"), logging.StreamHandler()], level=logging.INFO)


class Server():
    """
    Сервер
    """

    def __init__(self, port, clients=[], status=None):
        """
        Args:
            port (int): порт сервера
            clients (list): список подключенных клиентов. Defaults to [].
            status (str): текущее состояние программы. Defaults to None.
        """
        # users - файл с данными
        self.users = "users.json"
        self.clients = clients
        self.server_port = port
        self.all_Users = []
        self.status = status
        self.server_boot()

    def readJSON(self):
        """
        Читаем файл
        
        Returns:
            list: список пользователей
        """
        with open(self.users, 'r') as f:
            users = json.load(f)
        return users

    def writeJSON(self):
        """
        Запись всех пользователей в файл
        """
        with open(self.users, 'w') as f:
            json.dump(self.all_Users, f, indent=4)

    def server_boot(self):
        """
        Запуск сервера
        """
        sock = socket.socket()
        sock.bind(('', self.server_port))
        sock.listen(5)
        self.sock = sock
        logging.info(f"Сервер стартанул, слушаем порт {self.server_port}")
        while True:
            conn, addr = self.sock.accept()
            Thread(target=self.listenToClient, args=(conn, addr)).start()
            logging.info(f"Подключение клиента {addr}")
            self.clients.append(conn)

    def broadcast(self, msg, conn, address, username):
        """
        Отправка данных клиентам\n
        Отправляем сообщение и имя пользователя с номером соединения

        Args:
            msg (str): сообщение
            conn (socket): сокет с данными клиента
            address (tuple): кортеж ip-адреса и номера соединения
            username (str): имя клиента
        """
        username += "_"+str(address[1])
        for sock in self.clients:
            if sock != conn:
                data = pickle.dumps(["message", msg, username])
                sock.send(data)
                logging.info(f"Отправка данных клиенту {sock.getsockname()}: {msg}")
            

    def checkPassword(self, passwd, userkey):
        """
        Проверяем пароль из файла и введенный пользователем

        Args:
            passwd (str): пароль введенный пользователем
            userkey (str): хранимый пароль пользователя

        Returns:
            boolean: True/False
        """
        key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
        return key == userkey

    def generateHash(self, passwd):
        """
        Генерация пароля\n
        Args:
            passwd (str): пароль

        Returns:
            str: хэш пароль
        """
        key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
        return key

    def listenToClient(self, conn, address):
        """
        Слушаем клиента, если данные есть отправляем их клиентам.\n
        Иначе закрываем соединение клиента.

        Args:
            conn (socket): сокет с данными клиента
            address (tuple): кортеж ip-адреса и номера соединения
        """
        self.authorization(address, conn)
        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                conn.close()
                self.clients.remove(conn)
                logging.info(f"Отключение клиента {address}")
                break

            if data:
                status, data, username = pickle.loads(data)
                logging.info(f"Прием данных от клиента '{username}_{address[1]}': {data}")
                if status == "message":
                    self.broadcast(data, conn, address, username)
                    
            else:
                # Закрываем соединение
                conn.close()
                self.clients.remove(conn)
                logging.info(f"Отключение клиента {address}")
                break

    def authorization(self, addr, conn):
        """
        Авторизация, считывание информации из файла

        Args:
            addr (tuple): кортеж ip-адреса и номера соединения
            conn (socket): сокет с данными клиента
        """
        # Проверка есть ли в файле данные
        try:
            self.all_Users = self.readJSON()
        except json.decoder.JSONDecodeError:
            self.registration(addr, conn)

        user_flag = False
        for user in self.all_Users:
            if addr[0] in user:
                for k, v in user.items():
                    if k == addr[0]:
                        name = v['name']
                        password = v['password']
                        conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
                        passwd = pickle.loads(conn.recv(1024))[1]
                        conn.send(pickle.dumps(["success", f"Здравствуйте, {name}"])) if self.checkPassword(
                            passwd, password) else self.authorization(addr, conn)
                        user_flag = True
        # Если пользователь не найден в файле
        if not user_flag:
            self.registration(addr, conn)
        

    def registration(self, addr, conn):
        """
        Регистрация, запись данных в файл, обновление списка клиентов

        Args:
            addr (tuple): кортеж ip-адреса и номера соединения
            conn (socket): сокет с данными клиента
        """
        conn.send(pickle.dumps(
            ["auth", ""]))
        name = pickle.loads(conn.recv(1024))[1]
        conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
        passwd = self.generateHash(pickle.loads(conn.recv(1024))[1])
        conn.send(pickle.dumps(["success", f"Приветствую, {name}"]))
        self.all_Users.append({addr[0]: {'name': name, 'password': passwd}})
        # Запись в файл при регистрации пользователя
        self.writeJSON()
        self.all_Users = self.readJSON()




def main():
    # Подбор порта
    server_port = PORT_DEFAULT
    if not port_validation(PORT_DEFAULT, True):
        if not is_free_port(PORT_DEFAULT):
            logging.info(f"Порт по умолчанию {PORT_DEFAULT} занят")
            free_port = False
            # перебор порта
            while not free_port:
                server_port += 1
                free_port = is_free_port(server_port)
    try:
        Server(server_port)
    except KeyboardInterrupt:
        logging.info(f"Остановка сервера")

if __name__ == "__main__":
    main()

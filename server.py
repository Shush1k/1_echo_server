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
# TODO Server
# log Подключение клиента добавить имя пользователя и conn_id
# 

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

        self.status = status
        self.server_boot()

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
        Отправка данных клиентам
        Отправляем сообщение и имя пользователя с номером соединения

        Args:
            msg (str): сообщение
            conn: соединение
            address: адрес клиента
        """
        username += "_"+str(address[1])
        for sock in self.clients:
            if sock != conn:
                data = pickle.dumps(["message", msg, username])
                sock.send(data)
                logging.info(f"Отправка данных клиенту {sock.getsockname()}: {msg}")
            

    def checkPassword(self, passwd, userkey):
        """
        Args:
            passwd (str): пароль введенный пользователем
            userkey (str): хранимый пароль пользователя

        Returns:
            str: хэш пароль
        """
        key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
        return key == userkey

    def generateHash(self, passwd):
        """
        Генерация пароля
        """
        key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
        return key

    def listenToClient(self, conn, address):
        """
        Слушаем клиента
        """
        self.checkUser(address, conn)
        while True:
            data = conn.recv(1024)
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

    def checkUser(self, addr, conn):
        """
        Проверка данных клиента
        """
        try:
            open(self.users).close()
        except FileNotFoundError:
            open(self.users, 'a').close()
            
        with open(self.users, "r") as f:
            try:
                # Авторизация, считывание информации из файла
                users = json.load(f)
                name = users[str(addr[0])]['name']
                conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
                passwd = pickle.loads(conn.recv(1024))[1]
                conn.send(pickle.dumps(["success", f"Здравствуйте, {name}"])) if self.checkPassword(
                    passwd, users[str(addr[0])]['password']) else self.checkUser(addr, conn)

            except:
                # Регистрация и запись данных в файл
                conn.send(pickle.dumps(
                    ["auth", ""]))
                name = pickle.loads(conn.recv(1024))[1]
                conn.send(pickle.dumps(["passwd", "Введите свой пароль: "]))
                passwd = self.generateHash(pickle.loads(conn.recv(1024))[1])
                conn.send(pickle.dumps(["success", f"Приветствую, {name}"]))
                # TODO users.json если ip-адресов больше двух все ломается
                # Придумать как обновлять файл json 
                # Если файл уже существует то добавить запись/перезаписывать его каждый раз?
                with open(self.users, "a", encoding="utf-8") as f:
                    json.dump({addr[0]: {'name': name, 'password': passwd}}, f, indent=4)


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

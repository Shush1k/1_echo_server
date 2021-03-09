import socket
import logging
from validation import port_validation

PORT_DEFAULT = 9090
logging.basicConfig(filename='server.log',
                    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s", level=logging.INFO)


class Server:
    def __init__(self, server_port):
        sock = socket.socket()
        sock.bind(('', server_port))
        print(f"Слушаем порт: {server_port}")
        sock.listen(1)
        self.sock = sock
        logging.info(f"Сервер стартанул, слушаем порт {server_port}")
        while True:
            conn, addr = self.sock.accept()
            self.new_connection(conn, addr)

    def new_connection(self, conn, addr):
        """
        Обработчик нового соединения
        """
        logging.info(f"Новое соединение {addr}")
        msg = ""

        while True:
            # Получаем данные
            data = conn.recv(1024)

            # Если нет данных, то больше ничего не ждем от клиента
            if not data:
                break

            msg += data.decode()
            conn.send(data)

            data_str = str(data, "utf-8")
            logging.info(f"Собщение клиента: \"{data_str}\"")


def main():
    server_port = PORT_DEFAULT
    # Подбор порта
    while True:
        try:
            Server(server_port)
            break
        except:
            server_port += 1


if __name__ == "__main__":
    main()

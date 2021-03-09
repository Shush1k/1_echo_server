import socket
from validation import ip_validation, port_validation

IP_DEFAULT = "localhost"
PORT_DEFAULT = 9090

class Client:
    def __init__(self, server_ip, port):
        sock = socket.socket()
        sock.setblocking(1)
        sock.connect((server_ip, port))
        self.sock = sock
        #Работа с данными, поступающими от пользователя
        self.user_processing()
        #Закрываем сокет
        self.sock.close()
        
    def user_processing(self):

        while True:
            msg = input("==> ")
            if msg == "exit": 
                break
            elif msg == "":
                msg = "-"
        
            #Отправляем сообщение клиенту
            self.sock.send(msg.encode())
            #Получаем ответ
            data = self.sock.recv(1024)

            print(f"Ответ сервера: {data.decode()}")

def main():
    user_port = input("Введите порт:")
    if not port_validation(user_port):
        user_port = PORT_DEFAULT
        print(f"Установили порт {user_port} по умолчанию")

    user_ip = input("Введите ip сервера:")
    if not ip_validation(user_ip):
        user_ip = IP_DEFAULT
        print(f"Установили ip {user_ip} по умолчанию")

    Client(user_ip, int(user_port))


if __name__ == "__main__":
	main()
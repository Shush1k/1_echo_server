import socket

SERVER_IP = "localhost"
PORT_NUMBER = 9090

class Client:
    def __init__(self):
        sock = socket.socket()
        sock.setblocking(1)
        sock.connect((SERVER_IP, PORT_NUMBER))
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


if __name__ == "__main__":
	client = Client()
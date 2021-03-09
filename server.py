import socket
from validation import port_validation

PORT_DEFAULT = 9090

class Server:
	def __init__(self):
		sock = socket.socket()
		sock.bind(('', PORT_DEFAULT))
		sock.listen(1)
		self.sock = sock
		print(f"Сервер стартанул, слушаем порт {PORT_DEFAULT}")
		while True:
			conn, addr = self.sock.accept()
			self.new_connection(conn, addr)
	
	def new_connection(self, conn, addr):
		"""
		Обработчик нового соединения
		"""
		print(f"Новое соединение {addr}")
		msg = ""

		while True:
			#Получаем данные
			data = conn.recv(1024)
			
			#Если нет данных, то больше ничего не ждем от клиента
			if not data:
				break

			msg += data.decode()
			conn.send(data)

			data_str = str(data, "utf-8")
			print(f"Собщение клиента: \"{data_str}\"")

if __name__ == "__main__":
	server = Server()
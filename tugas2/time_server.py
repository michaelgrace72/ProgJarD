from socket import *
import socket
import threading
import logging
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"Thread started for {self.address}")
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()
                logging.warning(f"Received from {self.address}: {repr(message)}")

                if message.upper() == "QUIT":
                    break
                elif message.upper() == "TIME":
                    now = datetime.now()
                    time_str = now.strftime("%H:%M:%S")
                    response = f"JAM {time_str}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                else:
                    # Bisa abaikan atau kirim pesan error (opsional)
                    pass
        except Exception as e:
            logging.warning(f"Error with {self.address}: {e}")
        finally:
            self.connection.close()
            logging.warning(f"Connection closed for {self.address}")

class TimeServer(threading.Thread):
    def __init__(self):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.server_socket.bind(('0.0.0.0', 45000))
        self.server_socket.listen(5)
        logging.warning("Time Server running on port 45000...")

        while True:
            client_conn, client_addr = self.server_socket.accept()
            logging.warning(f"Connection from {client_addr}")
            client_thread = ProcessTheClient(client_conn, client_addr)
            client_thread.start()
            self.clients.append(client_thread)

def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
    server = TimeServer()
    server.start()

if __name__ == "__main__":
    main()


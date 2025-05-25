import socket
import threading
import logging
import time
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def handle_client(self):
        buffer = ""
        while True:
            data = self.connection.recv(1024)
            if data:
                buffer += data.decode()
                while "\r\n\r\n" in buffer:
                    idx = buffer.index("\r\n\r\n")
                    command = buffer[:idx]
                    buffer = buffer[idx+4:]
                    hasil = fp.proses_string(command)
                    hasil = hasil + "\r\n\r\n"
                    self.connection.sendall(hasil.encode())
            else:
                break
        self.connection.close()

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=6667, max_workers=50):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.running = True
        threading.Thread.__init__(self)

    def stop(self):
        self.running = False
        self.my_socket.close()
        self.thread_pool.shutdown(wait=True)

    def run(self):
        logging.warning(f"Thread-based server running on {self.ipinfo} with {self.thread_pool._max_workers} workers")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(100)
        try:
            while self.running:
                try:
                    connection, client_address = self.my_socket.accept()
                    logging.warning(f"Connection from {client_address}")
                    handler = ProcessTheClient(connection, client_address)
                    self.thread_pool.submit(handler.handle_client)
                except socket.error:
                    if self.running:
                        raise
                    break
        except KeyboardInterrupt:
            logging.info("Shutting down server...")
        finally:
            self.stop()

def main():
    parser = argparse.ArgumentParser(description='Thread-based file server')
    parser.add_argument('--workers', type=int, default=50, help='Number of worker threads')
    parser.add_argument('--port', type=int, default=6667, help='Port to listen on')
    args = parser.parse_args()
    svr = Server(ipaddress='0.0.0.0', port=args.port, max_workers=args.workers)
    svr.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        svr.stop()
        svr.join()

if __name__ == "__main__":
    main()

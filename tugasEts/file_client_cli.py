import socket
import json
import base64
import logging

server_address=('172.16.16.101',6667)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        # Tambahkan delimiter di akhir perintah
        sock.sendall((command_str + "\r\n\r\n").encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            data = sock.recv(256*1024*1024)  # Menerima data dalam ukuran yang lebih besar
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received.split("\r\n\r\n")[0])
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filename=""):
    try:
        with open(filename, 'rb') as f:
            filedata = f.read()
        filedata_b64 = base64.b64encode(filedata).decode()
        command_str = f"UPLOAD {filename} {filedata_b64}"
        hasil = send_command(command_str)
        if hasil['status'] == 'OK':
            print(f"Upload {filename} berhasil")
            return True
        else:
            print("Gagal upload:", hasil['data'])
            return False
    except Exception as e:
        print("Gagal upload:", str(e))
        return False

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print(f"File {filename} berhasil dihapus")
        return True
    else:
        print("Gagal hapus:", hasil['data'])
        return False


if __name__=='__main__':
    server_address=('172.16.16.101',6667)
    remote_list()
    remote_upload('file-example_PDF_500_kB.pdf')
    remote_list()
    remote_get('donalbebek.jpg')
    remote_list()
    remote_delete('donalbebek.jpg')
    remote_list()



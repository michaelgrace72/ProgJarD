# Time Server TCP

Program ini adalah server waktu sederhana berbasis TCP yang dapat menangani beberapa klien secara bersamaan menggunakan multithreading.

## Fitur

- Mendengarkan pada port 45000
- Protokol TCP
- Mendukung koneksi dari banyak klien secara bersamaan
- Merespons permintaan waktu dengan format `JAM hh:mm:ss`
- Koneksi dapat diakhiri dengan perintah `QUIT`

## Kebutuhan

- Python 3.x

## Cara Menjalankan

Jalankan server dengan perintah:

```bash
python time_server.py
```
## Format Permintaan Client 

- TIME\r\n

  Akan dibalas dengan waktu saat ini dalam format `JAM hh:mm:ss`.

- QUIT\r\n


## Pengujian

gunakan telnet untuk menguji server:

```bash
telnet localhost 45000
```
lalu kirimkan perintah `TIME` untuk mendapatkan waktu saat ini atau `QUIT` untuk menutup koneksi.

import logging
import time
import os
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple
from file_client_cli import remote_get, remote_upload
import gc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CLIENT_WORKERS = [1, 5, 50]

def test_worker(operation: str, filename: str, worker_id: int) -> Tuple[bool, float, int]:
    start_time = time.time()
    try:
        logging.info(f"Worker {worker_id} starting {operation} of {filename}")
        if operation == 'download':
            success = remote_get(filename)
            # File hasil download ada di current directory
            filepath = filename
        else:
            success = remote_upload(filename)
            # File yang diupload ada di ./files/
            filepath = os.path.join("./files", filename)
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return False, time.time() - start_time, 0
        file_size = os.path.getsize(filepath)
        time_taken = time.time() - start_time
        logging.info(f"Worker {worker_id} completed {operation} in {time_taken:.2f} seconds")
        gc.collect()
        return success, time_taken, file_size
    except Exception as e:
        logging.error(f"Worker {worker_id} error during {operation}: {str(e)}")
        return False, time.time() - start_time, 0

def run_concurrent_test(operation: str, filename: str, num_clients: int) -> Dict:
    start_time = time.time()
    results = []
    try:
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(test_worker, operation, filename, i) for i in range(num_clients)]
            results = [future.result() for future in futures]
    finally:
        if operation == 'download':
            try:
                os.remove(filename)
            except:
                pass
        gc.collect()
    total_time = time.time() - start_time
    successful_workers = sum(1 for success, _, _ in results if success)
    failed_workers = num_clients - successful_workers
    total_bytes = sum(bytes_transferred for _, _, bytes_transferred in results)
    total_time_per_client = total_time / num_clients
    throughput_per_client = total_bytes / total_time if total_time > 0 else 0
    return {
        "operation": operation,
        "filename": filename,
        "num_clients": num_clients,
        "total_time": total_time,
        "total_time_per_client": total_time_per_client,
        "throughput_per_client": throughput_per_client,
        "successful_workers": successful_workers,
        "failed_workers": failed_workers,
        "total_bytes_transferred": total_bytes
    }

def save_results_to_csv(results: List[Dict], filename: str = None) -> None:
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_thread_results_{timestamp}.csv"
    headers = [
        "Nomor",
        "Operasi",
        "Volume",
        "Jumlah Client Worker",
        "Waktu Total per Client (seconds)",
        "Throughput per Client (bytes/second)",
        "Client Workers Sukses",
        "Client Workers Gagal"
    ]
    try:
        file_exists = os.path.exists(filename)
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            start_idx = 1
            if file_exists:
                with open(filename, 'r') as f:
                    start_idx = sum(1 for _ in f)
            for idx, result in enumerate(results, start_idx):
                row = {
                    "Nomor": idx,
                    "Operasi": result['operation'],
                    "Volume": result['filename'],
                    "Jumlah Client Worker": result['num_clients'],
                    "Waktu Total per Client (seconds)": f"{result['total_time_per_client']:.2f}",
                    "Throughput per Client (bytes/second)": f"{result['throughput_per_client']:.2f}",
                    "Client Workers Sukses": result['successful_workers'],
                    "Client Workers Gagal": result['failed_workers']
                }
                writer.writerow(row)
        logging.info(f"Results appended to {filename}")
    except Exception as e:
        logging.error(f"Error saving results to CSV: {str(e)}")

def ensure_test_files():
    files_dir = "./files"
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
        logging.info(f"Created directory: {files_dir}")
    file_sizes = {
        '10mb-example-jpg.jpg': 10 * 1024 * 1024,
        '50mb.jpg': 50 * 1024 * 1024,
        '100-mb-example-jpg.jpg': 100 * 1024 * 1024
    }
    for filename, size in file_sizes.items():
        filepath = os.path.join(files_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(os.urandom(size))
            logging.info(f"Created test file: {filename}")

def main():
    ensure_test_files()
    operations = ['upload', 'download']
    file_sizes = ['10mb-example-jpg.jpg', '50mb.jpg', '100-mb-example-jpg.jpg']
    results = []
    for operation in operations:
        for filename in file_sizes:
            for num_clients in CLIENT_WORKERS:
                logging.info(f"Testing {operation} of {filename} with {num_clients} client workers")
                result = run_concurrent_test(operation, filename, num_clients)
                results.append(result)
                print(f"\nThread Results for {operation} {filename}:")
                print(f"Client Workers: {num_clients}")
                print(f"Total Time per Client: {result['total_time_per_client']:.2f} seconds")
                print(f"Throughput per Client: {result['throughput_per_client']/1024/1024:.2f} MB/s")
                print(f"Successful Workers: {result['successful_workers']}")
                print(f"Failed Workers: {result['failed_workers']}")
                print("-" * 80)
                gc.collect()
    save_results_to_csv(results)

if __name__ == "__main__":
    main()

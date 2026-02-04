import time
import socket
import sys

def wait_for_minio(host='minio', port=9000, timeout=60):
    """Ожидание доступности MinIO"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"MinIO at {host}:{port} is available!")
                return True
            else:
                print(f"Waiting for MinIO at {host}:{port}...")
        except Exception as e:
            print(f"Error checking MinIO: {e}")
        
        time.sleep(5)
    
    print(f"MinIO not available after {timeout} seconds")
    return False

if __name__ == "__main__":
    if wait_for_minio():
        sys.exit(0)
    else:
        sys.exit(1)
import socket
import os
import ssl

SERVER_HOST = '192.168.241.149'
SERVER_PORT = 12345
BUFFER_SIZE = 4096
DOWNLOADS_DIR = "downloads"

def main():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations('yourdomain.crt')  
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client_socket = context.wrap_socket(client_socket, server_hostname=SERVER_HOST)
        ssl_client_socket.connect((SERVER_HOST, SERVER_PORT))

        while True:
            try:
                command = input("Enter command (UPLOAD <filename>, DOWNLOAD <filename>): ")
                ssl_client_socket.send(command.encode())

                if command.startswith("UPLOAD"):
                    file_name = command.split()[1]
                    upload_file(file_name, ssl_client_socket)
                elif command.startswith("DOWNLOAD"):
                    file_name = command.split()[1]
                    download_file(file_name, ssl_client_socket)
                else:
                    print("Invalid command.")
            except Exception as e:
                print(f"Error processing command: {e}")

        ssl_client_socket.close()
    except Exception as e:
        print(f"Error connecting to server: {e}")

def upload_file(file_name, client_socket):
    try:
        with open(file_name, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.send(data)
        client_socket.send("DONE".encode())
        print(f"File {file_name} uploaded.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error uploading file: {e}")

def download_file(file_name, client_socket):
    try:
        response = client_socket.recv(BUFFER_SIZE).decode()
        if response == "EXIST":
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            file_path = os.path.join(DOWNLOADS_DIR, file_name)
            with open(file_path, "wb") as file:
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data or data == b"DONE":
                        break
                    file.write(data)
            print(f"File saved to: {file_path}")
        else:
            print("File does not exist on the server.")
    except Exception as e:
        print(f"Error downloading file: {e}")

if __name__ == "__main__":
    main()

import socket
import ssl
import os

SERVER_HOST = '192.168.241.149'
SERVER_PORT = 12345
BUFFER_SIZE = 4096
UPLOADS_DIR = "uploads"

def main():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('yourdomain.crt', 'yourdomain.key')

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Client {client_address} connected.")

            ssl_client_socket = context.wrap_socket(client_socket, server_side=True)

            try:
                request = ssl_client_socket.recv(BUFFER_SIZE).decode()
                if request.startswith("UPLOAD"):
                    file_name = request.split()[1]
                    receive_file(file_name, ssl_client_socket)
                elif request.startswith("DOWNLOAD"):
                    file_name = request.split()[1]
                    send_file(file_name, ssl_client_socket)
                else:
                    ssl_client_socket.send("Invalid command.".encode())
            except Exception as e:
                print(f"Error processing client request: {e}")

            ssl_client_socket.close()

    except Exception as e:
        print(f"Error starting server: {e}")

def receive_file(file_name, client_socket):
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        file_path = os.path.join(UPLOADS_DIR, file_name)
        with open(file_path, "wb") as file:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data or data == b"DONE":
                    break
                file.write(data)
        print(f"File saved to: {file_path}")
    except Exception as e:
        print(f"Error receiving file: {e}")

def send_file(file_name, client_socket):
    try:
        file_path = os.path.join(UPLOADS_DIR, file_name)
        if os.path.exists(file_path):
            client_socket.send("EXIST".encode())
            with open(file_path, "rb") as file:
                while True:
                    data = file.read(BUFFER_SIZE)
                    if not data:
                        break
                    client_socket.send(data)
            client_socket.send("DONE".encode())
            print(f"File {file_name} sent.")
        else:
            client_socket.send("NOTEXIST".encode())
    except Exception as e:
        print(f"Error sending file: {e}")

if __name__ == "__main__":
    main()

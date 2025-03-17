import socket

HOST = '192.168.64.1'
PORT = 12345

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        while True:
            # Receive and print data from the server.
            data = client_socket.recv(1024)
            if not data:
                break
            print("Server:", data.decode().strip())

            # Read user input and send it to the server.
            message = input("Enter command: ")
            client_socket.sendall(message.encode())

            if message.lower() == "exit":
                break
    except Exception as e:
        print("An error occurred:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
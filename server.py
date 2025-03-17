import socket
import threading

from server_handlers import handle_state, handle_score, handle_exit

# All interfaces: 0.0.0.0, localhost only: 127.0.0.1
HOST = '192.168.64.1'
PORT = 12345 

# For each client socket, we store a state dictionary.
clients = {}
clients_lock = threading.Lock()

# Mapping command names to their callback functions
command_callbacks = {
    "score": handle_score,
    "state": handle_state,
    "exit": handle_exit,
}

def get_welcome_message():
    return (
        "Welcome to the game server!\n"
        "Commands:\n"
        "  score <number>  - Add the given number to your score (for testing)\n"
        "  state           - Display your current state\n"
        "  exit            - Disconnect from the server\n"
    )

def send_welcome_message(client_socket):
    welcome_message = get_welcome_message()
    client_socket.sendall(welcome_message.encode())

def client_handler(client_socket, address):
    # Initialize state for the new client
    with clients_lock:
        clients[client_socket] = {"address": address, "score": 0}

    send_welcome_message(client_socket)

    try:
        while True:
            data = client_socket.recv(1024)
            
            # Client disconnected
            if not data:
                break

            message = data.decode().strip()
            print(f"Received from {address}: {message}")

            if not message:
                continue

            # Determine command based on first word
            command = message.split()[0].lower()
            client_state = clients.get(client_socket, {})

            # If a callback exists, invoke it; otherwise send an error message.
            if command in command_callbacks:
                should_exit = command_callbacks[command](client_socket, message, client_state)
                if should_exit:
                    break
            else:
                client_socket.sendall(f"Unknown command: {message}\n".encode())
    except Exception as e:
        print(f"Error with client {address}: {e}")
    finally:
        print(f"Client {address} disconnected.")
        with clients_lock:
            if client_socket in clients:
                del clients[client_socket]
        client_socket.close()

def start_server():
    # https://docs.python.org/3/library/socket.html#socket.socket
    # https://docs.python.org/3/library/socket.html#socket.create_server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid: OSError: [Errno 98] Address already in use
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    # up to 4 connections can wait up in the queue.
    server_socket.listen(4)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Client {address} connected.")
            
            # Start a new thread for each connected client.
            thread = threading.Thread(target=client_handler, args=(client_socket, address))

            # When the server is down, exit all clients.
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
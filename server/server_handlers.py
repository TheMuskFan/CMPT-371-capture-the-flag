def handle_score(client_socket, message, client_state):
    parts = message.split()
    if len(parts) == 2 and parts[1].isdigit():
        increment = int(parts[1])
        client_state["score"] += increment
        current_score = client_state["score"]
        response = f"Your score has been updated to {current_score}.\n"
        client_socket.sendall(response.encode())
    else:
        client_socket.sendall("Invalid score command. Use: score <number>\n".encode())
    # Return False so the handler loop continues.
    return False

def handle_state(client_socket, message, client_state):
    client_socket.sendall(f"Your state: {client_state}\n".encode())
    return False

def handle_exit(client_socket, message, client_state):
    client_socket.sendall("Goodbye!\n".encode())
    # Return True to signal that we should break out of the loop and disconnect the client.
    return True
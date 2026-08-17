import socket
import threading

HOST = "0.0.0.0"
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
finally:
    s.close()

print("server on")
print(f"ip: {local_ip}")

clients = []
clients_lock = threading.Lock()


def broadcast(message, sender):
    dead_clients = []

    with clients_lock:
        current_clients = clients.copy()

    for client in current_clients:
        if client == sender:
            continue

        try:
            client.send(message)
        except (ConnectionResetError, BrokenPipeError, OSError):
            dead_clients.append(client)

    if dead_clients:
        with clients_lock:
            for client in dead_clients:
                if client in clients:
                    clients.remove(client)
                try:
                    client.close()
                except OSError:
                    pass


def handle_client(client_socket):
    try:
        while True:
            try:
                data = client_socket.recv(1024)

                if not data:
                    break

                print(data.decode("utf-8"))
                broadcast(data, client_socket)

            except (ConnectionResetError, OSError):
                break

    finally:
        try:
            print(f"{client_socket.getpeername()} disconnected")
        except OSError:
            print("A client disconnected")

        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)

        try:
            client_socket.close()
        except OSError:
            pass


while True:
    client_socket, address = server.accept()

    print(f"{address} has connected")

    with clients_lock:
        clients.append(client_socket)

    threading.Thread(
        target=handle_client,
        args=(client_socket,),
        daemon=True,
    ).start()
from game_server import GameServer

if __name__ == '__main__':
    host = input("Enter the host IP address: ")
    port = int(input("Enter the port number: ") or 12345)
    
    server = GameServer(host, port)
    server.start()
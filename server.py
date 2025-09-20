import socket
import threading
import datetime
import sys


class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients = []
        self.nicknames = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen()
            print(f"🚀 Server started on {self.host}:{self.port}")
            print("📡 Waiting for connections...")
            print("Press Ctrl+C to stop the server")

            while True:
                client, address = self.server.accept()
                print(f"✅ Connection from {address[0]}:{address[1]}")

                # Request nickname
                client.send("NICK".encode('utf-8'))
                nickname = client.recv(1024).decode('utf-8')

                self.nicknames.append(nickname)
                self.clients.append(client)

                print(f"👤 Client nickname: {nickname}")
                self.broadcast(f"🌟 {nickname} joined the chat!".encode('utf-8'))

                # Start thread for client handling
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.shutdown()

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except:
                self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            self.broadcast(f"👋 {nickname} left the chat.".encode('utf-8'))
            client.close()
            print(f"❌ {nickname} disconnected")

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    # Add timestamp and nickname to message
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    nickname = self.nicknames[self.clients.index(client)]
                    formatted_message = f"[{timestamp}] {nickname}: {message.decode('utf-8')}"
                    print(formatted_message)
                    self.broadcast(formatted_message.encode('utf-8'))
                else:
                    self.remove_client(client)
                    break
            except:
                self.remove_client(client)
                break

    def shutdown(self):
        print("🔌 Shutting down server...")
        for client in self.clients:
            client.close()
        self.server.close()
        sys.exit(0)


if __name__ == "__main__":
    server = ChatServer()
    server.start()
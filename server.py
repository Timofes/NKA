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
                
                # Request nickname with error handling
                try:
                    client.send("NICK".encode('utf-8'))
                    nickname = client.recv(1024).decode('utf-8').strip()
                    
                    if not nickname:
                        nickname = f"Guest_{address[1]}"
                    
                    self.nicknames.append(nickname)
                    self.clients.append(client)
                    
                    print(f"👤 Client nickname: {nickname}")
                    self.broadcast(f"🌟 {nickname} joined the chat!".encode('utf-8'))
                    
                    # Start thread for client handling
                    thread = threading.Thread(target=self.handle_client, args=(client, nickname))
                    thread.daemon = True
                    thread.start()
                    
                except UnicodeDecodeError:
                    print(f"❌ Unicode error from {address[0]}, using default nickname")
                    nickname = f"Guest_{address[1]}"
                    self.nicknames.append(nickname)
                    self.clients.append(client)
                    self.broadcast(f"🌟 {nickname} joined the chat!".encode('utf-8'))
                    thread = threading.Thread(target=self.handle_client, args=(client, nickname))
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
            nickname = self.nicknames[index]
            self.clients.remove(client)
            self.nicknames.remove(nickname)
            try:
                self.broadcast(f"👋 {nickname} left the chat.".encode('utf-8'))
            except:
                pass
            client.close()
            print(f"❌ {nickname} disconnected")
    
    def handle_client(self, client, nickname):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    try:
                        decoded_message = message.decode('utf-8')
                    except UnicodeDecodeError:
                        decoded_message = message.decode('latin-1', errors='ignore')
                    
                    # Add timestamp and nickname to message
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    formatted_message = f"[{timestamp}] {nickname}: {decoded_message}"
                    print(formatted_message)
                    
                    try:
                        self.broadcast(formatted_message.encode('utf-8'))
                    except UnicodeEncodeError:
                        safe_message = f"[{timestamp}] {nickname}: [binary message]"
                        self.broadcast(safe_message.encode('utf-8'))
                else:
                    self.remove_client(client)
                    break
            except Exception as e:
                print(f"Error handling client {nickname}: {e}")
                self.remove_client(client)
                break
    
    def shutdown(self):
        print("🔌 Shutting down server...")
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.server.close()
        sys.exit(0)

if __name__ == "__main__":
    server = ChatServer()
    server.start()

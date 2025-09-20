import socket
import threading
import datetime
import sys
import json
from typing import Dict

from lib.include.User import User
from lib.include.NDFA import NDFA
from lib.include.Ans import Ans


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
            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for connections...")
            print("Press Ctrl+C to stop the server")

            while True:
                client, address = self.server.accept()
                print(f"Connection from {address[0]}:{address[1]}")

                # Request nickname with error handling
                try:
                    client.send("NICK".encode('utf-8'))
                    nickname = client.recv(1024).decode('utf-8').strip()

                    if not nickname:
                        nickname = f"Guest_{address[1]}"

                    self.nicknames.append(nickname)
                    self.clients.append(client)

                    print(f"Client nickname: {nickname}")
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

    def process_ndfa_data(self, user_data: Dict, ndfa_data: Dict) -> Ans:
        """Обработка данных NDFA и создание ответа"""
        try:
            user = User.from_dict(user_data)
            ndfa = NDFA.from_dict(ndfa_data)

            # Здесь должна быть логика проверки NDFA
            # Временно создаем фиктивный ответ
            ans = Ans(
                id=user.id,
                id_task=user.id_task if user.id_task else 0,
                error_count=0,
                error_msg=[],
                code="SUCCESS"
            )

            # Простая проверка корректности NDFA
            if not ndfa.V:
                ans.error_count += 1
                ans.error_msg.append("Алфавит не может быть пустым")

            if not ndfa.Q:
                ans.error_count += 1
                ans.error_msg.append("Состояния не могут быть пустыми")

            if not ndfa.q0:
                ans.error_count += 1
                ans.error_msg.append("Начальное состояние не задано")

            if ndfa.q0 and ndfa.q0 not in ndfa.Q:
                ans.error_count += 1
                ans.error_msg.append(f"Начальное состояние '{ndfa.q0}' не найдено в Q")

            for state in ndfa.F:
                if state not in ndfa.Q:
                    ans.error_count += 1
                    ans.error_msg.append(f"Конечное состояние '{state}' не найдено в Q")

            return ans

        except Exception as e:
            return Ans(
                id=user_data.get("id", 0),
                id_task=user_data.get("id_task", 0),
                error_count=1,
                error_msg=[f"Ошибка обработки: {str(e)}"],
                code="ERROR"
            )

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
                # Получаем длину JSON данных
                length_bytes = client.recv(4)
                if not length_bytes:
                    self.remove_client(client)
                    break

                data_length = int.from_bytes(length_bytes, 'big')

                # Получаем JSON данные
                json_data = b''
                while len(json_data) < data_length:
                    chunk = client.recv(min(4096, data_length - len(json_data)))
                    if not chunk:
                        break
                    json_data += chunk

                if not json_data:
                    self.remove_client(client)
                    break

                try:
                    # Парсим JSON
                    data = json.loads(json_data.decode('utf-8'))
                    user_data = data.get("user", {})
                    ndfa_data = data.get("data", {})

                    print(
                        f"📨 Received from {nickname}: UserID={user_data.get('id')}, TaskID={user_data.get('id_task')}")

                    # Обрабатываем данные
                    ans = self.process_ndfa_data(user_data, ndfa_data)

                    # Отправляем ответ
                    ans_json = json.dumps(ans.to_dict()).encode('utf-8')
                    ans_length = len(ans_json).to_bytes(4, 'big')

                    client.send(ans_length + ans_json)
                    print(f"📤 Sent response to {nickname}")

                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from {nickname}")
                    error_ans = Ans(
                        id=0,
                        id_task=0,
                        error_count=1,
                        error_msg=["Invalid JSON format"],
                        code="ERROR"
                    )
                    error_json = json.dumps(error_ans.to_dict()).encode('utf-8')
                    error_length = len(error_json).to_bytes(4, 'big')
                    client.send(error_length + error_json)

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

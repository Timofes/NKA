import socket
import threading
import datetime
import sys
import json
from time import sleep
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
        try:
            if client in self.clients:
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                print(f"🔍 [DEBUG] Removing client {nickname} from list")
                self.clients.remove(client)
                self.nicknames.remove(nickname)
                try:
                    if self.clients:  # Только если есть другие клиенты
                        print(f"🔍 [DEBUG] Broadcasting leave message for {nickname}")
                        self.broadcast(f"👋 {nickname} left the chat.".encode('utf-8'))
                except Exception as e:
                    print(f"🔍 [DEBUG] Error broadcasting leave message: {e}")
                try:
                    print(f"🔍 [DEBUG] Closing socket for {nickname}")
                    client.close()
                    print(f"🔍 [DEBUG] Socket closed for {nickname}")
                except Exception as e:
                    print(f"🔍 [DEBUG] Error closing socket: {e}")
                print(f"❌ {nickname} disconnected")
            else:
                print(f"🔍 [DEBUG] Client not found in list, already removed?")
        except ValueError:
            print(f"🔍 [DEBUG] ValueError in remove_client, client already removed")
        except Exception as e:
            print(f"🔍 [DEBUG] Unexpected error in remove_client: {e}")

    def handle_client(self, client, nickname):
        try:
            while True:
                try:
                    print(f"🔍 [DEBUG] Waiting for data from {nickname}...")

                    # Получаем длину JSON данных
                    length_bytes = client.recv(4)
                    if not length_bytes:
                        print(f"🔍 [DEBUG] No length bytes from {nickname}, breaking")
                        break

                    data_length = int.from_bytes(length_bytes, 'big')
                    print(f"🔍 [DEBUG] Expected data length: {data_length} from {nickname}")

                    # Получаем JSON данные
                    json_data = b''
                    while len(json_data) < data_length:
                        chunk = client.recv(min(4096, data_length - len(json_data)))
                        if not chunk:
                            print(f"🔍 [DEBUG] No chunk data from {nickname}, breaking")
                            break
                        json_data += chunk

                    if not json_data:
                        print(f"🔍 [DEBUG] No JSON data from {nickname}, breaking")
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
                        sleep(2000)
                        ans_json = json.dumps(ans.to_dict()).encode('utf-8')
                        ans_length = len(ans_json).to_bytes(4, 'big')

                        print(f"🔍 [SERVER] Sending response: {len(ans_json)} bytes")
                        client.send(ans_length + ans_json)
                        print(f"📤 Sent response to {nickname}")

                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON from {nickname}: {e}")
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

                except ConnectionResetError:
                    print(f"🔌 Connection reset by {nickname}")
                    break
                except BrokenPipeError:
                    print(f"🔌 Broken pipe for {nickname}")
                    break
                except OSError as e:
                    print(
                        f"🔌 OSError for {nickname}: {e} (winerror: {e.winerror if hasattr(e, 'winerror') else 'N/A'})")
                    if hasattr(e, 'winerror') and e.winerror == 10038:
                        print(f"🔌 Socket operation on non-socket for {nickname}")
                        break
                    else:
                        raise
                except Exception as e:
                    print(f"🔌 Unexpected error in inner loop for {nickname}: {e}")
                    break

        except Exception as e:
            print(f"❌ Error handling client {nickname}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"🔍 [DEBUG] Finally block for {nickname}, removing client")
            # Убеждаемся, что клиент удаляется при любом исходе
            self.remove_client(client)

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

import socket
from typing import Optional, Generator


class TCPClient:
    _instance: Optional['TCPClient'] = None

    def __new__(cls, host: str, port: int) -> 'TCPClient':
        if cls._instance is None:
            cls._instance = super(TCPClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host: str, port: int) -> None:
        if not self._initialized:
            self.chunked_data: list[str] = []
            self.host: str = host
            self.port: int = port
            self.client_socket: Optional[socket.socket] = None
            self.connected: bool = False
            self._initialized = True

    def _create_socket(self) -> None:
        self.client_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        if not self.connected:
            try:
                if self.client_socket is None:
                    self._create_socket()
                self.client_socket.connect((self.host, self.port))
                self.connected = True
            except Exception as e:
                print(f"Failed to connect: {e}")
                if self.client_socket:
                    self.client_socket.close()
                self.client_socket = None

    def send_and_wait_stream(self, message: str, is_stream: bool = False) -> Generator[Optional[str], None, None]:
        if not self.connected:
            self.connect()
        try:
            self.client_socket.sendall(f"{message}\x00".encode('utf-8'))
            self.chunked_data.clear()
            while True:
                data: Optional[bytes] = self.client_socket.recv(1024)
                if not data:
                    break
                yield data.decode('utf-8')
            self.close()
            return ''.join(self.chunked_data)
        except Exception as e:
            print(f"Error: {e}")
            self.close()
        return None

    def send_and_wait(self, message: str) -> Optional[str]:
        if not self.connected:
            self.connect()
        try:
            self.client_socket.sendall(f"{message}\x00".encode('utf-8'))
            self.chunked_data.clear()
            while True:
                data: Optional[bytes] = self.client_socket.recv(1024)
                if not data:
                    break
                self.chunked_data.append(data.decode('utf-8'))
            self.close()
            return ''.join(self.chunked_data)
        except Exception as e:
            print(f"Error: {e}")
            self.close()
        return None

    def close(self) -> None:
        if self.connected and self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.connected = False

import socket
from typing import Optional, Generator, AsyncGenerator
import asyncio


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

    async def connect(self) -> None:
        if not self.connected:
            try:
                if self.client_socket is None:
                    self._create_socket()
                await asyncio.get_event_loop().sock_connect(self.client_socket, (self.host, self.port))
                self.connected = True
            except Exception as e:
                print(f"Failed to connect: {e}")
                if self.client_socket:
                    self.client_socket.close()
                self.client_socket = None

    async def send_and_wait_stream(self, message: str, is_stream: bool = False) -> AsyncGenerator[Optional[str], None]:
        if not self.connected:
            await self.connect()
        try:
            await asyncio.get_event_loop().sock_sendall(self.client_socket, f"{message}\x00".encode('utf-8'))
            self.chunked_data.clear()
            while True:
                data: Optional[bytes] = await asyncio.get_event_loop().sock_recv(self.client_socket, 1024)
                if not data:
                    break
                yield data.decode('utf-8')
            await self.close()
            # Just end the generator here without returning any value
        except Exception as e:
            print(f"Error: {e}")
            await self.close()


    async def send_and_wait(self, message: str) -> Optional[str]:
        if not self.connected:
            await self.connect()
        try:
            await asyncio.get_event_loop().sock_sendall(self.client_socket, f"{message}\x00".encode('utf-8'))
            self.chunked_data.clear()
            while True:
                data: Optional[bytes] = await asyncio.get_event_loop().sock_recv(self.client_socket, 1024)
                if not data:
                    break
                self.chunked_data.append(data.decode('utf-8'))
            await self.close()
            return ''.join(self.chunked_data)
        except Exception as e:
            print(f"Error: {e}")
            await self.close()
        return None

    async def close(self) -> None:
        if self.connected and self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.connected = False

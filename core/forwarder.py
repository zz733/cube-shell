import logging
from contextlib import suppress

import paramiko
import socket
import threading
import select
import time


class ForwarderManager:
    def __init__(self):
        self.tunnels = {}
        self.ssh_clients = {}

    def add_tunnel(self, tunnel_id, tunnel):
        self.tunnels[tunnel_id] = tunnel

    def remove_tunnel(self, tunnel_id):
        if tunnel_id in self.tunnels:
            tunnel = self.tunnels[tunnel_id]
            tunnel.stop()

            # 给隧道一些时间来完全关闭
            time.sleep(1)
            # 如果 SSH 客户端没有其他隧道关联，则关闭 SSH 客户端
            self.close_ssh_client(tunnel.ssh_client)
            del self.tunnels[tunnel_id]

    def close_ssh_client(self, ssh_client):
        if ssh_client in self.ssh_clients:
            with suppress(Exception):
                ssh_client.close()
            del self.ssh_clients[ssh_client]

    def start_tunnel(self, tunnel_id, tunnel_type, local_port, remote_host=None, remote_port=None, ssh_host=None,
                     ssh_port=None, ssh_user=None, ssh_password=None, key_type=None, key_file=None):

        # 加载私钥
        private_key = None
        if key_type == 'Ed25519Key':
            private_key = paramiko.Ed25519Key.from_private_key_file(key_file)
        elif key_type == 'RSAKey':
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
        elif key_type == 'ECDSAKey':
            private_key = paramiko.ECDSAKey.from_private_key_file(key_file)
        elif key_type == 'DSSKey':
            private_key = paramiko.DSSKey.from_private_key_file(key_file)

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if private_key:
                ssh_client.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, pkey=private_key)
            else:
                ssh_client.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

            transport = ssh_client.get_transport()

            if tunnel_type == 'local':
                tunnel = LocalPortForwarder(ssh_client, tunnel_id, transport, remote_host, remote_port, local_port)
            elif tunnel_type == 'remote':
                tunnel = RemotePortForwarder(ssh_client, tunnel_id, transport, local_port, remote_host, remote_port)
            elif tunnel_type == 'dynamic':
                tunnel = DynamicPortForwarder(ssh_client, tunnel_id, transport, local_port)
            else:
                raise ValueError("Invalid tunnel type.")

            tunnel.start()

            return tunnel, ssh_client, transport
        except Exception as e:
            logging.error(f"Error starting tunnel: {e}")
            with suppress(Exception):
                ssh_client.close()
            raise


class LocalPortForwarder(threading.Thread):
    """
    本地端口转发
    """

    def __init__(self, ssh_client, tunnel_id, ssh_transport, remote_host, remote_port, local_port):
        super(LocalPortForwarder, self).__init__()
        self.daemon = True
        self.tunnel_id = tunnel_id
        self.ssh_transport = ssh_transport
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.ssh_client = ssh_client
        self.running = False
        self.listen_socket = None
        self.client_socket = None
        self.lock = threading.Lock()  # 添加锁

    def stop(self):
        with self.lock:  # 使用锁保护对 running 的修改
            self.running = False
        if self.listen_socket:
            try:
                self.listen_socket.close()
                self.listen_socket = None
                logging.info(f"Socket on port {self.local_port} has been closed")
            except Exception as e:
                logging.error(f"Exception in ForwardServer.stop: {e}")

    def run(self):
        self.running = True
        try:
            # 创建本地监听的套接字
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.listen_socket.bind(('127.0.0.1', self.local_port))  # 增加异常处理
            except Exception as e:
                logging.error(f"Error binding socket: {e}")
                return
            self.listen_socket.listen(100)
            logging.info(f"Listening for connections on 127.0.0.1:{self.local_port}...")

            while self.running:
                try:
                    client_socket, addr = self.listen_socket.accept()
                    logging.info(f"Received connection from {addr[0]}:{addr[1]}")

                    self.client_socket = client_socket

                    # 通过 SSH 隧道创建新的通道
                    channel = self.ssh_transport.open_channel(
                        kind='direct-tcpip',
                        dest_addr=(self.remote_host, self.remote_port),
                        src_addr=addr
                    )

                    if channel:
                        # 创建转发线程
                        threading.Thread(target=self.forward_data, args=(client_socket, channel)).start()
                    else:
                        logging.warning("Failed to open channel.")
                        client_socket.close()
                except socket.timeout:
                    # 可以在这里增加一个超时检查，防止无限等待
                    pass
                except Exception as e:
                    self.running = False
                    logging.error(f"Error accepting connection: {e}")
        finally:
            self.stop()

    def forward_data(self, client_socket, channel):
        try:
            while self.running:
                # 使用 select 监听 client_socket 和 channel
                r, w, x = select.select([client_socket, channel], [], [])
                # 如果 client_socket 有数据可读
                if client_socket in r:
                    try:
                        data = client_socket.recv(1024)
                        if len(data) <= 0:
                            # 如果没有读取到数据，说明连接已关闭
                            break
                        # 将数据发送到 channel
                        channel.send(data)
                    except Exception as e:
                        print(f"Error receiving data from client: {e}")
                        break
                # 如果 channel 有数据可读
                if channel in r:
                    try:
                        data = channel.recv(1024)
                        if len(data) <= 0:
                            # 如果没有读取到数据，说明连接已关闭
                            break
                        # 将数据发送回 client_socket
                        client_socket.send(data)
                    except Exception as e:
                        print(f"Error receiving data from channel: {e}")
                        break
        finally:
            with self.lock:
                self.running = False
            channel.close()
            client_socket.close()
            print("Connection closed.")


class RemotePortForwarder(threading.Thread):
    """
    远程端口转发
    """

    def __init__(self, ssh_client, tunnel_id, ssh_transport, local_port, remote_host, remote_port):
        super(RemotePortForwarder, self).__init__()
        self.daemon = True
        self.tunnel_id = tunnel_id
        self.ssh_transport = ssh_transport
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.ssh_client = ssh_client
        self.running = False
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()  # 添加锁

    def stop(self):
        with self._lock:
            self.running = False
        self._shutdown_event.set()

    def run(self):
        self.running = True
        self._shutdown_event.clear()
        self.ssh_transport.request_port_forward('', self.local_port)

        while self.running and not self._shutdown_event.is_set():
            chan = self.ssh_transport.accept(1000)
            if chan is None or not self.running:
                continue

            thr = threading.Thread(target=self.handle, args=(chan,))
            thr.setDaemon(True)
            thr.start()

    def handle(self, chan):
        sock = socket.socket()
        try:
            sock.connect((self.remote_host, self.remote_port))
        except (socket.error, Exception) as e:
            logging.error(f"Forwarding failed: {e}")
            self._close_resources(chan, sock)
            return

        logging.info(f"Connected! Tunnel open {chan.origin_addr} -> ({self.remote_host}, {self.remote_port})")

        while self.running and not self._shutdown_event.is_set():
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                sock.send(data)

        self._close_resources(chan, sock)
        logging.info(f"Tunnel closed from {chan.origin_addr}")

    def _close_resources(self, chan, sock):
        chan.close()
        sock.close()


class DynamicPortForwarder(threading.Thread):
    """
    动态端口转发
    """

    def __init__(self, ssh_client, tunnel_id, ssh_transport, local_port):
        super(DynamicPortForwarder, self).__init__()
        self.daemon = True
        self.tunnel_id = tunnel_id
        self.ssh_transport = ssh_transport
        self.local_port = local_port
        self.ssh_client = ssh_client
        self.running = False
        self._shutdown_event = threading.Event()
        self.channels = []
        self.channels_lock = threading.Lock()  # 添加锁

    def stop(self):
        self.running = False
        self._shutdown_event.set()
        # 关闭所有已打开的通道
        with self.channels_lock:
            for channel in self.channels:
                channel.close()
            self.channels.clear()

    def run(self):
        self.running = True
        self._shutdown_event.clear()
        self.ssh_transport.request_port_forward('', self.local_port)

        while self.running and not self._shutdown_event.is_set():
            chan = self.ssh_transport.accept(1000)
            if chan is None or not self.running:
                continue

            thr = threading.Thread(target=self.handle, args=(chan,))
            thr.setDaemon(True)
            thr.start()

    def handle(self, chan):
        try:
            # 接受目标地址类型
            address_type = ord(chan.recv(1))
            if address_type == 1:  # IPv4
                target_addr = socket.inet_ntoa(chan.recv(4))
            elif address_type == 3:  # Domain name
                domain_length = ord(chan.recv(1))
                target_addr = chan.recv(domain_length).decode('utf-8')
            else:
                logging.warning("Unsupported address type.")
                chan.close()
                return

            # 接受目标端口
            target_port = int.from_bytes(chan.recv(2), byteorder='big')

            logging.info(f"SOCKS request to {target_addr}:{target_port}")

            # 通过 SSH 隧道创建新的通道
            channel = self.ssh_transport.open_channel(
                kind='direct-tcpip',
                dest_addr=(target_addr, target_port),
                src_addr=chan.getpeername()
            )

            if channel:
                with self.channels_lock:
                    self.channels.append(channel)
                # 创建转发线程
                threading.Thread(target=self.forward_data, args=(chan, channel)).start()
            else:
                print("Failed to open channel.")
                chan.close()
        except Exception as e:
            print(f"Error handling channel: {e}")
            chan.close()

    def forward_data(self, client_socket, channel):
        try:
            while self.running and not self._shutdown_event.is_set():
                # 读取客户端发送的数据
                r, w, x = select.select([client_socket, channel], [], [])
                if client_socket in r:
                    data = client_socket.recv(1024)
                    if len(data) <= 0:
                        break
                    channel.send(data)
                if channel in r:
                    data = channel.recv(1024)
                    if len(data) <= 0:
                        break
                    client_socket.send(data)
        finally:
            channel.close()
            client_socket.close()
            with self.channels_lock:
                self.channels.remove(channel)
            print("Connection closed.")


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

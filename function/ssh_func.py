import paramiko

from core.backend import BaseBackend
from core.mux import mux


class SshClient(BaseBackend):

    def __init__(self, host, port, username, password, key_type, key_file):
        super(SshClient, self).__init__()
        self.host, self.port, self.username, self.password, self.key_type, self.key_file = host, port, username, \
            password, key_type, key_file
        self.close_sig = 1
        self.cpu_use, self.mem_use, self.disk_use = 0, 0, 0
        self.docker_info = []

        self.buffer1 = ['▉', '']
        self.buffer3 = ''
        self.buffer_write = b''
        # 加载私钥
        if key_type == 'Ed25519Key':
            # ssh-ed25519
            self.private_key = paramiko.Ed25519Key.from_private_key_file(key_file)
        elif key_type == 'RSAKey':
            self.private_key = paramiko.RSAKey.from_private_key_file(key_file)
        elif key_type == 'ECDSAKey':
            self.private_key = paramiko.ECDSAKey.from_private_key_file(key_file)
        elif key_type == 'DSSKey':
            self.private_key = paramiko.DSSKey.from_private_key_file(key_file)
        elif key_type == '':
            self.private_key = None

        # 初始化 SSH 客户端和通道状态
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = None

    def connect(self):
        """
        建立 SSH 连接的方法。
        """
        try:
            if self.private_key:
                self.conn.connect(hostname=self.host, port=self.port,
                                  username=self.username, pkey=self.private_key, timeout=10)
            else:
                self.conn.connect(hostname=self.host, port=self.port,
                                  username=self.username, password=self.password, timeout=10)
        except paramiko.ssh_exception.AuthenticationException:
            print("Authentication failed.")
        except Exception as e:
            print(f"Connection error: {e}")

        self.channel = self.conn.get_transport().open_session()
        self.channel.get_pty(width=200, height=400)
        self.channel.invoke_shell()
        mux.add_backend(self)

    def get_read_wait(self):
        """
       获取用于读取操作的等待对象。

       返回:
       - 当前 SSH 通道，用于轮询读取操作。
       """
        return self.channel

    def write(self, data):
        """
       向 SSH 通道写入数据。

       参数:
       - data: 要写入的数据。
       """
        self.channel.send(data)

    def read(self):
        """
        从 SSH 通道读取数据，并写入到屏幕。
        """
        output = self.channel.recv(1024)
        self.write_to_screen(output)

    def close(self):
        """
       关闭 SSH 连接，并从多路复用器中移除该后端。
       """
        if self.channel:
            self.conn.close()
            mux.remove_and_close(self)

    def exec(self, cmd='', pty=False):
        """
        远程执行命令
        :param cmd:
        :param pty:
        :return:
        """
        stdin, stdout, stderr = self.conn.exec_command(timeout=10, command=cmd, get_pty=pty)
        ack = stdout.read().decode('utf8')
        return ack

    def disconnect(self):
        """
        断开连接
        :return:
        """
        self.conn.close()

    def send(self, data):
        """
        发送字符
        :param data:
        :return:
        """
        self.channel.send(data)

    # sftp
    def open_sftp(self) -> paramiko.sftp_client:
        """
        在SSH服务器上打开一个SFTP会话
        :return: 一个新的“.SFTPClient”会话对象
        """
        sftp_client = self.conn.open_sftp()
        return sftp_client


if __name__ == '__main__':
    session = SshClient('192.168.31.162', 22, 'firefly', 'firefly')
    session.connect()
    sftp = session.open_sftp()

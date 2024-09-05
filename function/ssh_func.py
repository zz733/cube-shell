import paramiko
import time


# class CustomSession(paramiko.Channel):
#     def __init__(self, *args, **kwargs):
#         super(CustomSession, self).__init__(*args, **kwargs)
#
#     def send(self, data):
#         # 在这里可以添加自定义逻辑
#         print(f"Sending data: {data}")
#         super(CustomSession, self).send(data)


class SshClient:
    def __init__(self, host, port, username, password, key_type, key_file):
        self.host, self.port, self.username, self.password, self.key_type, self.key_file = host, port, username, \
            password, key_type, key_file
        self.session = None
        self.buffer = ''
        self.buffer1 = ['▉', '']
        self.buffer3 = ''
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
            self.private_key = ''

        # 创建SSH对象
        self.conn = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 创建连接
    def connect(self):
        try:

            if self.private_key:
                self.conn.connect(hostname=self.host, port=self.port,
                                  username=self.username, pkey=self.private_key, timeout=3)
            else:
                self.conn.connect(hostname=self.host, port=self.port,
                                  username=self.username, password=self.password, timeout=3)
            self.session = self.conn.invoke_shell(width=100, height=30)
        finally:
            pass

    # 远程执行命令
    def exec(self, cmd='', pty=False):
        stdin, stdout, stderr = self.conn.exec_command(timeout=10, command=cmd, get_pty=pty)
        ack = stdout.read().decode('utf8')
        return ack

    # 断开连接
    def diconnect(self):
        self.conn.close()

    # shell接收
    def receive(self):
        while True:
            if self.session.recv_ready():
                recv_0 = self.session.recv(1)
                print(b'0' + recv_0)
                if recv_0 != b'':
                    if recv_0 == b'\x07':
                        # Ring the terminal bell
                        pass
                    elif recv_0 == b'\x08':
                        # Backspace
                        self.buffer1.insert(1, self.buffer[-1:])
                        self.buffer = self.buffer[:-1]
                    elif recv_0 == b'\x09':
                        self.buffer += '        '
                    elif recv_0 == b'\x0a':
                        self.buffer += '\n'
                    elif recv_0 == b'\x0b':
                        self.buffer += '\r'
                    elif recv_0 == b'\x20':
                        self.buffer += ' '
                    elif recv_0 == b'\x0f':
                        pass
                    elif recv_0 == b'\x00':
                        pass
                    elif recv_0 == b'\x1b':
                        while True:
                            recv_1 = self.session.recv(1)
                            print(b'1=' + recv_1)
                            if recv_1 == b'c':
                                self.send(b'\x13')
                                time.sleep(1)
                                self.send(b'\x11')
                                break
                            elif recv_1 == b'7':
                                break
                            elif recv_1 == b'8':
                                break
                            elif recv_1 == b'>':
                                break
                            elif recv_1 == b'=':
                                break
                            elif recv_1 == b'%':
                                break
                            elif recv_1 == b']':
                                break
                            elif recv_1 == b'\\':
                                break
                            elif recv_1 == b'4':
                                buf0 = self.session.recv(3)
                                if buf0.endswith(b'5'):
                                    self.session.recv(3)
                                else:
                                    self.session.recv(7)
                                break
                            elif recv_1 == b'[':
                                buf1 = b''
                                check_list = [b'm', b'A', b'B', b'C', b'D', b'E', b'F', b'G', b'H', b'J', b'K',
                                              b'L', b'M', b'P', b'X', b'r', b'@', b'h', b'l', b'c', b'q', b't',
                                              b'u', b'p', b't', b'|']
                                while True:
                                    recv_2 = self.session.recv(1)
                                    print(b'2=' + recv_2)
                                    if recv_2 in check_list:
                                        if recv_2 in [b'm', b'A', b'B', b'D', b'E', b'F',
                                                      b'G', b'M', b'P', b'X', b'r', b'@', b'L',
                                                      b'h', b'l', b'c', b'q', b't', b'u', b'p', b't', b'|']:
                                            break
                                        elif recv_2 == b'@':
                                            self.buffer += (int(buf1[-1]) * ' ')
                                            break
                                        elif recv_2 == b'J':
                                            self.buffer = ''
                                            break
                                        elif recv_2 == b'H':
                                            self.buffer = ''
                                            break
                                        elif recv_2 == b'L':
                                            self.buffer += (int(buf1[-1]) * '\n')
                                            break
                                        elif recv_2 == b'K':
                                            del self.buffer1[1:]
                                            break
                                        elif recv_2 == b'C':
                                            if len(self.buffer1) > 1:
                                                self.buffer += self.buffer1[1]
                                                del self.buffer1[1]
                                            else:
                                                # 处理列表长度不足的情况
                                                print("Warning: self.buffer1 does not have enough elements.")
                                            # self.buffer += self.buffer1[1]
                                            # del self.buffer1[1]
                                            break
                                        else:
                                            continue
                                    else:
                                        buf1 += recv_2
                                        continue
                            elif recv_1 == b'\x1b':
                                continue
                            else:
                                if recv_1 == b'\x07':
                                    # Ring the terminal bell
                                    pass
                                elif recv_1 == b'\x08':
                                    # Backspace
                                    self.buffer1.insert(1, self.buffer[-1:])
                                    self.buffer = self.buffer[:-1]
                                elif recv_1 == b'\x09':
                                    self.buffer += '        '
                                elif recv_1 == b'\x0a':
                                    self.buffer += '\n'
                                elif recv_1 == b'\x0b':
                                    self.buffer += '\r'
                                elif recv_1 == b'\x20':
                                    self.buffer += ' '
                                elif recv_1 == b'\x0f':
                                    pass
                                elif recv_1 == b'\x00':
                                    pass
                                else:
                                    try:
                                        self.buffer += recv_1.decode()
                                    except UnicodeDecodeError:
                                        bu1 = recv_1 + self.session.recv(2)
                                        self.buffer += (b'\x00' + bu1).decode()
                                break
                            break
                    else:
                        try:
                            self.buffer += recv_0.decode()
                        except UnicodeDecodeError:
                            bu0 = recv_0 + self.session.recv(2)
                            self.buffer += (b'\x00' + bu0).decode()
                else:
                    break
                print(self.buffer1)
                self.buffer3 = self.buffer + self.to_contant(self.buffer1)

    @staticmethod
    def to_contant(ls: list) -> str:
        a = ''
        for b in ls:
            a += b
        return a

    # shell发送字符
    def send(self, data):
        self.session.send(data)

    # sftp
    def open_sftp(self) -> paramiko.sftp_client:
        sftp_client = self.conn.open_sftp()
        return sftp_client


if __name__ == '__main__':
    session = SshClient('192.168.31.162', 22, 'firefly', 'firefly')
    session.connect()
    sftp = session.open_sftp()

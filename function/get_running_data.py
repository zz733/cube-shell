import paramiko


class DevicInfo:
    def __init__(self, username, password, host, key_type, key_file):
        super(DevicInfo, self).__init__()
        self.username, self.password, self.host, self.key_type, self.key_file = username, password, host, \
            key_type, key_file
        self.cpu_use, self.mem_use, self.disk_use = 0, 0, 0
        self.docker_info = []
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
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.key_type != '':
            self.conn.connect(username=username, pkey=self.private_key, hostname=host.split(':')[0],
                              port=host.split(':')[1])
        else:
            self.conn.connect(username=username, password=password, hostname=host.split(':')[0],
                              port=host.split(':')[1])
        self.close_sig = 1

    @staticmethod
    def del_more_space(line: str) -> list:
        l = line.split(' ')
        ln = []
        for ll in l:
            if ll == ' ' or ll == '':
                pass
            elif ll != ' ' and ll != '':
                ln.append(ll)
        return ln

    def cpu_use_data(self, info: str) -> tuple:
        lines = info.split('\n')
        for l in lines:
            if l.startswith('cpu'):
                ll = self.del_more_space(l)
                i = int(ll[1]) + int(ll[2]) + int(ll[3]) + int(ll[4]) + int(ll[5]) + int(ll[6]) + int(ll[7])
                return i, int(ll[4])

    def disk_use_data(self, info: str) -> int:
        lines = info.split('\n')
        for l in lines:
            if l.endswith('/'):
                ll = self.del_more_space(l)
                if len(ll[4]) == 3:
                    return int(ll[4][0:2])
                elif len(ll[4]) == 2:
                    return int(ll[4][0:1])
                elif len(ll[4]) == 4:
                    return int(ll[4][0:3])

    def mem_use_data(self, info: str) -> int:
        lines = info.split('\n')
        for l in lines:
            if l.startswith('Mem'):
                ll = self.del_more_space(l)
                return int((int(ll[2])) / int(ll[1]) * 100)

    def get_datas(self):
        while True:
            try:
                if self.close_sig == 0:
                    break
                stdin, stdout, stderr = self.conn.exec_command(timeout=10, bufsize=100, command='sudo cat /proc/stat')
                cpuinfo1 = stdout.read().decode('utf8')
                #time.sleep(1)

                stdin, stdout, stderr = self.conn.exec_command(timeout=10, bufsize=100, command='sudo cat /proc/stat')
                cpuinfo2 = stdout.read().decode('utf8')

                stdin, stdout, stderr = self.conn.exec_command(timeout=10, bufsize=100, command='sudo df')
                diskinfo = stdout.read().decode('utf8')

                stdin, stdout, stderr = self.conn.exec_command(timeout=10, bufsize=100, command='sudo free')
                meminfo = stdout.read().decode('utf8')

                # 命令：列出所有doker 容器
                stdin, stdout, stderr = self.conn.exec_command(timeout=10, bufsize=100, command='sudo docker ps -a')
                procinfo = stdout.read().decode('utf8')

                c_u1, c_idle1 = self.cpu_use_data(cpuinfo1)
                c_u2, c_idle2 = self.cpu_use_data(cpuinfo2)
                self.cpu_use = int((1 - (c_idle2 - c_idle1) / (c_u2 - c_u1)) * 100)
                self.mem_use = self.mem_use_data(meminfo)
                self.disk_use = self.disk_use_data(diskinfo)

                self.docker_info = parse_docker_ps_output(procinfo)
                #time.sleep(1)
            except EOFError as e:
                print(f"EOFError: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                print(f"连接已经关闭")

    def disconnect(self):
        self.close_sig = 0
        self.conn.close()


def parse_docker_ps_output(output):
    """
    解析 docker ps 命令的输出，并将其转换为列表。

    :param output: docker ps 命令的输出
    :return: 处理后的输出，每行提取一个字段
    """
    lines = output.split('\n')
    # headers = [header.strip() for header in lines[0].split()]

    # headers = ['CONTAINER_ID', 'IMAGE', 'COMMAND', 'CREAT1', 'CREAT2', 'CREAT3', 'STATUS1', 'STATUS2', 'STATUS3',
    #            'PORT1', 'PORT2', 'NAMES']

    parsed_output = []

    # for line in lines[1:]:
    for line in lines:
        if not line.strip():
            continue
        # fields = line.strip().split()
        # container_info = dict(zip(headers, fields))
        parsed_output.append(line)

    return parsed_output


def process_ps_output(data):
    """
    处理 ps 命令的输出，提取每一行的字段。

    :param data: ps 命令的原始输出
    :return: 处理后的输出，每行提取一个字段
    """
    # 将数据分割成行
    lines = data.split('\n')

    # 获取表头
    header = lines[0].strip().split()

    # 解析数据行
    processes = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = line.split(maxsplit=len(header) - 1)
        process = dict(zip(header, values))
        processes.append(process)

    return processes

def parse_docker_ps_output(output):
    """
    解析 docker ps 命令的输出，并将其转换为列表。

    :param output: docker ps 命令的输出
    :return: 处理后的输出，每行提取一个字段
    """
    lines = output.split('\n')
    parsed_output = []
    for line in lines:
        if not line.strip():
            continue
        parsed_output.append(line)
    return parsed_output


def parse_net_dev(output):
    """
    解析网卡流量数据
    :param output:
    :return:
    """
    interface_stats = {}
    lines = output.split('\n')

    for line in lines[2:]:  # 跳过前两行表头
        line = line.strip()
        if not line:
            continue
        interface, stats = line.split(':')
        interface = interface.strip()
        stats = stats.split()

        interface_stats[interface] = {
            'Receive': {
                'bytes': int(stats[0]),
                'packets': int(stats[1]),
                'errs': int(stats[2]),
                'drop': int(stats[3]),
                'fifo': int(stats[4]),
                'frame': int(stats[5]),
                'compressed': int(stats[6]),
                'multicast': int(stats[7]),
            },
            'Transmit': {
                'bytes': int(stats[8]),
                'packets': int(stats[9]),
                'errs': int(stats[10]),
                'drop': int(stats[11]),
                'fifo': int(stats[12]),
                'colls': int(stats[13]),
                'carrier': int(stats[14]),
                'compressed': int(stats[15]),
            }
        }

    return interface_stats


def calculate_speed(prev_data, current_data, interval):
    """
    计算网卡流量
    :param prev_data: 前一次数据
    :param current_data: 当前数据
    :param interval: 间隔时间 秒
    :return: 返回速度
    """
    receive_speed = (current_data['Receive']['bytes'] - prev_data['Receive']['bytes']) / interval
    transmit_speed = (current_data['Transmit']['bytes'] - prev_data['Transmit']['bytes']) / interval
    return receive_speed, transmit_speed


def merge_network_data(data):
    """
    合并所有网卡数据
    :param data:
    :return:
    """
    merged_data = {
        'Receive': {'bytes': 0},
        'Transmit': {'bytes': 0}
    }
    for interface in data.values():
        merged_data['Receive']['bytes'] += interface['Receive']['bytes']
        merged_data['Transmit']['bytes'] += interface['Transmit']['bytes']
    return merged_data


def parse_hostnamectl_output(output):
    """
    系统信息解析
    解析 hostnamectl 命令的输出，并返回字典。
    参数:
    输出(str):来自hostnamectl命令的输出。
    退货:
    dict:包含解析信息的字典。
    """
    result = {}
    lines = output.strip().split('\n')
    for line in lines:
        key_value = line.split(":", 1)
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            result[key] = value

    return result

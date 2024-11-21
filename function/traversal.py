def frpc(server_addr, token, ant_type, local_port, remote_port):
    """
    客户端配置文件
    :param ant_type: 穿透类型
    :param server_addr: 服务端IP地址
    :param token: 认证密钥
    :param local_port: 本地端口
    :param remote_port: 远程端口
    :return:
    """
    return f"""
serverAddr = "{server_addr}"
serverPort = 7000
auth.token = "{token}"

[[proxies]]
name = "ssh01"
type = "{ant_type.lower()}"
localIP = "127.0.0.1"
localPort = {local_port}
remotePort = {remote_port}
    """


def frps(token):
    """
    服务端配置文件
    :param token: 认证密钥
    :return:
    """
    return f"""
bindPort = 7000
auth.token = "{token}"
        """

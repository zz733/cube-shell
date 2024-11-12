def frpc(server_addr, token, local_port, remote_port):
    """
    客户端配置文件
    :param server_addr: 服务端IP地址
    :param token: 认证密钥
    :param local_port: 本地端口
    :param remote_port: 远程端口
    :return:
    """
    return f"""
        serverAddr = {server_addr}
        serverPort = 7000
        auth.token = {token}
        
        [[proxies]]
        name = "ssh01"
        type = "tcp"
        localIP = "127.0.0.1"
        localPort = {local_port}
        remotePort = {remote_port}
    """


def frps(server_addr, token):
    """
    服务端配置文件
    :param server_addr: 服务端IP地址
    :param token: 认证密钥
    :return:
    """
    return f"""
        bind_addr = {server_addr}
        bind_port = 7000
        
        # 认证密钥
        token = {token}
        """

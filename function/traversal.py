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
{tcp(ant_type, local_port, remote_port) if ant_type == "TCP" else http(server_addr, ant_type, local_port)}
    """


def tcp(ant_type, local_port, remote_port):
    return f"""
[[proxies]]
name = "ssh01"
type = "{ant_type.lower()}"
localIP = "127.0.0.1"
localPort = {local_port}
remotePort = {remote_port}
    """


def http(server_addr, ant_type, local_port):
    return f"""
[[proxies]]
name = "web" # 名字随意但是要有
type = "{ant_type.lower()}" # 协议类型
localIP = "127.0.0.1" # 这里可以是自己的127.0.0.1，也可以是自己内网的ip地址
localPort = {local_port}  # 这个端口是你本地准备要映射出去的端口，就是你启动http服务的端口
customDomains = ["{server_addr}"] # 这里可以选择有域名和无域名两种，没有域名填写公网ip即可
    """


def frps(token):
    """
    服务端配置文件
    :param token: 认证密钥
    :return:
    """
    return f"""
bindPort = 7000
vhostHTTPPort = 80
auth.token = "{token}"
        """

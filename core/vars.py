CONF_FILE = "conf/tunnel.json"


class KEYS:
    TUNNEL_TYPE = "tunnel_type"
    BROWSER_OPEN = "browser_open"
    DEVICE_NAME = "device_name"
    SSH_ADDRESS = "ssh_address"
    SSH_PORT = "ssh_port"
    SSH_USERNAME = "ssh_username"
    SSH_PRIVATE_KEY = "ssh_private_key"
    REMOTE_BIND_ADDRESS = "remote_bind_address"
    LOCAL_BIND_ADDRESS = "local_bind_address"


class ICONS:
    TUNNEL = ":icons/tunnel.png"
    START = "icons/start_tunnel.png"
    STOP = "icons/stop_tunnel.png"
    KILL_SSH = ":icons/kill.png"


class CMDS:
    SSH = "ssh"
    SSH_KILL_NIX = "killall ssh"
    SSH_KILL_WIN = "taskkill /im ssh.exe /t /f"

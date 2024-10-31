CONF_FILE = "tunnel.json"


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
    TUNNEL = ":tunnel-diode.png"
    START = ":open.png"
    STOP = ":off.png"
    KILL_SSH = ":on-off.png"


class CMDS:
    SSH = "ssh"
    SSH_KILL_NIX = "killall ssh"
    SSH_KILL_WIN = "taskkill /im ssh.exe /t /f"

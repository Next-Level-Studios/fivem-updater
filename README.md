# updatefivem

A terminal CLI for updating FiveM Linux artifacts and managing a tmux-backed systemd service.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
updatefivem --help
```

## Production install

Recommended system venv install:

```bash
sudo apt update
sudo apt install -y python3 python3-venv tmux
sudo mkdir -p /opt/updatefivem
sudo python3 -m venv /opt/updatefivem/venv
sudo /opt/updatefivem/venv/bin/pip install /path/to/updatefivem
sudo ln -sf /opt/updatefivem/venv/bin/updatefivem /usr/local/bin/updatefivem
```

First-run config:

```bash
sudo updatefivem config
```

During config setup you can keep the config inside the server directory, or
point at a separate directory and filename. Examples:

```bash
# Config inside the FiveM server directory
sudo updatefivem config --server-dir /opt/fivem/server --config-dir configs/live --config-file production.cfg

# Config outside the FiveM server directory
sudo updatefivem config --server-dir /opt/fivem/server --config-dir /etc/fivem/configs --config-file production.cfg

# Equivalent one-shot absolute config path
sudo updatefivem config --server-dir /opt/fivem/server --config /etc/fivem/configs/production.cfg
```

Check selected artifact:

```bash
updatefivem --check
```

Update artifacts:

```bash
sudo updatefivem
```

Install and start service:

```bash
sudo updatefivem service install
sudo systemctl enable --now fivem
```

Open console:

```bash
updatefivem console
```

Detach without stopping server: press `Ctrl+B`, then `D`.

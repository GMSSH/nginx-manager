# Nginx Manager

A precise and efficient Nginx management tool based on Python and SimpleJRPC. It provides a robust API for installing, managing, and monitoring Nginx servers.

## Features

- **Installation & Version Management**: Support for compiling Nginx from source or installing via package managers (yum/apt).
- **Service Control**: Start, stop, restart, and reload Nginx services.
- **Configuration Management**: View and modify `nginx.conf` and performance settings directly.
- **Status Monitoring**: Real-time checking of Nginx process status, load average, and worker usage.
- **Log Management**: Access access logs and error logs.
- **RPC Interface**: Built on `simplejrpc` for easy integration.

## Project Structure

```
nginx-manager/
├── app/
│   ├── config/         # Configuration files
│   ├── consts/         # Constants (`constant.py`)
│   ├── services/       # Core business logic services
│   │   ├── InstallService.py   # Installation logic
│   │   ├── NginxService.py     # Nginx management logic
│   │   └── VersionService.py   # Version checking
│   └── server.py       # RPC Server definition and routes
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

## Requirements

- Python 3.8+
- `psutil`
- `simplejrpc`

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd nginx-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the RPC server:

```bash
python main.py
```

## API Overview

The server exposes the following RPC methods:

### System & status
- `get_versions`: Get available Nginx versions for installation.
- `get_installed`: Get currently installed Nginx version and path.
- `get_status`: Get Nginx process status (running/stopped).
- `get_loadavg`: Get Nginx resource usage.
- `ping`: Health check.

### Lifecycle Management
- `install_nginx`: Install a specific version of Nginx.
- `uninstall_nginx`: Uninstall Nginx.
- `server_do`: Perform action (`start`, `stop`, `restart`, `reload`).

### Configuration
- `get_config` / `set_config`: Read/Write `nginx.conf`.
- `get_perform_conf` / `set_perform_conf`: Read/Write performance tuning parameters (worker_processes, etc.).


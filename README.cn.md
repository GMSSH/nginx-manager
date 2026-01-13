# Nginx 管理器

基于 Python 和 SimpleJRPC 的精准高效 Nginx 管理工具。它提供了强大的 API，用于安装、管理和监控 Nginx 服务器。

## 功能特性

- **安装与版本管理**：支持源码编译安装或通过包管理器 (yum/apt) 安装 Nginx。
- **服务控制**：启动、停止、重启和重载 Nginx 服务。
- **配置管理**：直接查看和修改 `nginx.conf` 及性能设置。
- **状态监控**：实时检查 Nginx 进程状态、负载平均值和 Worker 使用情况。
- **日志管理**：查看访问日志和错误日志。
- **RPC 接口**：基于 `simplejrpc` 构建，易于集成。

## 项目结构

```
nginx-manager/
├── app/
│   ├── config/         # 配置文件
│   ├── consts/         # 常量定义 (`constant.py`)
│   ├── services/       # 核心业务逻辑服务
│   │   ├── InstallService.py   # 安装逻辑
│   │   ├── NginxService.py     # Nginx 管理逻辑
│   │   └── VersionService.py   # 版本检测
│   └── server.py       # RPC 服务器定义及路由
├── main.py             # 程序入口
└── requirements.txt    # Python 依赖
```

## 环境要求

- Python 3.8+
- `psutil`
- `simplejrpc`

## 安装说明

1. **克隆仓库：**
   ```bash
   git clone <repository_url>
   cd nginx-manager
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

## 使用指南

启动 RPC 服务器：

```bash
python main.py
```

## API 概览

服务器暴露了以下 RPC 方法：

### 系统与状态
- `get_versions`：获取可供安装的 Nginx 版本。
- `get_installed`：获取当前安装的 Nginx 版本和路径。
- `get_status`：获取 Nginx 进程状态（运行中/已停止）。
- `get_loadavg`：获取 Nginx 资源使用情况。
- `ping`：健康检查。

### 生命周期管理
- `install_nginx`：安装指定版本的 Nginx。
- `uninstall_nginx`：卸载 Nginx。
- `server_do`：执行操作（`start`、`stop`、`restart`、`reload`）。

### 配置
- `get_config` / `set_config`：读/写 `nginx.conf`。
- `get_perform_conf` / `set_perform_conf`：读/写性能调优参数（worker_processes 等）。



#!/usr/bin/env bash

#卸载极速安装的nginx
set -e

echo "==> 停止任何正在运行的 nginx 进程"
if pidof nginx >/dev/null 2>&1; then
    pkill -9 nginx || true
    sleep 1
fi

# 1) 包管理器卸载
if command -v yum >/dev/null 2>&1; then
    if yum list installed nginx >/dev/null 2>&1; then
        echo "==> 检测到 yum 安装的 nginx，开始卸载"
        yum remove -y nginx || true
    fi
elif command -v apt-get >/dev/null 2>&1; then
    if dpkg -l | grep -qw nginx; then
        echo "==> 检测到 apt 安装的 Redis，开始卸载"
        apt-get remove -y nginx || true
        apt-get purge -y nginx || true
    fi
fi

# 3) 清理服务脚本 & 配置 & 数据目录
echo "==> 清理 init/systemd 脚本和配置/数据目录"

# 删除配置文件
sudo rm -rf /etc/nginx || true
sudo rm -rf /etc/nginx.conf || true

# 删除日志文件
sudo rm -rf /var/log/nginx* || true

# 删除 Nginx 可执行文件（如果存在）
sudo rm -f /usr/sbin/nginx || true
sudo rm -f /usr/local/nginx/sbin/nginx || true

echo "==> nginx 已完全卸载"
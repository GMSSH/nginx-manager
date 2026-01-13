import os

APP_NAME = 'official/nginx'
APP = 'nginx'
BASE_APP_PATH = '/.__gmssh/plugin/official/nginx/'
PID_FILE = BASE_APP_PATH + "data/pid"

NGINX_CONF_PATH = BASE_APP_PATH + 'config/'
SOCK_FILE = BASE_APP_PATH + 'tmp/app.sock'

INSTALL_SCRIPT = "install_server.sh"
PACKAGE_UNINSTALL_SCRIPT = "uninstall_package_server.sh"

# 受管理的nginx临时存储文件。
INSTALL_INFO_FILE = BASE_APP_PATH + 'data/nginx_info.json'

PHPFPM_STATUS_CONF_PATH = "/www/server/panel/vhost/nginx/phpfpm_status.conf"

APT_SOURCE = "apt"
YUM_SOURCE = "yum"


SET_VERSION_AUTO = 'auto'
SET_VERSION_MANUAL = 'manual'

def mkdir_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

BASE_PATH = "/.__gmssh"
PLUGIN_PATH = os.path.join(BASE_PATH, "plugin")
APP_BASE_PATH = os.path.join(PLUGIN_PATH, APP_NAME)
APP_DATA_PATH = mkdir_dir(os.path.join(APP_BASE_PATH, "data"))
APP_LOGS_PATH = mkdir_dir(os.path.join(APP_BASE_PATH, "logs"))
APP_TMP_PATH = mkdir_dir(os.path.join(APP_BASE_PATH, "tmp"))
APP_INFO_FILE_PATH = os.path.join(APP_TMP_PATH, "info_file")
APP_INSTALL_LOGS_FILE_PATH = os.path.join(APP_LOGS_PATH, "app_version.log")


INSTALL_COMPILE = "compile"
INSTALL_PACKAGE = "package"
INSTALL_MANUAL = "manual"


FIND_NGINX_MASTER  = '''#!/bin/bash
TARGET_PATH="{}"

PIDS=$(pgrep -f "nginx")

for pid in $PIDS; do
    EXE_PATH=$(readlink -f /proc/"$pid"/exe 2>/dev/null)
    if [[ "$EXE_PATH" == "$TARGET_PATH" ]]; then
        echo "$pid"
        exit 0
    fi
done

echo "NONE"
exit 1
'''

NGINX_COMPILE_CMD_PATH = "/etc/init.d/nginx"

NGINX_STOP = "{} -s stop"
NGINX_RELOAD = "{} -s reload"

CHECK_STATUS_CONF = """server {
                    listen 80;
                    server_name 127.0.0.1;
                    allow 127.0.0.1;
                    location /nginx_status {
                        stub_status on;
                        access_log off;
                    }
                    }"""


NGINX_DATA_WORKER = "ps aux|grep nginx|grep 'worker process'|wc -l"
NGINX_DATA_WORKER_MAN = "ps aux|grep nginx|grep 'worker process'|awk '{memsum+=$6};END {print memsum}'"
CURL_NGINX_STATUS = "curl http://127.0.0.1/nginx_status"
KKMMGG = r"%s\s+[^kKmMgG\;\n]+"
PROXY_DESCRIPTIONS = ["CONST_NGINX_PROXY_INFO"]
PROXY_EXPRESSIONS = [(r"(client_body_buffer_size)\s+(\w+)", "client_body_buffer_size")]
CONFIG_DESCRIPTIONS = [
    "CONST_NGINX_WORKER_PROCESSES",
    "CONST_NGINX_WORKER_CONNECTIONS",
    "CONST_NGINX_KEEPALIVE_TIMEOUT",
    "CONST_NGINX_GZIP",
    "CONST_NGINX_GZIP_MIN_LENGTH",
    "CONST_NGINX_GZIP_COMP_LEVEL",
    "CONST_NGINX_CLIENT_MAX_BODY_SIZE",
    "CONST_NGINX_SERVER_NAMES_HASH_BUCKET_SIZE",
    "CONST_NGINX_CLIENT_HEADER_BUFFER_SIZE",
    "CONST_NGINX_PROXY_INFO",
]

EXPRESSIONS = [
    (r"(worker_processes)\s+(\w+)", "worker_processes"),
    (r"(worker_connections)\s+(\w+)", "worker_connections"),
    (r"(keepalive_timeout)\s+(\w+)", "keepalive_timeout"),
    (r"(gzip)\s+(\w+)", "gzip"),
    (r"(gzip_min_length)\s+(\w+)", "gzip_min_length"),
    (r"(gzip_comp_level)\s+(\w+)", "gzip_comp_level"),
    (r"(client_max_body_size)\s+(\w+)", "client_max_body_size"),
    (r"(server_names_hash_bucket_size)\s+(\w+)", "server_names_hash_bucket_size"),
    (r"(client_header_buffer_size)\s+(\w+)", "client_header_buffer_size"),
]
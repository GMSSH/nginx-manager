
import os
import re

from simplejrpc import RPCException
from app.consts import constant
from app.utils import helper
from pathlib import Path
from simplejrpc.i18n import T as i18n


def parse_nginx_config(config_path,regex):
    if not os.path.exists(config_path):
        raise RPCException(i18n.translate("LOGIC_NGINX_V2_TM"))
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue  # 跳过空行和注释
        match = re.search(regex, line)
        if match:
            return match
    return []
def match_config_value(config_path, key,match):
    if not os.path.exists(config_path):
        raise RPCException(i18n.translate("LOGIC_NGINX_V2_TM"))
    content = helper.read_file(config_path)
    config_list = []
    unitrep = "[kmgKMG]"
    for description, expression in zip(key, match):
        description = i18n.translate(description)
        key = expression[1]
        result = re.search(expression[0], content)
        if not result:
            value = ""
        else:
            value = result.group(2)
        unit = ""
        psst = description
        if re.search(unitrep, value):
            unit = str.upper(value[-1])
            value = value[:-1]
            psst = unit + ("B，" if len(unit) == 1 else "，") + description
        kv = {"name": key, "value": value, "unit": unit, "ps": psst}
        config_list.append(kv)
    return config_list

def recovery_conf(config_path) -> None:
    """还原配置文件
    :return: None
    """
    dir = os.path.dirname(config_path)
    bak_file = os.path.join(dir, "nginx.conf.back")
    helper.exec_shell(f"cp -f {bak_file} {config_path}")

def backup_conf(config_path):
    """将配置文件进行备份
    :return: None
    """
    ##获取配置文件的路径
    dir = os.path.dirname(config_path)
    bak_file = os.path.join(dir, "nginx.conf.back")
    helper.exec_shell(f"cp -f {config_path} {bak_file}")

def data_integration(tmp, worker, process_cpu, workermen) -> dict[str, str]:
    """将获取到的信息整合到一起
    :param tmp: 临时列表
    :param worker: worker进程数
    :param process_cpu: 进程cpu占用
    :param workermen: worker内存占用
    :return: 整合好的信息
    :rtype: dict
    """
    data = {}
    if "request_time" in tmp:
        data["accepts"] = tmp[8]
        data["handled"] = tmp[9]
        data["requests"] = tmp[10]
        data["Reading"] = tmp[13]
        data["Writing"] = tmp[15]
        data["Waiting"] = tmp[17]
    else:
        data["accepts"] = tmp[9]
        data["handled"] = tmp[7]
        data["requests"] = tmp[8]
        data["Reading"] = tmp[11]
        data["Writing"] = tmp[13]
        data["Waiting"] = tmp[15]
    data["active"] = tmp[2]
    data["worker"] = worker
    data["workercpu"] = round(float(process_cpu["nginx"]), 2)
    data["workermen"] = "%s%s" % (int(workermen), "MB")
    return data

def get_install_script(script):
    base_dir = os.path.dirname(os.path.abspath(__file__))
            # 往上两级回到项目根
    project_root = os.path.dirname(os.path.dirname(base_dir))
    script_path = os.path.join(project_root, script)
    if not os.path.isfile(script_path):
        raise RPCException(i18n.translate_ctx("ERR_SCRIPT_NOT_FOUND", script_path))
    return script_path

async def check_nginx(bin_path: str, config_path: str) -> str:
    """
    校验用户输入的Nginx可执行文件和配置文件是否有效

    Args:
        bin_path: Nginx可执行文件路径
        config_path: Nginx配置文件路径
    """

    # 1. 校验可执行文件
    if not os.path.exists(bin_path):
       # result["bin_error"] = f"可执行文件不存在: {bin_path}"
        return i18n.translate("NGINX_BIN_FILE_NOT_EXIST")

    if not os.access(bin_path, os.X_OK):
        return i18n.translate("NGINX_BIN_FILE_NOT_PERMISSION")

    # 测试执行nginx -v
    try:
        output, err = await helper.async_exec_shell(f"{bin_path} -v 2>&1")
        if "nginx version:" not in output and "nginx version:" not in err:
            return i18n.translate("NGINX_BIN_FILE_INVALID")
    except Exception as e:
        return i18n.translate("NGINX_BIN_FILE_INVALID")

    # 2. 校验配置文件
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        return i18n.translate("NGINX_CONF_FILE_NOT_EXIST")
    # 测试配置文件语法
    try:
        test_cmd = f"{bin_path} -t -c {config_path} 2>&1"
        output, err = await helper.async_exec_shell(test_cmd)

        if "test is successful" not in output and "test is successful" not in err:
            return i18n.translate("NGINX_CONF_FILE_INVALID")
    except Exception as e:
        return i18n.translate("NGINX_CONF_FILE_INVALID")

    return ''
async def get_nginx_version(nginx_path):
    # 2. 获取版本信息
    version_output, version_err = await helper.async_exec_shell(f"{nginx_path} -v 2>&1")

    # 3. 处理版本输出（兼容Tengine等特殊情况）
    version_lines = version_err.splitlines() if version_err else version_output.splitlines()
    nginx_version = None

    for line in version_lines:
        if "nginx version:" in line:
            # 提取版本号部分
            version_str = line.split(":")[-1].strip()
            if "(nginx/" in version_str:
                version_str = version_str.split("(nginx/")[-1].rstrip(")")

            # 提取纯数字版本（格式为 X.X.X）
            if "/" in version_str:
                version_str = version_str.split("/")[-1]

                # 确保只包含数字和点号
            return "".join(filter(lambda c: c.isdigit() or c == '.', version_str))
    return  ''

def single_cmd_raise_error(cmd_string: str, error_cmd: str = "exit 2") -> str:
        """
        生成一个条件执行命令的字符串
        :param cmd_string: 要执行的主命令
        :param error_cmd: 当主命令失败时要执行的命令，默认为"exit 2"
        :return: 生成的完整条件命令字符串
        """
        return f"""
    if ! {cmd_string}
    then 
        {error_cmd}
    fi 
    """

async def get_install_nginx():
    """
    获取系统已安装的Nginx信息（路径、版本和配置文件路径）
    Returns:
        dict: 包含安装路径、版本和配置文件路径的字典
    """
    # 1. 获取nginx安装路径
    path_output, path_err = await helper.async_exec_shell("command -v nginx || which nginx")
    nginx_path = path_output.strip() if path_output else None

    if not nginx_path:
        return {"path": None, "version": None, "config_path": None}

    #如果nginx是一个软链接，找到真实的路径
    if os.path.islink(nginx_path):
        nginx_path = str(Path(nginx_path).resolve());


    nginx_version = await get_nginx_version(nginx_path)
    # 4. 获取配置文件路径
    config_path = None
    try:
        # 使用nginx -t测试配置并获取实际使用的配置文件
        test_output, test_err = await helper.async_exec_shell(f"{nginx_path} -t 2>&1")
        output_lines = test_err.splitlines() if test_err else test_output.splitlines()

        for line in output_lines:
            # 匹配两种可能的输出格式
            if "configuration file" in line:
                parts = line.split("configuration file")
                if len(parts) > 1:
                    # 提取路径部分并清除后续描述
                    config_path = parts[1].split()[0].strip()
                    break

        # 如果仍未找到，尝试常见默认路径
        if not os.path.exists(config_path):
            config_path = ""
    except Exception:
        config_path = None

    return {
        "version": nginx_version,
        "bin_path": nginx_path,
        "config_path": config_path,
        "install_type": constant.INSTALL_MANUAL
    }


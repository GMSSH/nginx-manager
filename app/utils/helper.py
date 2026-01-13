# cython: language_level=3
# -*- encoding: utf-8 -*-
"""
@文件        :helpers.py
@说明        :
@时间        :2024/01/19 13:35:24
@作者        :Zack
@版本        :1.0
@Description: Methods common to both internal and external plugins
"""

import os
import pwd
import asyncio
import hashlib
import tempfile
import json
import psutil
from pathlib import Path

from app.utils import process


async def get_yum_app_version(app_name):
    """ 获取yum可以安装的redis版本"""
    versions = []
    try:
        # 处理输出，按行分割
        yumCmd = 'yum list available --showduplicates ' + app_name
        output, err = await async_exec_shell(yumCmd)
        if err != "":
            return versions
        # 获取版本信息的行，跳过表头
        for line in output.splitlines()[1:]:  # 跳过表头
            if not line.startswith(app_name +"."):
                continue
            parts = line.split()
            if len(parts) >= 2:
                package_version = parts[1].strip();
                versions.append({
                    "name": app_name +'-'+ package_version,
                    "version": app_name + '-' + package_version,
                })
        return versions
    except Exception as e:
        return versions

async def get_apt_app_version(app_name):
    versions = []
    try:
        aptCmd = 'apt-cache madison ' + app_name
        output, err = await async_exec_shell(aptCmd)
        if err:
            return versions
        # 用于去重的集合
        seen_versions = set()
        for line in output.splitlines():
            parts = line.split('|')
            if len(parts) < 3:
                continue
            # 提取版本号，去掉前缀如 5:
            version_str = parts[1].strip()
            # 避免重复添加相同版本
            if version_str not in seen_versions:
                seen_versions.add(version_str)
                versions.append({
                      "name": f"{app_name}-{version_str}",
                    "version": version_str})
        return versions
    except Exception:
        return versions

def is_process_exists_by_exe(bin_path):
    """
    根据执行文件路径查找进程是否存在
    """
    if isinstance(bin_path, str):
        bin_path = [bin_path]
    if not isinstance(bin_path, list):
        return False
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            _exe_bin = p.exe()
            for _e in bin_path:
                if _exe_bin.find(_e) != -1:
                    return True
        except Exception as e:
            continue
    return False

def get_pre_exec_fn(run_user):
    """
    获取指定执行用户的预处理函数
    """
    pid = pwd.getpwnam(run_user)
    uid = pid.pw_uid
    gid = pid.pw_gid

    def _exec_rn():
        os.setgid(gid)
        os.setuid(uid)

    return _exec_rn

async def async_exec_shell(cmd_string, timeout=None, shell=True, cwd=None, env=None, user=None):
    """
    异步执行命令
    @param cmd_string: 命令字符串
    @param timeout: 超时时间（秒）
    @param shell: 是否通过 shell 运行
    @param cwd: 工作目录
    @param env: 环境变量（dict）
    @param user: 用户名（可选，仅限 Unix）
    @return: (stdout, stderr)
    """
    pre_exec_fn = None
    tmp_dir = "/dev/shm"
    if user:
        pre_exec_fn = get_pre_exec_fn(user)
        tmp_dir = "/tmp"

    rx = md5(cmd_string.encode("utf-8"))

    try:
        success_f = tempfile.NamedTemporaryFile(
            mode="w+b",
            suffix="_success",
            # prefix=f"b_tex_{rx}",
            # dir=tmp_dir,
            delete=False
        )
        error_f = tempfile.NamedTemporaryFile(
            mode="w+b",
            suffix="_error",
            # prefix=f"b_tex_{rx}",
            # dir=tmp_dir,
            delete=False
        )

        process = await asyncio.create_subprocess_shell(
            cmd_string,
            stdout=success_f,
            stderr=error_f,
            shell=shell,
            cwd=cwd,
            env=env,
            preexec_fn=pre_exec_fn,
        )

        try:
            await asyncio.wait_for(process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return "", "Timed out"

        success_f.seek(0)
        error_f.seek(0)
        a = success_f.read()
        e = error_f.read()

        success_f.close()
        error_f.close()

    except Exception as e:
        return "", process.get_error_info()

    try:
        if isinstance(a, bytes):
            a = a.decode("utf-8")
        if isinstance(e, bytes):
            e = e.decode("utf-8")
    except Exception as e:
        a = str(a)
        e = str(e)

    return a, e

def md5(s: bytes) -> str:
    return hashlib.md5(s).hexdigest()

def write_json(filename, data, auto_create=False, auth_create_type="{}") -> bool:
    """
    写入 json 文件
    :param auth_create_type:
    :param auto_create:
    :param filename:
    :param data:
    :return:
    """
    import json

    if auto_create and not os.path.exists(filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        write_file(filename, auth_create_type)
    return write_file(filename, json.dumps(data))


async def long_cmd_bash(
        cmd_string: str,
        auto_run=False,
        start_msg: str = "",
        end_msg: str = "",
        close_type: int = 0,
        emit_type: str = "emitApp",
        app_name: str = "",
        operation_type: str = "flushed",
        title: str = ""
):
    """
    将长命令转换为xx.sh 文件，返回 bash xx.sh
    :param operation_type: 操作类型，默认是:flushed(刷新)
    :param emit_type: 默认是刷新应用：emitApp
    :param app_name: 要刷新的应用名称
    :param cmd_string: 要执行的命令
    :param auto_run: 执行完成是否需要执行关闭操作
    :param start_msg: 执行操作之前的提示
    :param end_msg: 执行操作之后的操作
    :param close_type: 操作类型，默认是刷新
    :param title: 设置终端窗口的弹窗
    :return:
    """
    home = Path.home()
    tmp_dir = os.path.join(home, ".gmb", "tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    rx = md5(cmd_string.encode("utf-8"))
    tmp_file = os.path.join(tmp_dir, f"b_tex_{rx}.sh")
    # gmc开始执行
    gmc_start_data = json.dumps({"type": "StartStak"}, ensure_ascii=False)
    cmd_string = f"echo _GMC:'{gmc_start_data}' \n{cmd_string}\n"

    if start_msg:
        cmd_string = f"echo {start_msg}\n" + cmd_string

    if end_msg:
        cmd_string += f"echo {end_msg}\n"

    gmc_data = {"type": emit_type, "data": {"app_name": app_name, "type": operation_type}}
    cmd_string += f"echo _GMC:'{json.dumps(gmc_data, ensure_ascii=False)}' \n"

    if close_type == 1:
        cmd_string += "\necho 'Press Enter to exit...'\n"

    # gmc结束执行
    gmc_end_data = json.dumps({"type": "EndStak"}, ensure_ascii=False)
    cmd_string += f"echo _GMC:'{gmc_end_data}' \n"

    # 执行完成gmc删除生成的sh文件
    cmd_string += f"rm -rf {tmp_file}"

    # 配置cleanup函数，异常也触发EndStak
    cleanup = f"""cleanup() {{
    echo _GMC:'{gmc_end_data}' \n
    echo _GMC:'{json.dumps(gmc_data, ensure_ascii=False)}' \n
    }}
    trap cleanup EXIT
    """
    cmd_string = cleanup + cmd_string
    # 设置终端窗口标题
    if title:
        gmc_set_title = {"type": "updateTitle", "data": title}
        cmd_string = f"echo _GMC:'{json.dumps(gmc_set_title, ensure_ascii=False)}' \n" + cmd_string

    write_file(tmp_file, cmd_string, file_mode="700")
    res_string = f"sudo  bash {tmp_file}"

    if auto_run:
        # 回车关闭
        if close_type == 1:
            return f"{res_string} && exit"
        # 直接关闭
        elif close_type == 2:
            return f"{res_string} && sleep 1 && exit\n"
        else:
            return f"{res_string}"

    return res_string

def write_file(filename, s_body, mode="w+", file_mode="", user="", encoding="utf-8") -> bool:
    """
    写入文件内容
    @filename 文件名
    @s_body 欲写入的内容
    return bool 若文件不存在则尝试自动创建
    """
    try:
        with open(filename, mode, encoding=encoding) as fp:
            fp.write(s_body)
        return _write_file(file_mode, filename, user)
    except Exception as e:
        try:
            with open(filename, mode, encoding=encoding) as fp:
                fp.write(s_body)
            return _write_file(file_mode, filename, user)
        except Exception as e:
            return False


def _write_file(file_mode, filename, user):
    """ """
    if file_mode:
        exec_shell(f"chmod {file_mode} {filename}")
    if user:
        exec_shell(f"chown {user}:{user} {filename}")
    return True


def exec_shell(cmd_string, timeout=None, shell=True, cwd=None, env=None, user=None):
    """
    @name 执行命令
    @param cmd_string 命令 [必传]
    @param timeout 超时时间
    @param shell 是否通过shell运行
    @param cwd 进入的目录
    @param env 环境变量
    @param user 执行用户名
    @return 命令执行结果
    """
    return process.exec_shell(
        cmd_string=cmd_string,
        timeout=timeout,
        shell=shell,
        cwd=cwd,
        env=env,
        user=user,
    )





def read_json(filename, auto_create=False, auth_create_type="{}"):
    """
    读取 json 文件
    :param auth_create_type:
    :param auto_create:
    :param filename:
    :return:
    """
    import json

    if auto_create and not os.path.exists(filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        write_file(filename, auth_create_type)
    contents = read_file(filename)
    return [] if contents == "" else json.loads(contents)

def is_process_exists_by_exe(bin_path):
    """
    根据执行文件路径查找进程是否存在
    """
    if isinstance(bin_path, str):
        bin_path = [bin_path]
    if not isinstance(bin_path, list):
        return False
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            _exe_bin = p.exe()
            for _e in bin_path:
                if _exe_bin.find(_e) != -1:
                    return True
        except Exception as e:
            continue
    return False

def read_file(filename, mode="r") -> str:
    """
    读取文件内容
    @filename 文件名
    return string(bin) 若文件不存在，则返回False
    """
    import os

    if not os.path.exists(filename):
        return ""
    fp = None
    try:
        fp = open(filename, mode)
        f_body = fp.read()
    except Exception as e:
        try:
            fp = open(filename, mode, encoding="utf-8", errors="ignore")
            f_body = fp.read()
        except Exception as e:
            fp = open(filename, mode, encoding="GBK", errors="ignore")
            f_body = fp.read()
    finally:
        if fp and not fp.closed:
            fp.close()
    return f_body


def async_run(cmd_string: str):
    """
    异步执行命令
    """
    exec_shell(f"nohup {cmd_string} &")




def bool_to_int(b):
    """
    bool转int
    :param b:
    :return:
    """
    return 1 if b else 0


def check_command_exists(command):
    """
    执行which命令检查命令是否存在
    :param command:
    :return:
    """
    return process.check_command_exists(command)


def ensure_file(path: str) -> None:
    """
    确保给定的文件存在：如果父目录不存在，就先创建目录；
    如果文件不存在，就创建一个空文件。
    """
    # 确保父目录存在
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)

    # 如果文件不存在，就创建一个空文件
    if not os.path.isfile(path):
        with open(path, 'a'):
            pass



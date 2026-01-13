# -*- encoding: utf-8 -*-
"""
@文件        :command.py
@说明        :
@时间        :2024/06/11 17:31:38
@作者        :Zack
@版本        :1.0
"""

import os
import time



def get_pre_exec_fn(run_user):
    """
    @name 获取指定执行用户预处理函数
    @param run_user<string> 运行用户
    @return 预处理函数
    """
    import pwd

    pid = pwd.getpwnam(run_user)
    uid = pid.pw_uid
    gid = pid.pw_gid

    def _exec_rn():
        os.setgid(gid)
        os.setuid(uid)

    return _exec_rn


def md5(strings):
    """
    @name 生成MD5
    @param strings 要被处理的字符串
    @return string(32)
    """
    if type(strings) != bytes:
        strings = strings.encode()
    import hashlib

    m = hashlib.md5()
    m.update(strings)
    return m.hexdigest()

def get_error_info():
    """ """
    import traceback

    return traceback.format_exc()



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
    import subprocess
    import tempfile

    pre_exec_fn = None
    tmp_dir = "/dev/shm"
    if user:
        pre_exec_fn = get_pre_exec_fn(user)
        tmp_dir = "/tmp"
    try:
        rx = md5(cmd_string.encode("utf-8"))
        success_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode="wb+",
            suffix="_success",
            prefix=f"b_tex_{rx}",
            dir=tmp_dir,
        )
        error_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode="wb+",
            suffix="_error",
            prefix=f"b_tex_{rx}",
            dir=tmp_dir,
        )
        sub = subprocess.Popen(
            cmd_string,
            close_fds=True,
            shell=shell,
            bufsize=128,
            stdout=success_f,
            stderr=error_f,
            cwd=cwd,
            env=env,
            preexec_fn=pre_exec_fn,
        )
        if timeout:
            s = 0
            d = 0.01
            while sub.poll() is None:
                time.sleep(d)
                s += d
                if s >= timeout:
                    if not error_f.closed:
                        error_f.close()
                    if not success_f.closed:
                        success_f.close()
                    return "", "Timed out"
        else:
            sub.wait()

        error_f.seek(0)
        success_f.seek(0)
        a = success_f.read()
        e = error_f.read()
        if not error_f.closed:
            error_f.close()
        if not success_f.closed:
            success_f.close()
    except Exception as e:
        return "", get_error_info()
    try:
        # 编码修正
        if type(a) == bytes:
            a = a.decode("utf-8")
        if type(e) == bytes:
            e = e.decode("utf-8")
    except Exception as e:
        a = str(a)
        e = str(e)

    return a, e


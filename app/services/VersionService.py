## 对nginx安装版本
import os
import shutil

from simplejrpc import i18n

from app.utils import helper
from app.utils import  utils
from app.consts import constant
from simplejrpc.exceptions import RPCException


class VersionService:
    def __init__(self):
        self.compile_versions =helper.read_json(constant.NGINX_CONF_PATH + 'version.json')

    async def _get_extreme_speed_version(self):
        """ """
        if shutil.which(constant.APT_SOURCE):
            return await helper.get_apt_app_version(constant.APP)
        elif shutil.which(constant.YUM_SOURCE):
            return await helper.get_yum_app_version(constant.APP)
        else:
            return []

    async def get_version_versions(self):
        return {
            "compile_version": self.compile_versions,
            "package_version": await self._get_extreme_speed_version()
        }

    async def tail_log(self):
        """ 实时查看日志 """
        # if not os.path.exists(constant.APP_INFO_FILE_PATH):
        #     return i18n.translate("NG_ERR_TEMPLATE_V6")
        if not os.path.exists(constant.APP_INSTALL_LOGS_FILE_PATH):
            return i18n.translate("NG_ERR_TEMPLATE_V6")

        raise RPCException(data=f"tail -f {constant.APP_INSTALL_LOGS_FILE_PATH}\n", code=206,
                           message=i18n.translate("STATUS_OK"))


    async def kill_process(self):
        """ 杀掉 redis 进程 """
        redis_info = helper.read_file(constant.APP_INFO_FILE_PATH)
        if not redis_info:
            return False

        try:
            pid, md5_command = redis_info.strip().split("_")
        except ValueError:
            return False

        if not pid.isdigit():
            return False

        # server_pid = helper.read_file(constant.PID_FILE)
        # if not server_pid or not server_pid.strip().isdigit():
        #     return False

        # 拼接完整的 shell 脚本命令
        kill_cmd = f"""#!/bin/bash
    kill_tree() {{
      local _pid=$1
      local _exclude=$2
      if [[ "$_pid" == "$_exclude" ]]; then
        return
      fi
      for _child in $(pgrep -P "$_pid"); do
        kill_tree "$_child" "$_exclude"
      done
      kill -TERM "$_pid" 2>/dev/null
    }}

    kill_tree "{pid}" "{os.getpid()}"
    """

        await helper.async_exec_shell(kill_cmd)
        return True

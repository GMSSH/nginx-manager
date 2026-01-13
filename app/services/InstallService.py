import os
import shutil
from simplejrpc import i18n, RPCException

from app.consts import constant
from app.services.NginxService import NginxService
from app.utils import helper, utils
from pathlib import Path


nginx_service = NginxService()

class InstallService:

    def __init__(self):
        version_data =helper.read_json(constant.NGINX_CONF_PATH + 'version.json')
        data_list = version_data.get('data', [])
        self.versions_list = [item.get('version') for item in data_list]

    def check_install(self):
        if not os.path.exists(constant.INSTALL_INFO_FILE):
            raise RPCException(i18n.translate("NGINX_UNSTALLED"))

    """
    安装服务类
    """
    def get_installed(self):
        """
        获取已安装的版本
        :return:
        """
        if not os.path.exists(constant.INSTALL_INFO_FILE):
            return None,None
        info =  helper.read_json(constant.INSTALL_INFO_FILE)
        if not info:
            return None,None
        return info['install_type'], info['bin_path']


    async def set_installed(self, bin_path, config_path, version, set_type):
        """
        设置已安装的版本
        :return:
        """
        input_data = {
            "version":version,
            "bin_path": bin_path,
            "config_path": config_path,
            "install_type": constant.INSTALL_MANUAL
        }
        if  set_type == constant.SET_VERSION_MANUAL:
            check_res = await utils.check_nginx(bin_path, config_path)
            if check_res != '':
                raise RPCException(check_res)
            input_data['version'] = await  utils.get_nginx_version(bin_path)
        else:
            if  input_data['version'] == '':
                raise RPCException(i18n.translate("AUTO_NEED_VERSION"))

        #判断bin是不是快捷方式，拿到真实路径写入
        if os.path.islink(bin_path):
            input_data['input_data'] = str(Path(bin_path).resolve());

        helper.write_json(constant.INSTALL_INFO_FILE, input_data)
        return True


    # 安装nginx
    async def install_nginx(self,install_type,version):
        #先判断data目录在不在，不在就创建
        if not os.path.exists(constant.BASE_APP_PATH + 'data'):
            os.makedirs(constant.BASE_APP_PATH + 'data')
        # 1 编译 2 极速
        match install_type:
            case constant.INSTALL_COMPILE:
                return await self._compile_install(version)
            case constant.INSTALL_PACKAGE:
                return await self._package_install(version)
            case _:
                raise RPCException(i18n.translate("UNSUPPORT_INSTALL_TYPE"))

    # 卸载nginx
    async def uninstall_nginx(self,execute):
        cache = nginx_service.nginx_install_verify()
        bash_cmd = ''
        if cache['install_type'] == constant.INSTALL_COMPILE:
            script_path = utils.get_install_script(constant.INSTALL_SCRIPT);
            # 拼装安装命令
            uninstall_cmd = utils.single_cmd_raise_error(f"bash {script_path} uninstall")
            bash_cmd = await helper.long_cmd_bash(uninstall_cmd, True, i18n.translate("START_UNINSTALL"),
                                                  i18n.translate("END_UNINSTALL"), 3, app_name=constant.APP_NAME,
                                                  title=f"{i18n.translate('UNINSTALL')} Nginx")
           # return bash_cmd
        elif cache['install_type'] == constant.INSTALL_PACKAGE:
            if shutil.which(constant.APT_SOURCE):
                bash_cmd =  utils.single_cmd_raise_error("apt-get remove -y nginx && apt-get purge -y nginx")
            elif shutil.which(constant.YUM_SOURCE):
                bash_cmd = utils.single_cmd_raise_error("yum remove -y nginx")
            else:
                raise RPCException(i18n.translate("UNSUPPORT_INSTALL_TYPE"))
            bash_cmd = await helper.long_cmd_bash(bash_cmd, True, i18n.translate("START_UNINSTALL"),
                                                  i18n.translate("END_UNINSTA"
                                                                 "LL"), 3, app_name=constant.APP_NAME,
                                                  title=f"{i18n.translate('UNINSTALL')} Nginx")
           # return await self.create_backend_tasks(bash_cmd)
        else:
            # 用户手动选择的nginx，不要去卸载
            return ''
        if execute and bash_cmd != '':
            return await self.create_backend_tasks(bash_cmd)
        return bash_cmd



    async def _compile_install(self, version):
        if version not in self.versions_list:
            raise RPCException(i18n.translate("UNSUPPORT_VERSION"))
        script_path = utils.get_install_script(constant.INSTALL_SCRIPT);
        if not os.path.isfile(script_path):
            raise RPCException(i18n.translate_ctx("ERR_SCRIPT_NOT_FOUND", script_path))
        # 拼装安装命令
        install_cmd = f"bash {script_path} install {version}"
        uninstall_cmd = await self._nginx_install_prev()
        steps = []
        if len(uninstall_cmd) != 0:
            steps = uninstall_cmd
        steps.append(install_cmd)
        full_cmd = "\n".join(steps)
        bash_cmd = await helper.long_cmd_bash(full_cmd, True, i18n.translate("START_INSTALL"),
                                               i18n.translate("END_INSTALL"), 3, app_name=constant.APP_NAME,
                                               title=f"{i18n.translate('COMPILE_INSTALL')} Nginx {version}")
        return await self.create_backend_tasks(bash_cmd)

    async def _package_install(self, version):
        bin_path = "/user/sbin/nginx"
        config_path = "/etc/nginx/nginx.conf"
        uninstall_cmd = self._nginx_install_prev()
        if shutil.which(constant.APT_SOURCE):
            install_cmd = ["apt-get update", f"apt-get install -y nginx={version}",
                           '''find /etc/nginx -type f -name "*.dpkg-new" -exec bash -c 'for file; do echo mv -f "$file" "${file%.dpkg-new}"; done' _ {} +''']
        elif shutil.which(constant.YUM_SOURCE):
            install_cmd = [f"yum install -y nginx {version}"]
        else:
            raise RPCException(i18n.translate("UNSUPPORT_OS"))
        write_json = (
            f"cat > {constant.INSTALL_INFO_FILE} <<'EOF'\n"
            f'{{\n'
            f'  "bin_path":"{bin_path}",\n'
            f'  "conf_path":"{config_path}",\n'
            f'  "version":"{version}",\n'
            f'  "install_type":"{constant.INSTALL_PACKAGE}"\n'
            f'}}\n'
            f"EOF"
        )
        start_cmd = f"{bin_path} -c {config_path} "
        steps = []
        if len(uninstall_cmd) != 0:
            steps = uninstall_cmd
        for each_install_cmd in install_cmd:
            steps.append(self._utils.single_cmd_raise_error(each_install_cmd))
        steps.append(self._utils.single_cmd_raise_error(write_json))
        steps.append(self._utils.single_cmd_raise_error(start_cmd))
        full_cmd = "\n".join(steps)

        bash_cmd = await helper.long_cmd_bash(full_cmd, True, i18n.translate("START_INSTALL"),
                                          i18n.translate("END_INSTALL"), 3, app_name=constant.APP_NAME,
                                          title=f"{i18n.translate('COMPILE_INSTALL')} Nginx {version}")
        return await self.create_backend_tasks(bash_cmd)

    #nginx 安装的第一步，需要先卸载历史的，保证nginx能够正常启动
    async def _nginx_install_prev(self):
        install_type, bin_path = self.get_installed();
        if install_type is None:
            return  ''
        pkill_cmd = 'pkill nginx'
        if install_type == constant.INSTALL_MANUAL:
            return [pkill_cmd]

        try:
            cache= nginx_service.nginx_install_verify()
        except Exception as e:
            return [pkill_cmd]
        bash = await self.uninstall_nginx(False)
        return [pkill_cmd, bash]

    async def create_backend_tasks(self, bash_cmd):
        pid = await self.nohub_exec(bash_cmd, constant.APP_INSTALL_LOGS_FILE_PATH)
        if pid == 0:
            raise RPCException(i18n.translate("ERR_TEMPLATE_V15"))
        command = await self.get_process_command(pid)
        if not command:
            raise RPCException(i18n.translate("ERR_TEMPLATE_V16"))
        command_md5 = helper.md5(command.encode("utf-8"))
        res = helper.write_file(constant.APP_INFO_FILE_PATH, f"{pid}_{command_md5}")
        return res

    async def nohub_exec(self, cmd, log_file="/dev/null") -> int:
        """
        使用 nohup 去执行一个命令，返回 nohup 执行的结果。

        :param cmd: 要执行的命令，例如 "ls -al"
        :param log_file: 日志文件路径，默认 /dev/null
        :return: 执行结果 {"pid": 9999, "command": "sleep 600"}，command 为真实运行命令
        """

        # nohup 后台运行并输出 PID
        nohup_cmd = f"nohup {cmd} > {log_file} 2>&1 & echo $!"
        # 执行 nohup 命令并获取 PID
        stdout, err = await helper.async_exec_shell(nohup_cmd)
        if err:
            return 0

        pid_str = stdout.strip()
        if not pid_str.isdigit():
            return 0
        pid = int(pid_str)
        return pid

    async def get_process_command(self, pid):
        # 通过 ps 命令获取该 PID 的真实执行命令
        verify_cmd = f"ps -p {pid} -o cmd="
        real_cmd_stdout, real_cmd_err = await helper.async_exec_shell(verify_cmd)
        if real_cmd_err:
            return ""

        real_cmd = real_cmd_stdout.strip()
        if not real_cmd:
            return ""

        return real_cmd

    async def check_process(self):
        """ 检查redis进程是否存在 """
        if not os.path.exists(constant.APP_INFO_FILE_PATH):
            return False
        res = await self._check_process()
        if not res:
            os.remove(constant.APP_INFO_FILE_PATH)
        return res

    async def _check_process(self):
        """ 检查redis进程是否存在 """
        redis_info = helper.read_file(constant.APP_INFO_FILE_PATH)
        if not redis_info:
            return False
        pid, md5_command = redis_info.split("_")
        if not pid.isdigit():
            return False
        pid = int(pid)
        command = await self.get_process_command(pid)
        if not command:
            return False
        command_md5 = helper.md5(command.encode("utf-8"))
        if command_md5 != md5_command:
            return False
        return True






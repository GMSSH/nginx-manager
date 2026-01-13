# Nginx Server Management Service
import os.path
import psutil
import re
import contextlib
import time

from simplejrpc import RPCException, i18n
from app.consts import constant
from app.utils import utils, helper



class NginxService:
    ...

    # Verify if Nginx is installed
    def nginx_install_verify(self):
        if not os.path.exists(constant.INSTALL_INFO_FILE):
            raise RPCException(i18n.translate("UNINSTALLED_NGINX"))
        cached = helper.read_json(constant.INSTALL_INFO_FILE, True)
        if not cached or not cached.get("bin_path") or not os.path.exists(cached.get("bin_path")):
            raise RPCException(i18n.translate("UNINSTALLED_NGINX"))
        return cached

    # Get installed Nginx version information
    async def get_installed(self):
        # 先获取到管理的配置文件
        cached = helper.read_json(constant.INSTALL_INFO_FILE,True)
        if cached and (not cached.get("bin_path") or not os.path.exists(cached.get("bin_path"))):
            os.remove(constant.INSTALL_INFO_FILE)
        if not cached:
            cached =  await utils.get_install_nginx()
        return cached

    # Get Nginx running status
    async def get_status(self):
        cached = self.nginx_install_verify()
        ng_pid_sh = constant.FIND_NGINX_MASTER.format(cached.get("bin_path"))
        out = await helper.async_exec_shell(ng_pid_sh)
        if  "NONE" in out[0]:
            return {"status": "stop"}
        return {"status": "start", "pid": out[0].replace("\n", "")}

    async def nginx_do(self, action):
        match action:
            case "start":
                 return await self._start_nginx()
            case "stop":
                return await self._stop_nginx()
            case "restart":
                 return await self._restart_nginx()
            case "reload":
                 return await self._reload_nginx()
            case _:
                raise RPCException(i18n.translate("SERVER_DO_FORM"))

    async def _reload_nginx(self):
        if (await self.get_status()["status"]) != "start":
            raise RPCException(i18n.translate("NGINX_NOT_START"))
        cached = self.nginx_install_verify()
        ng_reload_cmd = constant.NGINX_RELOAD.format(cached.get("bin_path"))
        out = await helper.async_exec_shell(ng_reload_cmd)
        if out[0] == "" and out[1] == "":
            return {}
        raise RPCException(i18n.translate("STATUS_FAILED"))

    async def _restart_nginx(self):
        await self._stop_nginx()
        return await self._start_nginx()

    async def _stop_nginx(self):
        cached = self.nginx_install_verify()
        ng_stop_cmd = constant.NGINX_STOP.format(cached.get("bin_path"))
        out = await helper.async_exec_shell(ng_stop_cmd)
        return {}
    async def _start_nginx(self):
        if (await self.get_status())["status"] == "start":
            return {}
        cached = self.nginx_install_verify()
        #nginx如果已经启动了就不操作。
        #如果是编译则使用编译的启动命令
        if cached.get("install_type") == constant.INSTALL_COMPILE:
            out = await helper.async_exec_shell(f"{constant.NGINX_COMPILE_CMD_PATH} start")
        else:
            #直接使用-c命令启动
            out = await helper.async_exec_shell(f"{cached.get('bin_path')} -c {cached.get('config_path')}")
        if out[1] != "":
            ports = self._get_nginx_ports(cached.get('config_path'))
            for port in ports:
                if not self._check_port_with_proc_net_tcp(port):
                    continue
                raise RPCException(i18n.translate("LOGIC_NGINX_V37_TM"))
            raise RPCException(i18n.translate("LOGIC_NGINX_V36_TM"))
        return {}


    # Get Nginx load information
    async def get_loadavg(self):
        self.nginx_install_verify()
        try:
            process_cpu = {}
            worker = int(helper.exec_shell(constant.NGINX_DATA_WORKER)[0]) - 1
            workermen = int(helper.exec_shell(constant.NGINX_DATA_WORKER_MAN)[0]) / 1024
            for proc in psutil.process_iter():
                if proc.name() == "nginx":
                    self._get_process_cpu_percent(proc.pid, process_cpu)
            time.sleep(0.1)
            self._check_status_conf()
            is_curl = True
            tmp = []
            if is_curl:
                result = helper.exec_shell(constant.CURL_NGINX_STATUS)[0]
                tmp = result.split()
            return utils.data_integration(tmp, worker, process_cpu, workermen)
        except Exception as e:
            raise RPCException(i18n.translate("LOGIC_NGINX_V8_TM"))

    def _get_process_cpu_percent(self, i, process_cpu) -> None:
        """Get process CPU usage
        :param i: Process ID
        :param process_cpu: Process CPU usage dictionary
        :return: None
        """
        with contextlib.suppress(Exception):
            pp = psutil.Process(i)
            if pp.name() not in process_cpu.keys():
                process_cpu[pp.name()] = float(pp.cpu_percent(interval=0.01))
            process_cpu[pp.name()] += float(pp.cpu_percent(interval=0.01))

    def _check_status_conf(self):
        """ """
        filename = constant.PHPFPM_STATUS_CONF_PATH
        if os.path.exists(filename):
            if helper.read_file(filename).find("nginx_status") != -1:
                return
        conf = constant.CHECK_STATUS_CONF
        helper.write_file(filename, conf)
        self.nginx_do("reload")

    def _get_nginx_ports(self,config_file=""):
        try:
            with open(config_file, 'r') as file:
                content = file.read()
                return re.findall(r'listen\s+(\d+);', content)
        except FileNotFoundError:
            pass
        return []
    def _check_port_with_proc_net_tcp(self,port):
        # 遍历所有连接
        for conn in psutil.net_connections(kind='inet'):
            if str(conn.laddr.port) == port:
                return True  # 端口被占用
        return False

    def _check_conf(self):
        """Check if the configuration file is correct
        .. code-block:: Shell

            >> nginx -t -c nginx.conf
        :return: True if correct, False otherwise.
        :rtype: tuple(bool, str)
        """
        cached = self.nginx_install_verify()
        result = helper.exec_shell(f"ulimit -n 8192; {cached['bin_path']} -t -c {cached['config_path']}")
        if result[1].find("successful") == -1:
            return False, result[1]
        return True, "ok"

    async def get_nginx_config(self):
        cached = self.nginx_install_verify()
        if not os.path.exists(cached['config_path']):
            raise RPCException(i18n.translate("LOGIC_NGINX_V2_TM"))
        return helper.read_file(cached['config_path'])

    def set_nginx_config(self,config_data):
        cached = self.nginx_install_verify()
        # Backup
        conf_path = cached['config_path']
        if not os.path.exists(conf_path):
            raise RPCException(i18n.translate("LOGIC_NGINX_V2_TM"))
        utils.backup_conf(conf_path)
        helper.write_file(conf_path, config_data)
        status, err = self._check_conf()
        if not status:
            utils.recovery_conf(conf_path)
            raise RPCException(i18n.translate("LOGIC_NGINX_V29_TM"))
        self.nginx_do("reload")
        return True

    async def get_perform_conf(self):
        cached = self.nginx_install_verify()
        if not os.path.exists(cached['config_path']):
            raise RPCException(i18n.translate("LOGIC_NGINX_V2_TM"))
        config_list = utils.match_config_value(cached['config_path'], constant.CONFIG_DESCRIPTIONS, constant.EXPRESSIONS)
        # 获取nginx的proxy
        dir = os.path.dirname(cached['config_path'])
        proxy_path = os.path.join(dir, "proxy.conf")
        if not os.path.exists(proxy_path):
            return config_list
        return config_list + utils.match_config_value(proxy_path, constant.PROXY_DESCRIPTIONS, constant.PROXY_EXPRESSIONS)

    async def set_perform_conf(self, conf_list):
        cached = self.nginx_install_verify()
        conf_file = cached['config_path']
        proxy_file = os.path.join(os.path.dirname(cached['config_path']), "proxy.conf")
        conf_content = helper.read_file(conf_file)
        proxy_content = ''
        if  os.path.exists(proxy_file):
            utils.backup_conf(proxy_file)
            proxy_content = helper.read_file(proxy_file)

        utils.backup_conf(conf_file)
        for c in conf_list:
            """ """
            rep = self._nginx_const.KKMMGG % c["name"]
            if c["name"] == "worker_processes" or c["name"] == "gzip":
                if not re.search(r"auto|on|off|\d+", c["value"]):
                    raise RPCException(i18n.translate("LOGIC_NGINX_V4_TM"))
            else:
                if not re.search(r"\d+", c["value"]):
                    raise RPCException(i18n.translate("LOGIC_NGINX_V5_TM"))
            if re.search(rep, conf_content):
                new_conf = "%s %s" % (c["name"], c["value"])
                conf_content = re.sub(rep, new_conf, conf_content)
            elif proxy_content != '' and re.search(rep, proxy_content):
                new_conf = "%s %s" % (c["name"], c["value"])
                proxy_content = re.sub(rep, new_conf, proxy_content)
        helper.write_file(conf_file, conf_content)
        if proxy_content != '':
            helper.write_file(proxy_file, proxy_content)
        isError, err = self._check_conf()
        if not isError:
            utils.recovery_conf(conf_file)
            if proxy_content != '':
                utils.recovery_conf(conf_file)
            raise RPCException(i18n.translate("LOGIC_NGINX_V15_TM") + err)
        self.nginx_do("reload")
        return True

    async def get_error_log(self):
        install_cache = self.nginx_install_verify()
        #拿到nginx配置文件，获取error_log 路径
        config_file = install_cache['config_path']
        match = utils.parse_nginx_config(config_file,  r"error_log\s+([^;\s]+)\s+([^;]+);")
        if not match:
            raise RPCException(i18n.translate("LOGIC_NGINX_V6_TM"))

        return helper.read_file(match.group(1))


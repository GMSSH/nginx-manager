import os

from simplejrpc.app import ServerApplication
from simplejrpc.response import jsonify

from app.schemas import NginxForm
from app.services.InstallService import InstallService
from app.services.VersionService import VersionService
from app.services.NginxService import NginxService


from app.consts import constant
from simplejrpc.i18n import T as i18n

current_path = os.path.dirname(__file__)
#socket_path = os.path.join(current_path, "tmp.socket")
app = ServerApplication(constant.SOCK_FILE)
version_service = VersionService()
nginx_service = NginxService()
install_service = InstallService()

@app.route(name="get_versions")
async def get_versions(*args,**kwargs):

    res = await version_service.get_version_versions()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="get_installed")
async def check_installed(*args,**kwargs):
    res = await nginx_service.get_installed()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="set_nginx", form=NginxForm.SetInstallForm)
async def set_nginx_install(*args,**kwargs):
    set_type = kwargs.get("set_type")
    bin_path = kwargs.get("bin_path")
    config_path = kwargs.get("config_path")
    version =  kwargs.get("version")
    res = await install_service.set_installed(bin_path, config_path, version, set_type)
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="install_nginx",form=NginxForm.InstallForm)
async def install_nginx(*args,**kwargs):
    install_type = kwargs.get("install_type")
    version = kwargs.get("version")
    res = await install_service.install_nginx(install_type, version)
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="uninstall_nginx")
async def uninstall_nginx(*args,**kwargs):
    res = await install_service.uninstall_nginx(True)
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))


@app.route(name="get_status")
async def get_status(*args,**kwargs):
    res = await nginx_service.get_status()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="server_do",form=NginxForm.ServerDoForm)
async def server_do(*args,**kwargs):
    res = await nginx_service.nginx_do(kwargs.get("action"))
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))


@app.route(name="get_loadavg")
async def get_loadavg(*args,**kwargs):
    res = await nginx_service.get_loadavg()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="get_config")
async def get_conf(*args,**kwargs):
    res = await nginx_service.get_nginx_config()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="set_config")
async def set_conf(*args,**kwargs):
    res = await nginx_service.set_nginx_config(kwargs.get("config_data"))
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="get_perform_conf")
async def get_perform_conf(*args,**kwargs):
    res = await nginx_service.get_perform_conf()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="set_perform_conf")
async def set_perform_conf(*args,**kwargs):
    res = await nginx_service.set_perform_conf(kwargs.get("config_data"))
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="get_error_log")
async def get_error_log(*args,**kwargs):
    res = await nginx_service.get_error_log()
    return jsonify(data=res, msg=i18n.translate("STATUS_OK"))

@app.route(name="tail_log")
async def tail_log(*args, **kwargs):
    """ 使用 tail -f 方式实时获取日志"""
    res_data = await version_service.tail_log()
    return jsonify(data=res_data, msg=i18n.translate("STATUS_OK"))

@app.route(name="kill_process")
async def kill_process(*args, **kwargs):
    """ Kill the Nginx process """
    res_data = await version_service.kill_process()
    return jsonify(data=res_data, msg=i18n.translate("STATUS_OK"))

@app.route(name="check_process")
async def check_process(*args, **kwargs):
    """ Check if Nginx installation process exists """
    res_data = await install_service.check_process()
    return jsonify(data=res_data, msg=i18n.translate("STATUS_OK"))

# 状态检查接口
@app.route(name="ping")
async def ping(**kwargs):
    """ """
    return jsonify(data="pong", msg=i18n.translate("STATUS_OK"))
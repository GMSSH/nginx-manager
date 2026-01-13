import os
from typing import Type, Any
from simplejrpc import StringField, BaseForm,RequireValidator, StringRangField, \
    Validator, F
from simplejrpc import TextMessage as r

from app.consts import constant
from app.exception.FormValidateException import FormValidateException


class FileExistsValidator(Validator):
    def __init__(self, message=None):
        super(FileExistsValidator, self).__init__(message)

    def clean_data(self, instance: Type[F]) -> Any:
        if not os.path.exists(self.value):
            raise FormValidateException(r("FILE_NOT_EXIST"))


class InstallForm(BaseForm):

    install_type = StringRangField(
        validators=[RequireValidator(r("INSTALL_TYPE_FORM"))], allow=[constant.INSTALL_COMPILE,
                                                                      constant.INSTALL_PACKAGE])


class SetInstallForm(BaseForm):
    set_type = StringRangField(
        validators=[RequireValidator(r("INSTALL_TYPE_FORM"))], allow=[ constant.SET_VERSION_AUTO, constant.SET_VERSION_MANUAL])
    bin_path = StringField(validators=[RequireValidator(r("NGINX_BIN_FILE_NOT_EXIST")),FileExistsValidator()])
    config_path = StringField(validators=[RequireValidator(r("NGINX_CONF_FILE_NOT_EXIST")),FileExistsValidator()])

class ServerDoForm(BaseForm):
    action = StringRangField(
        validators=[RequireValidator(r("SERVER_DO_FORM"))], allow=[ "start", "stop", "restart", "reload"])
import { Result } from 'gm-app-components';
import request from '../utils/request';

/**
 * 获取已安装的Nginx
 */
export const getInstalledNginxApi = () =>
  request<Result>(`/api/call/official/nginx/get_installed`);

/**
 * 获取可以安装的Nginx版本信息
 */
export const getNginxVersionApi = () =>
  request<Result<{ label: string; value: string }[]>>(
    `/api/call/official/nginx/get_versions`
  );

/**
 * 安装Nginx
 */
export const installNginxApi = (data: {
  install_type: string;
  version: string;
}) => request<Result>(`/api/call/official/nginx/install_nginx`, data);

/**
 * 卸载Nginx
 */
export const uninstallNginxApi = () =>
  request<Result>(`/api/call/official/nginx/uninstall_nginx`);

/**
 * 查看nginx安装进度
 * **/
export const checkNginxInstallProgressApi = () =>
  request<Result<{ status: number; progress: number }>>(
    `/api/call/official/nginx/check_process`
  );

/**
 * 停止Nginx安装
 **/
export const stopNginxInstallApi = () =>
  request<Result>(`/api/call/official/nginx/kill_process`);

/**
 * 获取Nginx安装日志
 */
export const getNginxInstallLogApi = () =>
  request<Result<{ content: string; status: number }>>(
    `/api/call/official/nginx/tail_log`
  );

/**
 * 获取nginx负载信息
 */
export const getNginxLoadApi = () =>
  request<Result>(`/api/call/official/nginx/get_loadavg`);

/**
 * 获取nginx运行状态
 */
export const getNginxStatusApi = () =>
  request<Result>(`/api/call/official/nginx/get_status`);

/**
 * nginx服务操作
 */
export const nginxActionApi = (data: { action: string }) =>
  request<Result>(`/api/call/official/nginx/server_do`, data);

/**
 * 获取nginx配置
 * **/
export const getNginxConfigApi = () =>
  request<Result>(`/api/call/official/nginx/get_perform_conf`);

/**
 * 设置nginx配置
 * **/
export const setNginxConfigApi = (data: { config_data: any }) =>
  request<Result>(`/api/call/official/nginx/set_perform_conf`, data);

/**
 * 获取nginx错误日志
 * **/
export const getNginxErrorLogApi = () =>
  request<Result>(`/api/call/official/nginx/get_error_log`);

/**
 * 清除nginx错误日志
 * **/
export const clearNginxErrorLogApi = () =>
  request<Result>(`/api/call/official/nginx/clear_log`);

/**
 * 手动设置nginx版本和配置
 */
export const setNginxVersionApi = (data: {
  version?: string;
  bin_path: string;
  config_path: string;
  set_type: 'manual' | 'auto';
}) => request<Result>(`/api/call/official/nginx/set_nginx`, data);

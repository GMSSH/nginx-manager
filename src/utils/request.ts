import { naiveui, Result } from 'gm-app-components';
import { locale } from './index';

const handledErrors = new Map(); // 用来记录已经处理过的错误类型

// 判断报错是否过期
function judgmentErrorExpired(key: string) {
  if (handledErrors.has(key)) {
    const value = handledErrors.get(key);
    const curTime = new Date().getTime();
    if (curTime - value.timeStamp > 2000) {
      handledErrors.delete(key);
      return true;
    } else {
      return false;
    }
  } else {
    return true;
  }
}

/**
 * 统一请求封装函数
 * @param url 请求地址
 * @param data 请求参数
 * @returns Promise<T> 返回接口数据
 */
const request = <T = Result>(
  url: string,
  data: { [key: string]: any } = {}
): Promise<T> => {
  return new Promise((resolve, reject) => {
    return window.$gm
      .request<Result>(url, {
        method: 'post',
        data: {
          version: window.$gm.version,
          transport: window.$gm.communicationType,
          params: {
            lang: locale,
            ...data,
          },
        },
      })
      .then((res) => {
        // 判断请求是否成功
        if (res.code == 200000 && res.data.code == 200) {
          resolve(res.data as T);
        } else if (res?.data?.code == 206) {
          window.$gm.openShell({
            arr: [res.data.data],
          });
          resolve(res.data as T);
        } else {
          reject(res);
          const errorMsg = res?.data?.data?.msg || res?.data?.msg;
          if (errorMsg && judgmentErrorExpired(errorMsg)) {
            // 显示错误信息
            naiveui.message.error(errorMsg);
            // 标记该错误类型为已处理
            handledErrors.set(errorMsg, { timeStamp: new Date().getTime() });
          }
        }
      })
      .catch((err) => {
        reject(err);
        const errorMsg = '请求错误';
        if (errorMsg && judgmentErrorExpired(errorMsg)) {
          // 显示错误信息
          naiveui.message.error(errorMsg);
          // 标记该错误类型为已处理
          handledErrors.set(errorMsg, { timeStamp: new Date().getTime() });
        }
      });
  });
};

export default request;

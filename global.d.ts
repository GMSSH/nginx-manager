// global.d.ts
// 定义 GMProps 接口

// 扩展全局 Window 接口
import{ GMProps }from 'gm-app-sdk';

declare global {
  interface Window {
    $gm: GMProps;
  }
}
export {};

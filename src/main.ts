import 'gm-app-sdk';
import { createApp } from 'vue';
import './style/index.scss';
import 'gm-app-components/index.css';
import App from './App.vue';
import { i18n } from './locales';
import { SvgIcon } from 'gm-app-components';

const initializeApp = () => {
  const app = createApp(App);
  app.component('SvgIcon', SvgIcon);
  app.use(i18n);
  app.mount('#app');
};
// 获取 webURL
const webURL = (window as any).$gm.webURL;
// 动态加载脚本函数
const loadScript = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.async = false; // 禁用异步加载，确保按顺序加载
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(script);
  });
};

// 加载 Ace Editor 及相关扩展
const loadAceEditor = async (): Promise<void> => {
  const aceScripts = [
    `${webURL}ace-builds@1.5.0/ace.js`,
    `${webURL}ace-builds@1.5.0/ext-language_tools.js`,
    `${webURL}ace-builds@1.5.0/ext-searchbox.js`,
  ];

  try {
    for (const src of aceScripts) {
      await loadScript(src);
    }
    console.log('Ace Editor and extensions loaded successfully!');
  } catch (error) {
    console.error(error);
  }
};
// 启动逻辑
(async () => {
  await loadAceEditor(); // 加载 Ace Editor 脚本
  initializeApp(); // 初始化 Vue 应用
})();

import { createI18n } from 'vue-i18n';
import zhCN from './json/zh-Hans.json';
import en from './json/en.json';
import {locale} from "@/utils";
//
const lang = locale === 'zh-CN' ? 'zhCN' : 'en';
export const i18n = createI18n({
  legacy: false,
  locale: lang,
  globalInjection: true, // 全局注册$t方法
  messages: {
    zhCN: zhCN,
    en: en,
  },
});
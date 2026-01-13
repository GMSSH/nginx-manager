import { naiveui } from 'gm-app-components';

// 获取系统语言设置，默认为中文
export const locale = window?.$gm?.lang || 'zh-CN';

/**
 * 生成一个随机字母
 * @returns 随机小写字母
 */
function getRandomLetter() {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz';
  const randomIndex = Math.floor(Math.random() * alphabet.length);
  return alphabet[randomIndex];
}

/**
 * 生成随机字符串
 * 包含大小写字母、数字和特殊符号的字符串
 * @returns 随机字符串，长度在16-30个字符之间
 */
export function generateRandomString() {
  const characters =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$^&*()=_~?.,';
  const length = Math.floor(Math.random() * (30 - 16 + 1)) + 16;
  let result = getRandomLetter();
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

/**
 * 复制文本到剪贴板
 * @param text 需要复制的文本
 * @returns 复制是否成功
 */
export const copyToClipboard = (text: string) => {
  // 创建一个文本域
  const textArea = document.createElement('textarea');
  // 隐藏掉这个文本域，使其在页面上不显示
  textArea.style.position = 'fixed';
  textArea.style.visibility = '-10000px';
  // 将需要复制的内容赋值给文本域
  textArea.value = text;
  // 将这个文本域添加到页面上
  document.body.appendChild(textArea);
  // 添加聚焦事件，写了可以鼠标选取要复制的内容
  textArea.focus();
  // 选取文本域内容
  textArea.select();

  if (!document.execCommand('copy')) {
    // 检测浏览器是否支持这个方法
    console.warn('浏览器不支持 document.execCommand("copy")');
    // 复制失败将构造的标签 移除
    document.body.removeChild(textArea);
    return false;
  } else {
    naiveui.message.success(
      window.$gm?.lang === 'en' ? 'Copy successful' : '复制成功'
    );
    // 复制成功后再将构造的标签 移除
    document.body.removeChild(textArea);
    return true;
  }
};

/**
 * 唤起文件选择窗口，并获取选择的文件
 * @returns Promise<FileList> 选中的文件列表
 */
export async function getWinFiles() {
  // 创建文件选择元素
  const input = document.createElement('input');
  input.setAttribute('type', 'file');
  input.setAttribute('style', 'display:none');
  input.setAttribute('multiple', 'true'); // 多选
  input.setAttribute('accept', ''); // 文件上传格式限制
  // 将文件选择元素添加到文档中
  document.body.appendChild(input);
  // 触发文件选择元素的点击事件
  input.click();
  // 等待文件选择元素的change事件
  return await new Promise((resolve) => {
    input.addEventListener('change', (e) => {
      const files = (e.target as HTMLInputElement).files || [];
      // 从文档中移除文件选择元素
      document.body.removeChild(input);
      // 抛出附件，并生成附件uid
      resolve(files);
    });
  });
}

/**
 * 获取根元素CSS变量值
 * @param cssVar CSS变量名（不包含--前缀）
 * @returns CSS变量值
 */
export function useRootElementCssVariable(cssVar: string) {
  // 获取根元素
  const root = document.documentElement;

  // 获取计算后的样式
  const rootStyle = getComputedStyle(root);

  /**
   * 获取CSS变量的值
   * @param variableName CSS变量名（不包含--前缀）
   * @returns CSS变量值
   */
  function getCssVariable(variableName: string) {
    // 检查CSS变量是否设置
    const isVar = rootStyle.getPropertyValue(`--${variableName}`);
    if (isVar) {
      return rootStyle.getPropertyValue(`--${variableName}`).trim();
    }

    return '';
  }

  return getCssVariable(cssVar);
}

/**
 * 防抖函数，用于限制函数的执行频率
 * 第一次调用会立即执行，后续调用会在指定延迟时间内只执行最后一次
 * @param fn 需要防抖的函数
 * @param time 延迟时间，单位为毫秒，默认300ms
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  time = 300
): (...args: Parameters<T>) => void {
  let timerId: ReturnType<typeof setTimeout> | null = null;
  let first = true;
  return function (...args: Parameters<T>): void {
    if (first) {
      // 第一次调用立即执行
      first = false;
      fn(...args);
      return;
    }
    if (timerId !== null) {
      // 如果已有定时器，清除它
      clearTimeout(timerId);
    }
    // 设置新的定时器
    timerId = setTimeout(() => {
      fn(...args);
      timerId = null;
    }, time);
  };
}
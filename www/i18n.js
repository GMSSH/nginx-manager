// const fs = require("fs").promises;
const path = require('path');
const fs = require('fs-extra');
const { parse } = require('@vue/compiler-sfc');

class ParseFile {
  // ^(.+?)\s*\?\s*(.+?)\s*:\s*(.+)$   三目运算符
  // 本地配置文件路径
  #localesPath = '';
  #addPath = '';
  // 本地配置文件数据
  #localesData = {};
  #dirPath = '';
  // 递归执行的文件夹路径
  #directoryPath = '';
  // .vue等文件内容
  #content = '';
  // 注释
  #comments = [];
  #singleLineCommentRegex = /\/\/.*$|\/\*[\s\S]*?\*\/|<!--[\s\S]*?-->$/gm;
  // 本次执行的缓存，也是最终输出到locales的数据
  #cacheResult = {};
  // 标签里的attr替换中文
  chineseRegex = /(['"`])([^`'"]*[\u4e00-\u9fa5]+[^`'"]*)(\1)/g;
  // 用于匹配单行注释的正则表达式
  // 当前解析文档临时用来存储替换的内容
  #temResult = {};
  // 临时存贮当前读取的文件所在的文件目录结构如：src/page/home/index.vue -> page.home
  #temDirs = '';
  constructor({ dirPath, localesPath, addPath }) {
    if (!dirPath) {
      throw Error('缺少入口文件夹路径');
    }
    this.#dirPath = dirPath;
    // 自动化根目录
    this.#directoryPath = path.resolve(__dirname, dirPath);
    // 配置文件根目录
    if (!localesPath) {
      this.#localesPath = path.resolve(
        this.#directoryPath,
        'locales/zh-Hans.json'
      );
    } else {
      this.#localesPath = path.resolve(__dirname, localesPath);
    }
    // 新增配置目录
    if (!addPath) {
      this.#addPath = path.resolve(this.#directoryPath, 'add.json');
    } else {
      this.#addPath = path.resolve(__dirname, addPath);
    }
    this.init();
  }
  async init() {
    const existsLocalesPath = await fs.pathExists(this.#localesPath);
    // 读取本地配置文件
    if (existsLocalesPath) {
      this.#localesData = await fs.readJson(this.#localesPath);
    } else {
      await fs.outputFile(this.#localesPath, JSON.stringify({}));
    }
    this.readDirectory(this.#directoryPath).then(async () => {
      if (existsLocalesPath) {
        // 把新增的写入addPath，便于提供给翻译
        await fs.writeJson(this.#addPath, this.#cacheResult, {
          spaces: 2,
        });
        // 文件对比，把差异的输入到localesPath里
        this.mergeJson(this.#localesData, this.#cacheResult);
        await fs.writeJson(this.#localesPath, this.#localesData, { spaces: 2 });
      } else {
        // 不存在直接写入
        await fs.writeJson(this.#localesPath, this.#cacheResult, { spaces: 2 });
      }
    });
  }
  // 读取配置文件，递归文件或文件夹
  async readDirectory(directoryPath) {
    try {
      const files = await fs.readdir(directoryPath);
      // const directoryName= path.dirname(directoryPath);
      for (const file of files) {
        const filePath = path.join(directoryPath, file);
        // 异步获取文件/目录状态
        const stat = await fs.stat(filePath);
        if (stat.isDirectory()) {
          // 如果是目录，递归处理
          await this.readDirectory(filePath);
        } else if (stat.isFile()) {
          // 处理文件并且返回文件里的配置信息
          await this.readFileByType(filePath);
        }
      }
    } catch (error) {
      console.error(`Error processing directory ${directoryPath}:`, error);
    }
  }
  // 读取文件，判断什么类型。使用不同处理方法
  async readFileByType(filePath) {
    // 使用平台相关的路径分隔符，分割成数组
    // 需要新建目录结构page.home.xxx
    const folders = filePath.split(path.sep);
    // 截取src后面的目录
    // 检索文件前，查看该文件在哪个目录下，最多只截取两个如src/page/home/xxx->page.home
    const srcIndex = folders.indexOf(this.#dirPath);
    if (folders.length && srcIndex !== -1) {
      this.#temDirs = folders
        .slice(srcIndex + 1, srcIndex + 3)
        .join('.')
        .replace(/\.(vue|ts|js|jsx|tsx)$/, '');
    } else {
      throw Error('代理文件夹失败');
    }
    // 读取内容
    this.#content = await fs.readFile(filePath, 'utf-8');
    const extname = path.extname(filePath).toLowerCase();

    let content = '';
    switch (extname) {
      case '.ts':
        content = this.parseJsOrTs(this.#content);
        break;
      case '.vue':
        content = this.parseVue(this.#content);
        break;
      case '.js':
        content = this.parseJsOrTs(this.#content);
        break;
      default:
      // return console.error("文件类型不支持", filePath);
    }
    // 当是处理文件里字段为空时，则不回写
    if (this.#temResult.writeFile) {
      delete this.#temResult.writeFile;
      // 提取的处理字段返回出去
      const srcdir = this.#temDirs.split('.');
      srcdir.reduce((acc, curr, index) => {
        if (!acc[curr]) {
          acc[curr] = {};
        }
        if (index === srcdir.length - 1) {
          // 合并
          acc[curr] = { ...acc[curr], ...this.#temResult };
        }
        return acc[curr];
      }, this.#cacheResult);
      try {
        // 当前文件检索完成，清空临时数据
        // 处理好文件回写
        await fs.writeFile(filePath, content, 'utf-8');
        // await this.logger(filePath, this.#temResult);
        this.#temResult = {};
      } catch (error) {
        console.error('回写文件出错', error);
      }
    }
  }
  // 日志
  async logger(filePath, result) {
    try {
      const { dirName, fileName } = this.getCurrentTime();
      const folderPath = path.join(__dirname, 'log', dirName);
      await fs.ensureDir(folderPath);
      await fs.writeJson(
        path.join(folderPath, fileName),
        { filePath, ...result },
        { spaces: 2 }
      );
    } catch (err) {
      console.error('Error:', err);
    }
  }
  getCurrentTime() {
    const now = new Date(); // 获取当前日期和时间
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    // 格式化并返回时间字符串
    return {
      dirName: `${year}_${month}_${day}`,
      fileName: `${year}_${month}_${day}_${hours}_${minutes}_${seconds}.json`,
    };
  }
  parseJsOrTs(content) {
    // 删除注释
    let scriptText = this.removeComments(content);
    // 替换script里中文
    scriptText = this.replaceChineseInJS(scriptText);
    // 回复注释
    scriptText = this.restoreComments(scriptText);
    const index = scriptText.indexOf('i18n');
    if (index === -1) {
      return `import { i18n } from '@/locales';\nconst $t = (...args) => i18n.global.t(...args);\n${scriptText}`;
    }
    return scriptText;
  }
  // 处理vue文件
  parseVue(content) {
    const parsed = parse(content);
    const templateContent = parsed.descriptor?.template?.content;
    const scriptSetup = parsed.descriptor?.scriptSetup;
    const scriptSetupContent =
      parsed.descriptor?.scriptSetup?.content?.trim?.();
    const scriptContent = parsed.descriptor?.script?.content?.trim?.();

    const styles = parsed.descriptor?.styles;
    let template = '';
    let scriptStr = '';
    let templateTag = '';
    if (templateContent) {
      let templateText = this.removeComments(templateContent);
      // 替换属性中的中文
      templateText = this.replaceChineseInAttrs(templateText);
      // 替换标签文本中的中文
      templateText = this.replaceChineseInTags(templateText);
      // 回复注释
      template = this.restoreComments(templateText);
      templateTag = `<template>${template}</template>`;
      // 输出处理后的内容
    }
    let scriptTag = '';
    // 处理script setup部分
    if (scriptSetupContent) {
      scriptTag = '<script setup';
      if (scriptSetup.lang) {
        scriptTag += ` lang=${scriptSetup.lang}>`;
      } else {
        scriptTag += `>`;
      }
      let scriptText = this.removeComments(scriptSetupContent);
      // 替换script里中文
      scriptText = this.replaceChineseInJS(scriptText);

      // 处理返回script
      let i18n = '';
      const vi18n = scriptText.indexOf('i18n');
      // useI18n只能在setup里使用
      if (vi18n === -1) {
        i18n = `import { useI18n } from 'vue-i18n';\n  const { t:$t } = useI18n();\n`;
      }
      // 返回script内容
      scriptStr = `${scriptTag}\n  ${i18n}${this.restoreComments(
        scriptText
      )}\n</script>`;
    }
    // 处理纯script部分
    if (scriptContent) {
      scriptTag = '<script>';
      let scriptText = this.removeComments(scriptContent);
      // 替换script里中文
      scriptText = this.replaceChineseInJS(scriptText);

      // 处理返回script
      let i18n = '';
      const vi18n = scriptText.indexOf('i18n');
      // 普通script
      if (vi18n === -1) {
        i18n = `import { i18n } from '@/locales';\n  const $t = i18n.global.t;`;
      }
      // 返回script内容
      scriptStr = `${scriptTag}\n  ${i18n}${this.restoreComments(
        scriptText
      )}\n </script>`;
    }
    // 处理style标签
    let styleTag = '';
    if (styles?.length) {
      styleTag = '<style';
      const attrs = styles[0]?.attrs;
      const style = styles[0].content;
      // 处理style标签
      if (attrs?.lang) styleTag += ` lang="${attrs.lang}"`;
      if (attrs?.scoped) styleTag += ' scoped';
      styleTag += `>${style}</style>`;
    }

    // 返回完整的vue文件
    return `${templateTag}\n${scriptStr}\n${styleTag}`;
  }
  replaceChineseInJS(scriptText) {
    // 匹配纯文本
    const notJsStr = scriptText.match(this.chineseRegex);
    // 不是`xx${xx}`
    if (notJsStr) {
      notJsStr.forEach((cvalue) => {
        if (cvalue) {
          const token = this.createRandomKey(cvalue.replace(/["'`]/g, ''));
          scriptText = scriptText.replace(cvalue, token);
        }
      });
    }

    // 包含${}的字符
    const expressions = this.extractTemplateExpressions(scriptText);
    if (expressions.length) {
      scriptText = this.recursiveHandle(scriptText, expressions);
    }

    return scriptText;
  }
  recursiveHandle(str, expressions) {
    let newStr = str;

    expressions.forEach((expr) => {
      if (expr.includes('${')) {
        const innerExprs = this.extractTemplateExpressions(expr);
        newStr = this.recursiveHandle(newStr, innerExprs);
      }
      // ✅ 无论有没有嵌套，都提取字符串字面量
      const stringLiteralMatches = expr.match(this.chineseRegex);
      if (stringLiteralMatches) {
        stringLiteralMatches.forEach((match) => {
          const token = this.createRandomKey(match.replace(/["'`]/g, ''));
          newStr = newStr.replace(match, token);
        });
      }
    });

    return newStr;
  }
  // 递归查找 ${xx}
  extractTemplateExpressions(str) {
    const result = [];
    const stack = [];
    let startIndex = -1;

    for (let i = 0; i < str.length; i++) {
      if (str[i] === '$' && str[i + 1] === '{') {
        if (stack.length === 0) {
          startIndex = i; // 记录最外层 `${` 起始位置
        }
        stack.push('${');
        i++; // 跳过 {
      } else if (str[i] === '}') {
        if (stack.length > 0) {
          stack.pop();
          if (stack.length === 0 && startIndex !== -1) {
            const fullExpr = str.slice(startIndex + 2, i); // 不含 `${` 和 `}`
            result.push(fullExpr);
            startIndex = -1;
          }
        }
      }
    }

    return result;
  }
  // 分析tag中的中文
  replaceChineseInTags(content) {
    const tagReg = /(>\s*\{{0,2})\s*([^<]+?)\s*(\}{0,2}\s*<)/g;
    // const chineseRegex = /(['"]?)[\u4e00-\u9fa5，。！？“”《》（）：]+(['"]?)/g;
    // const chineseRegex = /(['"`])([^`'"]*[\u4e00-\u9fa5]+[^`'"]*)(\1)/g;
    const chineseRegex = /(['"])?([^'"]*[\u4e00-\u9fa5]+[^'"]*)(['"])?/g;
    return content.replace(tagReg, (matchStr, left, value, right) => {
      let returnVal = matchStr;
      // 删除>和<括号
      const str = matchStr.replace(/^>\s*|\s*<$/g, '');

      // const notJsStr = str.split(/\{\{[\s\S]*?\}\}/g)?.filter(Boolean);
      // 尝试{{xx}}分割
      const regex = /\{\{([^{}]*)\}\}/g;
      // 标签里包含 js语法
      const jsStr = [];
      let match;
      while ((match = regex.exec(str)) !== null) {
        jsStr.push(match[1]);
      }

      if (jsStr?.length) {
        jsStr.forEach((str) => {
          const notJsStr = str.match(chineseRegex);
          if (notJsStr) {
            if (notJsStr.length > 1) {
              // 此处说attr是一个表达式 :title="queryArgu == 1 ? '管理的吧' : '加入的吧'"
              notJsStr.forEach((cvalue) => {
                if (cvalue) {
                  const token = this.createRandomKey(
                    cvalue.replace(/["'`]/g, '')
                  );
                  returnVal = returnVal.replace(cvalue, token);
                }
              });
            } else {
              const cvalue = notJsStr[0];
              if (cvalue) {
                const token = this.createRandomKey(
                  cvalue.replace(/["'`]/g, '')
                );
                returnVal = returnVal.replace(cvalue, token);
              }
            }
          }
        });
      }
      // 普通文本
      const notJsStr = str.match(chineseRegex);
      if (notJsStr) {
        if (notJsStr.length > 1) {
          // 此处说attr是一个表达式 :title="queryArgu == 1 ? '管理的吧' : '加入的吧'"
          notJsStr.forEach((cvalue) => {
            if (cvalue?.trim()) {
              let token = this.createRandomKey(cvalue.replace(/["'`]/g, ''));
              token = this.tagContentPosition(left, right, token);
              returnVal = returnVal.replace(cvalue, token);
            }
          });
        } else {
          const cvalue = notJsStr[0];
          if (cvalue?.trim()) {
            let token = this.createRandomKey(cvalue.replace(/["'`]/g, ''));
            token = this.tagContentPosition(left, right, token);
            returnVal = returnVal.replace(cvalue, token);
          }
        }
      }

      if (jsStr?.length || notJsStr?.length) {
        return returnVal;
      }

      return matchStr;
    });
  }

  tagContentPosition(left, right, token) {
    return `{{${token}}}`;
    if (left.includes('{{') && right.includes('}}')) {
      // {{ token }}形式
      return token;
    } else {
      //{{ xx }}token 形式->left.includes("{{")
      //token{{ xx }} 形式->right.includes("}}")
      //token{{ xx }}token1 形式-> !left.includes("{{") && !right.includes("}}")
      return `{{${token}}}`;
    }
  }

  // 替换属性中的中文
  replaceChineseInAttrs(content) {
    const attrRegex = /(\:?)([a-zA-Z0-9_]+)\s*=\s*["']([^"]+)["']/g;
    // const chineseRegex = /(['"`])([^`'"]*[\u4e00-\u9fa5]+[^`'"]*)(\1)/g;
    const chineseRegex = /(['"])?([^'"]*[\u4e00-\u9fa5]+[^'"]*)(['"])?/g;
    // 匹配属性及属性值的正则
    return content.replace(attrRegex, (match, _, attr, value) => {
      let returnVal = match;
      // 判断属性值是否包含中文

      const chineseMatcheArr = value.match(chineseRegex);
      if (chineseMatcheArr) {
        if (chineseMatcheArr.length > 1) {
          let a = '';
          //此处说attr是一个表达式 :title="queryArgu == 1 ? '管理的吧' : '加入的吧'"
          chineseMatcheArr.forEach((cvalue, cindex) => {
            if (_ || cindex === chineseMatcheArr.length - 1) {
              a = '';
            } else if (!_) {
              a = '+';
            }
            const token = `${this.createRandomKey(
              cvalue.replaceAll("'", '')
            )}${a}`;
            returnVal = returnVal.replace(cvalue, token);
          });
        } else {
          let cvalue = chineseMatcheArr[0];
          const token = this.createRandomKey(cvalue.replace(/["'`]/g, ''));
          // 匹配成:attr="$t(xx)"
          returnVal = returnVal.replace(cvalue, token);
        }
        if (!_) {
          returnVal = `:${returnVal}`;
        }
        return returnVal;
      }
      return match;
    });
  }
  //合并json
  mergeJson(target, source) {
    for (let key in source) {
      if (source.hasOwnProperty(key)) {
        if (
          typeof source[key] === 'object' &&
          source[key] !== null &&
          !Array.isArray(source[key])
        ) {
          // 如果值是对象，则递归合并
          target[key] = this.mergeJson(target[key] || {}, source[key]);
        } else if (target[key] !== source[key]) {
          target[key] = source[key];
        }
      }
    }
    return target;
  }
  // 创建token
  createRandomKey(value) {
    let key, localesKey, cacheKey, temKey;
    // 本地配置文件的json里找
    localesKey = this.findKeyWithValue(this.#localesData, value);
    if (!localesKey) {
      // 通过内存中json树去寻找
      cacheKey = this.findKeyWithValue(this.#cacheResult, value);
    }
    if (!cacheKey) {
      //当前解析文件缓存是否重复key
      temKey = this.findKeyWithValue(this.#temResult, value);
    }
    //只有匹配成功，需要替换中文，即使从缓存获取了，也需要写入.vue等文件
    this.#temResult.writeFile = true;
    // 本地配置和临时缓存都不存在创建key
    if (!temKey && !cacheKey && !localesKey) {
      key = this.generateUniqueString(6);
      while (
        this.findValueWithKey(this.#localesData, key) ||
        this.findValueWithKey(this.#cacheResult, key) ||
        this.#temResult?.[key]
      ) {
        // key不能和当前页面已生成字段名重复，也不可以和其他同目录下已生成字段名重复
        // 如pages.home下所有文件不能字段重复
        key = this.generateUniqueString(6);
      }
      //存储新建的token和value
      this.#temResult[key] = value;
      key = `$t('${this.#temDirs}.${key}')`;
    } else if (localesKey) {
      // 从本地缓存获取
      key = `$t('${localesKey}')`;
    } else if (cacheKey) {
      // 从临时缓存获取
      key = `$t('${cacheKey}')`;
    } else if (temKey) {
      key = `$t('${this.#temDirs}.${temKey}')`;
    }
    return key;
  }
  // 通过值获取key
  findKeyWithValue(obj, value, path = '') {
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        // 构造新的路径
        const newPath = path ? `${path}.${key}` : key;
        if (
          typeof obj[key] === 'object' &&
          obj[key] !== null &&
          !Array.isArray(obj[key])
        ) {
          const result = this.findKeyWithValue(obj[key], value, newPath);
          if (result) return result;
        } else if (obj[key] === value) {
          // 如果值匹配目标字符串，返回当前路径
          return newPath;
        }
      }
    }
    return null;
  }
  // 通过key获取到值
  findValueWithKey(obj, value) {
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        if (
          //递归
          typeof obj[key] === 'object' &&
          obj[key] !== null &&
          !Array.isArray(obj[key])
        ) {
          return this.findKeyWithValue(obj[key], value);
        } else if (obj[key] === value) {
          return value;
        }
      }
    }
    return null;
  }
  //随机生成6位字符
  generateUniqueString(length) {
    const characters =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';

    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * characters.length);
      result += characters[randomIndex];
    }

    return result;
  }
  // 删除注释
  removeComments(content) {
    // 提取注释部分，使用占位符替换
    const singleLineCommentRegex = this.#singleLineCommentRegex;
    return content.replace(singleLineCommentRegex, (match) => {
      this.#comments.push(match); // 保存注释
      return `#*COMMENT${this.#comments.length - 1}*#`; // 替换注释为占位符
    });
  }
  // 还原注释
  restoreComments(content) {
    this.#comments.forEach((comment, index) => {
      content = content.replace(`#*COMMENT${index}*#`, comment);
    });
    this.#comments = [];
    return content;
  }
}
// process.on('unhandledRejection', (reason, promise) => {
//   console.error('Unhandled promise rejection:', promise, 'reason:', reason);
// });
// process.on('uncaughtException', (err) => {
//   console.error('Uncaught exception:', err);
//   process.exit(1);
// });

new ParseFile({
  dirPath: 'src',
  localesPath: 'src/locales/json/zh-Hans.json',
  addPath: 'src/locales/json/add.json',
});

// 思路，将配置文件还是放到一个zh.json里，按照和现在一样的方式{ post:{ aasf:'',jghkh:'dada } }来写入，
// 额外写入一个依赖关系 page.js文件，这个文件表面了所有page依赖了zh.json里哪些配置项，['post.aasf','post.jghkh']
// 做一个命令，将zh.json的项和 page.js匹配，匹配分类后，按照当前匹配结果，分割成页面独有的配置文件，写入到文件夹里。
// 前端在路由里beforeEarch 通过判断即将进入哪个路由页面，加载这个页面的json文件实现按需加载。
// const loadLocaleMessages = async (locale) => {
//   try {
//     // 动态导入并设置语言文件
//     const commonMessages = await import(`./locales/${locale}.common.json`);
//     const uiMessages = await import(`./locales/${locale}.ui.json`);
//     const errorMessages = await import(`./locales/${locale}.errors.json`);

//     // 将加载的翻译内容合并
//     i18n.global.setLocaleMessage(locale, {
//       ...commonMessages.default,
//       ...uiMessages.default,
//       ...errorMessages.default
//     });

//     // 设置当前语言
//     i18n.global.locale = locale;
//   } catch (e) {
//     console.error(`Failed to load locale messages for ${locale}:`, e);
//   }
// };

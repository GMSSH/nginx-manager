module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'juming',
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/vue3-recommended',
  ],
  overrides: [
    {
      env: {
        node: true,
      },
      files: ['.eslintrc.{js,cjs}'],
      parserOptions: {
        sourceType: 'script',
      },
    },
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    parser: '@typescript-eslint/parser',
  },
  ignorePatterns: ['*.d.ts', '*.test.ts', '**/node_modules/**'],
  plugins: ['@typescript-eslint', 'vue'],
  rules: {
    indent: 'off', // 或者 "indent": 0
    'comma-dangle': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    'vue/max-attributes-per-line': 'off',
    'vue/singleline-html-element-content-newline': 'off',
    'vue/multiline-html-element-content-newline': 'off',
    'no-lonely-if': 'off',
    'vue/html-self-closing': ['error', {
      html: {
        void: 'always',  // 允许 void 元素自闭合
        normal: 'never',
        component: 'always'
      }
    }]
  },
};

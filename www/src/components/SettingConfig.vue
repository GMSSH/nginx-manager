<template>
  <div class="setting-config">
    <n-spin :show="loading">
      <n-scrollbar
        :style="{ height: `${windowHeight - 219}px`, padding: '15px' }"
      >
        <n-form
          ref="formRef"
          :label-width="230"
          :model="formData"
          :show-require-mark="false"
          label-placement="left"
        >
          <n-form-item
            v-for="(item, index) in formData?.config"
            :key="item?.name"
            :label="item?.name"
            :path="`config.${index}.value`"
            size="small"
            :rule="{
              required: true,
              message: `${item?.name === 'gzip' ? t('请选择') : t('请输入')}${item?.name}`,
              trigger: ['input', 'blur'],
              type: numberFields.includes(item?.name) ? 'number' : 'string',
            }"
          >
            <n-select
              v-if="item?.name === 'gzip'"
              v-model:value="formData.config[index].value"
              size="small"
              style="width: 140px"
              :placeholder="t('请选择')"
              :options="[
                { label: t('开启'), value: 'on' },
                { label: t('关闭'), value: 'off' },
              ]"
              clearable
            />
            <n-input-number
              v-else-if="numberFields.includes(item?.name)"
              v-model:value="formData.config[index].value"
              :allow-input="onlyAllowNumber"
              :min="fieldRange[item?.name]?.min"
              :max="fieldRange[item?.name]?.max"
              :show-button="false"
              style="width: 140px"
              :placeholder="t('请输入')"
            />
            <NInput
              v-else-if="item?.name === 'worker_processes'"
              v-model:value="formData.config[index].value"
              :allow-input="allowInput"
              :show-button="false"
              style="width: 140px"
              :placeholder="t('请输入')"
            >
              <!-- <template v-if="item?.unit" #suffix> {{ item?.unit }} </template> -->
            </NInput>
            <NInput
              v-else
              v-model:value="formData.config[index].value"
              :show-button="false"
              style="width: 140px"
              :placeholder="t('请输入')"
            >
              <!-- <template v-if="item?.unit" #suffix> {{ item?.unit }} </template> -->
            </NInput>
            <div class="config-ps">{{ item?.ps }}</div>
          </n-form-item>
        </n-form>
      </n-scrollbar>
    </n-spin>
    <div style="padding-bottom: 15px">
      <n-button
        :loading="submitLoading"
        text-color="var(--jm-accent-7)"
        size="medium"
        type="primary"
        style="width: 110px; margin-left: 245px"
        @click="handleThrottle"
      >
        {{ t('保存') }}
      </n-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { throttle } from 'lodash-es';
  import { FormInst, NButton, NInput, NInputNumber } from 'naive-ui';
  import { naiveui, useApp } from 'gm-app-components';
  import { useI18n } from 'vue-i18n';
  import { NUMBERREG } from '@/utils/regexp';
  import { getNginxConfigApi, setNginxConfigApi } from '@/api';

  const numberFields = [
    'worker_connections',
    'gzip_min_length',
    'gzip_comp_level',
    'client_max_body_size',
    'server_names_hash_bucket_size',
    'client_header_buffer_size',
    'client_body_buffer_size',
    'keepalive_timeout'
  ];
  const { windowHeight } = useApp();
  const { t } = useI18n();
  const formData = ref<any>({
    config: [],
  });
  /** 只能输入数字 */
  const onlyAllowNumber = (value: string) => !value || NUMBERREG.test(value);
  const loading = ref(false);
  const formRef = ref<FormInst | null>(null);
  const submitLoading = ref(false);
  const fieldRange = {
    client_body_buffer_size: {
      min: 1,
      max: 1000,
    },
    client_header_buffer_size: {
      min: 1,
      max: 1000,
    },
    client_max_body_size: {
      min: 1,
      max: 1000,
    },
    gzip_comp_level: {
      min: 1,
      max: 9,
    },
    gzip_min_length: {
      min: 1,
      max: 1000,
    },
    keepalive_timeout: {
      min: 1,
      max: 1000,
    },
    server_names_hash_bucket_size: {
      min: 1,
      max: 1000,
    },
    worker_connections: {
      min: 10,
      max: 100000,
    },
  };

  /**
   * 获取nginx配置
   */
  const getNginxConfig = () => {
    loading.value = true;
    getNginxConfigApi()
      .then((res) => {
        formData.value.config = res.data;
        formData.value.config.forEach((item) => {
          if (numberFields.includes(item?.name)) {
            item.value = item.value ? Number(item.value) : null;
          }
        });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  /**
   * 提交
   */
  const submit = () => {
    formRef.value?.validate((errors) => {
      if (!errors) {
        submitLoading.value = true;
        const configData = {};
        formData.value.config.forEach((item) => {
          configData[item.name] = item.value;
        });
        setNginxConfigApi({ config_data: configData })
          .then((res) => {
            getNginxConfig();
            naiveui.message.success(res.msg);
          })
          .finally(() => {
            submitLoading.value = false;
          });
      }
    });
  };

  const handleThrottle = throttle(
    () => {
      submit();
    },
    1000,
    {
      trailing: false,
    }
  );

  const allowInput = (value: string) => {
    // 允许输入 "auto" 的前缀（必须小写）
    if (/^a(u(t(o)?)?)?$/.test(value)) {
      return true;
    }

    // 允许纯数字
    return /^[0-9]*$/.test(value);
  };

  defineExpose({
    getNginxConfig,
  });
</script>

<style lang="scss" scoped>
  .config-ps {
    margin-left: 10px;
    color: var(--jm-accent-7);
    font-size: 12px;
  }
</style>

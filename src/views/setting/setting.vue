<template>
  <page-container-layout :title="t('配置调整')">
    <template #header>
      <n-flex justify="space-between">
        <div class="header-left">
          <span class="title">{{ t('配置调整') }}</span>
        </div>

        <div class="header-right">
          <n-button
            type="primary"
            text-color="var(--jm-accent-7)"
            @click="handleThrottle"
          >
            {{ t('打开配置文件') }}
          </n-button>
        </div>
      </n-flex>
    </template>

    <div class="nginx-config">
      <SettingConfig ref="settingConfigRef" :current-version="currentVersion" />
    </div>
  </page-container-layout>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  import SettingConfig from '@/components/SettingConfig.vue';
  import PageContainerLayout from '@/layout/PageContainerLayout.vue';
  import { VersionInfoType } from '@/types/type';
  import { onActivated, ref } from 'vue';
  import { throttle } from 'lodash-es';

  const props = defineProps<{
    currentVersion: VersionInfoType;
    getInstalledVersion: () => void;
  }>();
  const { t } = useI18n();
  const settingConfigRef = ref();

  const getData = () => {
    settingConfigRef.value?.getNginxConfig();
  };

  const handleThrottle = throttle(
    () => {
      handleOpenConfigFile();
    },
    2000,
    {
      trailing: false, // 最后一次要执行
    }
  );

  const handleOpenConfigFile = () => {
    window.$gm?.openCodeEditor(props.currentVersion.config_path);
  };

  onActivated(() => {
    props.getInstalledVersion();
  });

  defineExpose({
    getData,
  });
</script>

<style lang="scss" scoped>
  .header-left {
    display: flex;
    align-items: center;
    .title {
      font-size: 18px;
      font-weight: bold;
    }
  }

  .nginx-config {
    background: var(--jm-accent-1);
    // padding: 15px;
  }
</style>

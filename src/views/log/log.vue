<template>
  <page-container-layout :title="t('日志')">
    <template #header>
      <n-flex justify="space-between">
        <div class="header-left">
          <span class="title">{{ t('日志') }}</span>
        </div>

        <div class="header-right">
          <n-button
            :loading="submitLoading"
            type="primary"
            text-color="var(--jm-accent-7)"
            @click="handleClear()"
          >
            {{ t('清除日志') }}
          </n-button>
        </div>
      </n-flex>
    </template>
    <div class="log-content">
      <n-spin :show="loading">
        <n-scrollbar
          :style="{ height: `${windowHeight - 200}px`, padding: '0 15px' }"
        >
          <div v-if="logTxt" ref="log" class="log-container-box">
            {{ logTxt }}
          </div>
          <div v-if="!logTxt && !loading" class="log-empty-box">
            <img class="null-img" src="@/assets/null.png" alt="" />
            <div class="null-txt">{{ t('暂无日志') }}</div>
          </div>
        </n-scrollbar>
      </n-spin>
    </div>
  </page-container-layout>
</template>

<script setup lang="ts">
  import { ref, onActivated } from 'vue';
  import { useI18n } from 'vue-i18n';
  import PageContainerLayout from '@/layout/PageContainerLayout.vue';
  import { clearNginxErrorLogApi, getNginxErrorLogApi } from '@/api';
  import { useApp, naiveui } from 'gm-app-components';
  import { VersionInfoType } from '@/types/type';

  const { windowHeight } = useApp();
  const { t } = useI18n();
  const loading = ref(true);
  const logTxt = ref('');
  const submitLoading = ref(false);

  const props = defineProps<{
    getInstalledVersion: () => void;
    currentVersion: VersionInfoType;
  }>();

  /**
   * 清除日志
   */
  const handleClear = () => {
    naiveui.dialog.warning({
      maskClosable: false,
      title: t('警告'),
      content: `${t('您确定要清除日志吗')}`,
      positiveText: `${t('确定')}(Y)`,
      negativeText: `${t('取消')}(N)`,
      class: 'dialog-warning',
      onPositiveClick: () => {
        submitLoading.value = true;
        clearNginxErrorLogApi()
          .then(() => {
            getLog();
          })
          .finally(() => {
            submitLoading.value = false;
          });
      },
    });
  };

  /**
   * 获取日志
   */
  const getLog = () => {
    loading.value = true;
    getNginxErrorLogApi()
      .then((res) => {
        logTxt.value = res.data;
      })
      .finally(() => {
        loading.value = false;
      });
  };

  onActivated(() => {
    props.getInstalledVersion();
  });

  const getData = () => {
    getLog();
  };

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

  .log-content {
    background: var(--jm-accent-1);
    padding: 15px 0;
    .log-container-box {
      color: #ffffffb3;
      white-space: pre-line;
      word-break: break-all;
    }

    .log-empty-box {
      text-align: center;
      padding-top: 20%;
      .null-img {
        width: 62px;
      }
      .null-txt {
        font-size: 14px;
        color: var(--jm-accent-5);
      }
    }
  }
</style>

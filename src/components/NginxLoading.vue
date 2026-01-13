<template>
  <div v-if="taskLoading" class="glob-modal">
    <div class="glob-modal-container">
      <template v-if="isTaskFail">
        <img
          src="@/assets/error.png"
          class="glob-modal-container-img"
          alt=""
        />
        <div class="glob-modal-container-txt">
          {{ nginxLoadingData?.loadingErrorText }}
        </div>
      </template>
      <template v-else>
        <img
          src="@/assets/loading.png"
          class="glob-modal-container-img"
          alt=""
        />
        <div class="glob-modal-container-txt">
          {{ nginxLoadingData?.loadingText }}
        </div>
      </template>
      <n-space>
        <n-button
          v-if="isTaskFail"
          color="rgba(240, 77, 60, 1)"
          style="width: 110px"
          @click="taskLoading = false"
        >
          <template #icon>
            <svg-icon
              icon="icon-a-guanbi"
              font-size="18"
              color="var(--jm-accent-7)"
            />
          </template>
          {{ $t('close') }}
        </n-button>
        <n-button
          v-else
          color="rgba(240, 77, 60, 1)"
          style="max-width: 120px"
          @click="stopTask"
        >
          <template #icon>
            <svg-icon icon="icon-zanting" color="var(--jm-accent-7)" />
          </template>
          {{ nginxLoadingData?.loadingStopText }}
        </n-button>
        <n-button
          type="primary"
          style="max-width: 120px"
          @click="handleThrottle"
        >
          <template #icon>
            <svg-icon icon="icon-chakan1" color="var(--jm-accent-7)" />
          </template>
          {{ $t('查看日志') }}
        </n-button>
      </n-space>
    </div>
  </div>
</template>
<script setup lang="ts">
  import { onMounted, ref } from 'vue';
  import {
    checkNginxInstallProgressApi,
    getInstalledNginxApi,
    getNginxInstallLogApi,
    stopNginxInstallApi,
  } from '@/api';
  import { useI18n } from 'vue-i18n';
  import { throttle } from 'lodash-es';
  import { naiveui } from 'gm-app-components';

  let timer: any = null;
  const taskLoading = ref(false);
  const { t: $t } = useI18n();
  const nginxLoadingData = ref({
    loadingText: $t('运行中...'),
    loadingStopText: $t('停止运行'),
    loadingErrorText: $t('运行失败'),
    loadingType: 'unknow',
  });

  const emit = defineEmits(['stopTask']);
  const isTaskFail = ref(false); // 任务失败

  /**
   * 开始任务
   * **/
  const startTask = (data: {
    success: (res: any) => any;
    fail: (res: any) => any;
    init: () => any;
  }) => {
    isTaskFail.value = false;
    const localStr = localStorage.getItem('NginxLoading');
    if (localStr) {
      nginxLoadingData.value = JSON.parse(localStr);
    } else {
      nginxLoadingData.value = {
        loadingText: $t('运行中...'),
        loadingStopText: $t('停止运行'),
        loadingErrorText: $t('运行失败'),
        loadingType: 'unknow',
      };
    }
    const { init, success, fail } = data;
    const isInit = init();
    // 刚打开外置应用，初始化任务暂不开启loading
    if (!isInit) {
      taskLoading.value = true;
    }
    clearTimeout(timer);
    checkTaskStatus(success, fail);
  };

  /**
   * 查看任务
   * **/
  function checkTaskStatus(success, fail) {
    checkNginxInstallProgressApi()
      .then((res) => {
        if (res.data) {
          taskLoading.value = true;
          // 运行中
          timer = setTimeout(() => {
            checkTaskStatus(success, fail);
          }, 3000);
        } else {
          // 任务结束
          clearTimeout(timer);
          getInstalledNginxApi()
            .then((res) => {
              if (nginxLoadingData?.value?.loadingType === 'install') {
                // 安装处理
                judgeInstallResult(success, fail, res?.data);
              } else if (nginxLoadingData?.value?.loadingType === 'uninstall') {
                // 卸载处理
                judgeUninstallResult(success, fail, res?.data);
              } else {
                success({ data: res?.data });
                taskLoading.value = false;
              }
            })
            .finally(() => {
              // taskLoading.value = false;
              localStorage.removeItem('NginxLoading');
            });
        }
      })
      .catch(() => {
        fail({});
        isTaskFail.value = true;
        // taskLoading.value = false;
      });
  }

  /**
   * 停止任务
   * **/
  const stopTask = () => {
    naiveui.dialog.warning({
      maskClosable: false,
      title: $t('警告'),
      content: `${$t('是否终止该任务？')}`,
      positiveText: `${$t('确定')}(Y)`,
      negativeText: `${$t('取消')}(N)`,
      class: 'dialog-warning',
      onPositiveClick: () => {
        stopNginxInstallApi().then((res) => {
          emit('stopTask');
          clearTimeout(timer);
          taskLoading.value = false;
          naiveui.message.success(res.msg);
          localStorage.removeItem('NginxLoading');
        });
      },
    });
  };

  /**
   * 查看日志
   * **/
  const viewLog = () => {
    getNginxInstallLogApi();
  };

  const handleThrottle = throttle(
    () => {
      viewLog();
    },
    1000,
    {
      trailing: false,
    }
  );

  /**
   * 判断安装结果
   */
  const judgeInstallResult = (success, fail, data) => {
    if (data?.version) {
      // 安装成功
      success({ data });
      taskLoading.value = false;
    } else {
      // 安装失败
      fail({});
      isTaskFail.value = true;
    }
  };

  /**
   * 判断卸载结果
   */
  const judgeUninstallResult = (success, fail, data) => {
    if (data?.manager == 0) {
      // 卸载成功
      success({ data });
      taskLoading.value = false;
    } else {
      // 卸载失败
      fail({ data });
      isTaskFail.value = true;
    }
  };

  defineExpose({
    startTask,
  });

  onMounted(() => {});
</script>
<style scoped lang="scss">
  .glob-modal {
    position: fixed;
    background: rgba(16, 16, 16, 0.8);
    left: 0;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 999999;
    &-container {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 400px;
      height: 249px;
      background: var(--jm-accent-1);
      box-shadow: 0 2px 21px 0 rgba(0, 0, 0, 0.14);
      border-radius: 8px 8px 8px 8px;
      border: 1px solid #4c4c4c;
      @include flex(center, center, column);
      &-img {
        width: 56px;
      }
      &-txt {
        font-size: 13px;
        color: var(--jm-accent-7);
        margin-top: 20px;
        margin-bottom: 36px;
      }
    }
  }
</style>

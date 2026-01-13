<template>
  <page-container-layout :title="t('控制台')">
    <template #header>
      <n-flex v-if="nginxStatus" justify="space-between">
        <div class="header-left">
          <span class="title">{{ t('控制台') }}</span>
          <span class="state">
            {{ t('当前状态') }}：
            <span v-if="nginxStatus === 'start'" class="state-txt state-open">
              {{ t('运行中') }}
              <svg-icon
                class="icon"
                font-size="12px"
                icon="icon-kaishi1"
                color="var(--jm-success-color)"
              />
            </span>
            <span v-else class="state-txt state-off">
              {{ t('已停止') }}
              <svg-icon
                class="icon"
                font-size="12px"
                icon="icon-zanting2"
                color="var(--jm-warning-color)"
              />
            </span>
          </span>
        </div>
        <div class="header-right">
          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <div
                class="opr-btn"
                @click="
                  handleAction(
                    nginxStatus === 'start' ? 'stop' : 'start',
                    nginxStatus === 'start' ? t('停止') : t('启动')
                  )
                "
              >
                <svg-icon
                  v-if="nginxStatus === 'start'"
                  icon="icon-tingzhi"
                  color="var(--jm-accent-7)"
                />
                <svg-icon
                  v-else
                  icon="icon-qidong"
                  color="var(--jm-accent-7)"
                />
              </div>
            </template>
            {{ nginxStatus === 'start' ? t('停止') : t('启动') }}
          </n-tooltip>
          <n-tooltip trigger="hover">
            <template #trigger>
              <div class="opr-btn" @click="handleAction('restart', t('重启'))">
                <svg-icon icon="icon-chongqi" color="var(--jm-accent-7)" />
              </div>
            </template>
            {{ t('重启') }}
          </n-tooltip>
          <n-tooltip trigger="hover">
            <template #trigger>
              <div class="opr-btn" @click="handleAction('reload', t('重载'))">
                <svg-icon icon="icon-zhongzai" color="var(--jm-accent-7)" />
              </div>
            </template>
            {{ t('重载') }}
          </n-tooltip>
        </div>
      </n-flex>
    </template>

    <n-spin :show="loading" style="height: 100%">
      <!--已启动-->
      <n-scrollbar
        v-if="nginxStatus === 'start' && loadInfo"
        :style="{ height: `${windowHeight - 200}px` }"
      >
        <div class="console-content">
          <div class="console-title">{{ t('负载信息') }}</div>
          <div class="console-list">
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('活动连接(Active connections) PUBLIC') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.active }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('总连接次数(accepts)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.accepts }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('总握手次数(handled)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.handled }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('请求数(Reading)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.Reading }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('响应数(Writing)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.Writing }}</div>
            </div>

            <div class="console-item">
              <div class="console-item-col title">
                {{ t('驻留进程(Waiting)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.Waiting }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('工作进程(Worker)') }}
              </div>
              <div class="console-item-col value">{{ loadInfo?.worker }}</div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('Nginx占用CPU(Workercpu)') }}
              </div>
              <div class="console-item-col value">
                {{ loadInfo?.workercpu }}
              </div>
            </div>
            <div class="console-item">
              <div class="console-item-col title">
                {{ t('Nginx占用内存(Worker memory)') }}
              </div>
              <div class="console-item-col value">
                {{ loadInfo?.workermen }}
              </div>
            </div>
          </div>
        </div>
      </n-scrollbar>
      <!--未启动-->
      <div
        v-if="nginxStatus === 'stop' && !loading"
        class="control-start"
        :style="{ height: windowHeight - 200 + 'px' }"
      >
        <img class="control-start-img" src="@/assets/start.png" />
        <p class="control-start-txt">{{ t('Nginx尚未启动，请点击启动') }}</p>
        <n-button
          type="primary"
          text-color="var(--jm-accent-7)"
          @click="handleAction('start', t('启动'))"
        >
          {{ t('启动Nginx') }}
        </n-button>
      </div>
    </n-spin>
  </page-container-layout>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  import { onActivated, ref } from 'vue';
  import { useApp, naiveui } from 'gm-app-components';
  import { getNginxLoadApi, getNginxStatusApi, nginxActionApi } from '@/api';
  import PageContainerLayout from '@/layout/PageContainerLayout.vue';
  import { VersionInfoType } from '@/types/type';

  const { t } = useI18n();
  const loading = ref(true);
  const loadInfo = ref<any>();
  const { windowHeight } = useApp();
  const nginxStatus = ref('');

  const props = defineProps<{
    getInstalledVersion: () => void;
    currentVersion: VersionInfoType;
  }>();

  const handleAction = (action: string, text: string) => {
    naiveui.dialog.warning({
      maskClosable: false,
      title: t('警告'),
      content: `${t('您确定要{XXX}nginx服务吗', { text })}`,
      positiveText: `${t('确定')}(Y)`,
      negativeText: `${t('取消')}(N)`,
      class: 'dialog-warning',
      onPositiveClick: () => {
        loading.value = true;
        nginxActionApi({ action })
          .then((res) => {
            naiveui.message.success(res.msg);
            getNginxStatus();
          })
          .catch(() => {
            loading.value = false;
          });
      },
    });
  };

  /**
   * 获取nginx运行状态
   */
  const getNginxStatus = () => {
    loading.value = true;
    getNginxStatusApi()
      .then((res) => {
        nginxStatus.value = res?.data?.status;
        if (nginxStatus.value === 'start') {
          getNginxLoad();
        } else {
          loading.value = false;
        }
      })
      .catch(() => {
        loading.value = false;
      });
  };

  /**
   *获取nginx负载信息
   */
  const getNginxLoad = () => {
    getNginxLoadApi()
      .then((res) => {
        loadInfo.value = res?.data;
      })
      .finally(() => {
        loading.value = false;
      });
  };

  onActivated(() => {
    props.getInstalledVersion();
  });

  const getData = () => {
    getNginxStatus();
  };

  defineExpose({
    getData,
  });
</script>

<style lang="scss" scoped>
  .header-left {
    display: flex;
    align-items: center;
    line-height: 32px;
    .title {
      font-size: 18px;
      font-weight: bold;
    }
    .state {
      font-size: 14px;
      margin-left: 30px;
      display: flex;
      align-items: center;
      .state-txt {
        display: flex;
        align-items: center;
        .icon {
          margin-left: 3px;
        }
      }
      .state-open {
        color: var(--jm-success-color);
      }
      .state-off {
        color: var(--jm-warning-color);
      }
    }
  }

  .header-right {
    display: flex;
    line-height: 32px;
    .opr-btn {
      width: 32px;
      height: 32px;
      border: 1px solid var(--jm-accent-4);
      border-radius: 5px;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: row;
      flex-wrap: nowrap;
      cursor: pointer;
      margin-left: 10px;
      margin-left: 10px;
      // &:hover {
      //   color: #fff;
      //   border-color: var(--jm-accent-7);
      // }
    }
  }

  .console-content {
    .console-title {
      font-size: 14px;
      font-weight: bold;
      color: #fff;
      margin-bottom: 20px;
    }

    .console-list {
      .console-item {
        display: flex;
        font-size: 14px;
        .console-item-col {
          flex: 1;
          // height: 44px;
          padding: 11px 20px;
          color: #fff;
          font-size: 14px;
          background-color: rgba(34, 34, 34, 1);
          margin-bottom: 1px;
        }
        .title {
          margin-right: 1px;
        }
      }

      .console-item:first-child {
        .title {
          border-top-left-radius: 4px;
        }
        .value {
          border-top-right-radius: 4px;
        }
      }

      .console-item:last-child {
        .title {
          border-bottom-left-radius: 4px;
        }
        .value {
          border-bottom-right-radius: 4px;
        }
      }
    }
  }

  .control-start {
    background: var(--jm-accent-1);
    padding: 0 20px 40px 20px;
    @include flex(center, center, column);
    &-img {
      width: 62px;
    }
    &-txt {
      font-size: 13px;
      color: var(--jm-accent-5);
      margin: 20px 0;
    }
  }
</style>

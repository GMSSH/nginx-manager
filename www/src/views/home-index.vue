<template>
  <div class="main">
    <Sidebar router-store="console" default-path="console" :menus="menus">
      <template v-if="isManager" #footer>
        <n-popover trigger="hover" raw :show-arrow="false" placement="top">
          <template #trigger>
            <div class="nginx-version">
              <div class="nginx-title">{{ t('版本管理') }}</div>
              <div class="nginx-version-change" @click="openVersionDetail">
                <n-popover trigger="hover">
                  <template #trigger>
                    <div class="version-name">
                      {{ currentVersion?.version }}
                    </div>
                  </template>
                  {{ currentVersion?.version }}
                </n-popover>
                <svg-icon icon="icon-qiehuan" color="var(--jm-accent-7)" />
              </div>
            </div>
          </template>
        </n-popover>
      </template>
    </Sidebar>
    <n-spin :show="false">
      <keep-alive>
        <component
          :is="isManager ? currentComponent : Null"
          ref="conpRef"
          :container-loading="containerLoading"
          :current-version="currentVersion"
          :get-installed-version="getInstalledVersion"
          @handle-select-version="handleChangeManageVersion"
        />
      </keep-alive>
    </n-spin>

    <batch-operation ref="batchOperationRef" />
    <CheckInstall
      v-model:visibly="checkInstallVisibly"
      @open-install="handleOpenInstall"
    />
    <SelectVersion
      v-model:visibly="selectVersionVisibly"
      :form-state="currentVersion"
      @select-version="handleChangeManageVersion"
      @set-manager="handleSetManager"
    />
    <VersionInfo
      v-model:visibly="versionInfoVisibly"
      :manage-version="currentVersion"
      @change-manage-version="handleChangeManageVersion"
      @uninstall="handleUninstall"
    />
    <NginxInstall
      v-model:visibly="nginxInstallVisibly"
      :current-version="currentVersion"
      :type="nginxInstallType"
      @start-install="handleStartInstall"
    />
    <NginxLoading ref="nginxLoadingRef" @stop-task="handleStopTask" />
  </div>
</template>
<script setup lang="ts">
  import {
    BatchOperation,
    Sidebar,
    useRouteStore,
    naiveui,
  } from 'gm-app-components';
  import Null from './home-null.vue';
  import { useI18n } from 'vue-i18n';
  import { computed, onMounted, ref, nextTick } from 'vue';
  import Log from '@/views/log/log.vue';
  import Console from '@/views/console/console.vue';
  import Setting from '@/views/setting/setting.vue';
  import CheckInstall from '@/components/CheckInstall.vue';
  import SelectVersion from '@/components/SelectVersion.vue';
  import NginxInstall from '@/components/NginxInstall.vue';
  import VersionInfo from '@/components/VersionInfo.vue';
  import NginxLoading from '@/components/NginxLoading.vue';
  import { VersionInfoType } from '@/types/type';
  import { getInstalledNginxApi } from '@/api';

  const { t } = useI18n();
  const routeStore = useRouteStore('console');
  // eslint-disable-next-line vue/return-in-computed-property
  const currentComponent = computed(() => {
    switch (routeStore.route) {
      case 'console':
        return Console; // 控制台
      case 'log':
        return Log; // 日志
      case 'setting':
        return Setting; // 配置调整
    }
  });
  const menus = [
    { label: t('控制台'), icon: 'icon-kongzhitai', path: 'console' },
    { label: t('配置调整'), icon: 'icon-peizhi', path: 'setting' },
    { label: t('日志'), icon: 'icon-a-List-viewliebiaoshitu', path: 'log' },
  ];
  const isManager = ref(false); // 是否管理对应nginx版本
  const nginxInstallVisibly = ref(false); // nginx安装弹窗
  const nginxInstallType = ref('auto');
  const checkInstallVisibly = ref(false); // 扫描安装弹窗
  const selectVersionVisibly = ref(false); // 选择版本弹窗
  const versionInfoVisibly = ref(false); // 版本信息弹窗
  const currentVersion = ref<VersionInfoType>(currentVersionInit()); // 当前版本
  const nginxLoadingRef = ref();
  function currentVersionInit() {
    return {
      version: '',
      bin_path: '',
      config_path: '',
      manager: 0, // 0 未管理 1 已管理
      install_type: '', // compile-编译 package-极速 manual-扫描到的/手动选择的
    };
  }
  const containerLoading = ref(true);
  const conpRef = ref();

  /**
   * 查看版本详情
   */
  const openVersionDetail = () => {
    versionInfoVisibly.value = true;
  };

  /**
   * 切换版本
   */
  const handleChangeManageVersion = () => {
    nginxInstallType.value = 'auto';
    // 打开安装弹窗
    nginxInstallVisibly.value = true;
  };

  /**
   * 初始化
   */
  const initData = (data) => {
    containerLoading.value = false;
    // selectVersionVisibly.value = true;
    // 未被管理
    if (data?.manager == 0) {
      isManager.value = false;
      if (data?.version) {
        // 已安装
        selectVersionVisibly.value = true;
        currentVersion.value = data;
      } else {
        // 未安装
        checkInstallVisibly.value = true;
      }
    } else {
      // 已被管理
      isManager.value = true;
      currentVersion.value = data;
      nextTick(() => {
        conpRef.value?.getData?.();
      });
    }
  };

  /**
   * 开始安装
   */
  const handleStartInstall = () => {
    localStorage.setItem(
      'NginxLoading',
      JSON.stringify({
        loadingType: 'install',
        loadingText: t('安装中...'),
        loadingStopText: t('停止安装'),
        loadingErrorText: t('安装失败'),
      })
    );
    nginxLoadingRef.value.startTask({
      init: () => {
        return false;
      },
      success: ({ data }) => {
        // 关闭选择安装弹窗
        nginxInstallVisibly.value = false;
        // 安装成功
        initData(data);
        naiveui.message.success(t('安装成功'));
      },
      fail: () => {
        // 安装失败
        // naiveui.message.error(t('安装失败'));
      },
    });
  };

  /**
   * 开始卸载
   */
  const handleUninstall = () => {
    localStorage.setItem(
      'NginxLoading',
      JSON.stringify({
        loadingType: 'uninstall',
        loadingText: t('卸载中...'),
        loadingStopText: t('停止卸载'),
        loadingErrorText: t('卸载失败'),
      })
    );
    nginxLoadingRef.value.startTask({
      init: () => {
        return false;
      },
      success: ({ data }) => {
        // isManager.value = false;
        versionInfoVisibly.value = false;
        nginxInstallVisibly.value = false;
        initData(data);
        naiveui.message.success(t('卸载成功'));
      },
      fail: () => {
        // 卸载失败
        // naiveui.message.error(t('卸载失败'));
      },
    });
  };

  /**
   * 打开安装弹窗
   */
  const handleOpenInstall = (data) => {
    nginxInstallType.value = data.type;
    nginxInstallVisibly.value = true;
  };

  /**
   * 初始化开启任务
   * **/
  const startTask = () => {
    containerLoading.value = true;
    nginxLoadingRef.value.startTask({
      init: () => {
        return true;
      },
      success: ({ data }) => {
        initData(data);
        containerLoading.value = false;
      },
      fail: () => {
        containerLoading.value = false;
      },
    });
  };

  const getInstalledVersion = () => {
    getInstalledNginxApi().then((res) => {
      initData(res?.data);
    });
  };

  const handleSetManager = () => {
    getInstalledVersion();
  };

  const handleStopTask = () => {
    getInstalledVersion();
  };

  onMounted(() => {
    startTask();
  });
</script>
<style lang="scss" scoped>
  .main {
    display: flex;
    width: 100%;
    &-handle {
      cursor: pointer;
      @include flex(flex-start);
      height: 42px;
      background: var(--jm-accent-1);
      border-radius: 8px;
      margin-bottom: 25px;
      box-sizing: border-box;
      padding: 0 8px;
      &-title {
        color: var(--jm-accent-7);
        font-size: 12px;
        margin-left: 8px;
        white-space: nowrap;
      }
      &-status {
        margin-left: auto;
        font-size: 12px;
        white-space: nowrap;
      }
    }
    :deep(.n-spin-container) {
      flex: 1;
    }
    :deep(.sidebar) {
      .sidebar-icon {
        svg {
          width: 16px;
        }
      }
      .sidebar-menu {
        ul {
          li {
            padding: 14px;
            .cate {
              padding-left: 7px;
            }
          }
        }
      }
    }
  }
</style>
<style lang="scss">
  .nginx-version {
    margin-bottom: 30px;
    width: 130px;
    .nginx-title {
      font-size: 14px;
      margin-bottom: 11px;
      color: var(--jm-accent-7);
    }

    .nginx-version-change {
      height: 34px;
      background: var(--jm-theme);
      border-radius: 4px 4px 4px 4px;
      border: 1px solid var(--jm-accent-4);
      color: var(--jm-accent-7);
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-sizing: border-box;
      padding: 0 10px;
      font-size: 12px;
      cursor: pointer;

      .version-name {
        width: 125px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }
  }
</style>

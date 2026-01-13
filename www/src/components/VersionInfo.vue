<template>
  <modal-layout :show="visibly" @after-enter="afterEnter">
    <modal-form-layout
      :width="400"
      :title="t('版本信息')"
      :confirm-text="t('切换版本')"
      :cancel-text="
        manageVersion?.install_type == 'manual' ? t('取消') : t('卸载')
      "
      @on-cancel="handleCancel"
      @on-confirm="handleConfirm"
    >
      <div class="modal-body">
        <n-form
          ref="formRef"
          :show-require-mark="false"
          label-placement="top"
          size="small"
        >
          <n-form-item :label="$t('版本号')">
            <n-input style="width: 350px" :value="formState.version" />
          </n-form-item>
          <n-form-item :label="$t('安装路径')">
            <n-input style="width: 350px" :value="formState.bin_path" />
          </n-form-item>
          <n-form-item :label="$t('配置文件')">
            <n-input style="width: 350px" :value="formState.config_path" />
          </n-form-item>
        </n-form>
      </div>
    </modal-form-layout>
  </modal-layout>
</template>
<script lang="ts" setup>
  const { t } = useI18n();
  import { ref } from 'vue';
  import { ModalFormLayout, ModalLayout, naiveui } from 'gm-app-components';
  import { useI18n } from 'vue-i18n';
  import { VersionInfoType } from '@/types/type';
  import { uninstallNginxApi } from '@/api';

  const props = defineProps<{
    visibly: boolean;
    manageVersion: VersionInfoType;
  }>();
  const formState = ref({
    version: '',
    bin_path: '',
    config_path: '',
  });
  const emit = defineEmits([
    'update:visibly',
    'changeManageVersion',
    'uninstall',
  ]);

  /**
   * 初始化弹窗
   */
  const afterEnter = () => {
    formState.value = {
      version: props.manageVersion?.version,
      bin_path: props.manageVersion?.bin_path,
      config_path: props.manageVersion?.config_path,
    };
  };

  /**
   * 确定
   */
  const handleConfirm = () => {
    emit('update:visibly', false);
    emit('changeManageVersion');
  };

  /**
   * 取消
   */
  const handleCancel = (data) => {
    if (!data) {
      emit('update:visibly', false);
      return;
    }
    const { done } = data;
    // 非管理器安装不卸载
    if (props?.manageVersion?.install_type == 'manual') {
      emit('update:visibly', false);
    } else {
      // 卸载
      naiveui.dialog.warning({
        maskClosable: false,
        title: t('警告'),
        content: `${t('您确定要卸载Nginx{XXX}吗', { text: formState.value?.version })}`,
        positiveText: `${t('确定')}(Y)`,
        negativeText: `${t('取消')}(N)`,
        class: 'dialog-warning',
        onPositiveClick: () => {
          uninstallNginxApi()
            .then(() => {
              emit('uninstall');
              // statusText.value = t('卸载');
            })
            .finally(() => {
              done();
            });
        },
        onNegativeClick: () => {
          done();
        },
        onClose: () => {
          done();
        },
      });
    }
  };
</script>
<style lang="scss" scoped>
  .modal-body {
    padding: 0 20px 0 20px;
    @include flex(center, center, column);
    &-img {
      width: 56px;
    }
    &-text {
      font-size: 13px;
      color: var(--jm-accent-7);
      text-align: center;
      margin-top: 20px;
      margin-bottom: 40px;
    }
    .version {
      @include flex(flex-start, flex-start);
      flex-wrap: wrap;
      &-item {
        width: 111px;
        height: 34px;
        background: var(--jm-theme);
        border-radius: 4px 4px 4px 4px;
        border: 1px solid var(--jm-accent-3);
        color: var(--jm-accent-7);
        text-align: center;
        line-height: 34px;
        cursor: pointer;
        margin-right: 9px;
        margin-bottom: 9px;
        &:nth-child(3n) {
          margin-right: 0;
        }
        &.active {
          background: var(--jm-primary-1);
          border: 1px solid var(--jm-primary-1);
        }
      }
    }
  }
</style>

<template>
  <modal-layout :show="visibly" @after-enter="afterEnter">
    <modal-form-layout
      :width="400"
      :title="t('文件扫描')"
      :confirm-text="t('安装nginx')"
      :cancel-text="t('手动选择')"
      @on-cancel="handleCancel"
      @on-confirm="handleConfirm"
    >
      <div class="modal-body">
        <div class="modal-body-none">
          <img class="modal-body-img" src="@/assets/null.png" alt="" />
          <p class="modal-body-text">{{ t('未扫描到nginx') }}</p>
        </div>
      </div>
    </modal-form-layout>
  </modal-layout>
</template>
<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { ModalFormLayout, ModalLayout } from 'gm-app-components';

  const { t } = useI18n();
  defineProps<{
    visibly: boolean;
  }>();
  const emit = defineEmits(['update:visibly', 'openInstall']);

  const afterEnter = () => {};

  const handleConfirm = () => {
    emit('update:visibly', false);
    emit('openInstall', {
      type: 'auto',
    });
  };

  const handleCancel = (data) => {
    emit('update:visibly', false);
    if (data) {
      emit('openInstall', {
        type: 'hand',
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
      color: var(--jm-accent-5);
      text-align: center;
      margin-top: 20px;
      margin-bottom: 40px;
    }
    .modal-body-loading {
      text-align: center;
    }
    .modal-body-none {
      text-align: center;
    }
  }
</style>

<template>
  <modal-layout :show="visibly" :auto-focus="false" @after-enter="afterEnter">
    <n-spin :show="loading">
      <modal-form-layout
        :width="400"
        :title="t('选择版本')"
        :confirm-text="t('确认')"
        :cancel-text="t('切换版本')"
        @on-cancel="handleCancel"
        @on-confirm="submit"
      >
        <div class="modal-body">
          <n-form
            ref="formRef"
            :show-require-mark="false"
            label-placement="top"
            size="small"
          >
            <n-form-item :label="t('版本号')">
              <n-input style="width: 350px" :value="form.version" />
            </n-form-item>
            <n-form-item :label="t('安装路径')">
              <n-input style="width: 350px" :value="form.bin_path" />
            </n-form-item>
            <n-form-item :label="t('配置文件')">
              <n-input style="width: 350px" :value="form.config_path" />
            </n-form-item>
          </n-form>
        </div>
      </modal-form-layout>
    </n-spin>
  </modal-layout>
</template>
<script lang="ts" setup>
  import { ref, toRaw } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { ModalFormLayout, ModalLayout, naiveui } from 'gm-app-components';
  import { setNginxVersionApi } from '@/api';

  const { formState } = defineProps<{
    visibly: boolean;
    formState: FormState;
  }>();
  const { t } = useI18n();
  type FormState = {
    version: string;
    bin_path: string;
    config_path: string | undefined;
  };
  const form = ref<FormState>({
    version: '',
    bin_path: '',
    config_path: '',
  });
  const loading = ref(false);

  const emit = defineEmits(['update:visibly', 'selectVersion', 'setManager']);

  const afterEnter = () => {
    form.value = toRaw(formState);
  };

  const submit = async ({ done }) => {
    setNginxVersionApi({
      set_type: 'auto',
      version: form.value.version,
      bin_path: form.value.bin_path,
      config_path: form.value.config_path as string,
    })
      .then((res) => {
        naiveui.message.success(res?.msg);
        emit('setManager');
        emit('update:visibly', false);
      })
      .catch(() => {
        done();
      });
  };

  const handleCancel = (data) => {
    emit('update:visibly', false);
    if (!data) {
      return;
    }
    emit('selectVersion');
  };
</script>
<style lang="scss" scoped>
  .modal-body {
    padding: 0 20px 0 20px;
    @include flex(center, center, column);
  }
</style>

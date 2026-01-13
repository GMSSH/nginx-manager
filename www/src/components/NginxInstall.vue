<template>
  <modal-layout :show="visibly" @after-enter="afterEnter">
    <modal-form-layout
      :width="400"
      :title="t('安装Nginx')"
      @on-cancel="closeModal"
      @on-confirm="submit"
    >
      <div class="modal-body">
        <div class="config-tabs">
          <div
            v-for="(item, index) in tabs"
            :key="item.label"
            :class="[
              'config-tabs-item',
              currentIndex == index ? 'active' : '',
              (index == 0 && currentIndex == 2) ||
              (index == 1 && currentIndex == 0)
                ? 'vertical'
                : '',
              index == 0 ? `config-tabs-item-${locale}` : '',
            ]"
            @click="
              form = defaultData();
              currentIndex = index;
              formRef?.restoreValidation?.();
            "
          >
            {{ item.label }}
            <n-tooltip
              v-if="[0, 1].includes(index)"
              placement="top-start"
              trigger="hover"
            >
              <template #trigger>
                <svg-icon
                  style="margin-left: 4px; position: relative; z-index: 2"
                  color="var(--jm-accent-5)"
                  font-size="13px"
                  icon="icon-systemInfo"
                />
              </template>
              <div v-if="!index" style="font-size: 12px">
                {{
                  t(
                    '从源码编译优化，性能最佳，稳定性更强，但安装较慢，适合生产环境。'
                  )
                }}
              </div>
              <div v-else style="font-size: 12px">
                {{
                  t(
                    '预编译二进制包，安装极快，但版本和稳定性略低，适合快速部署测试。'
                  )
                }}
              </div>
            </n-tooltip>
          </div>
        </div>
        <n-form
          ref="formRef"
          :label-width="90"
          :model="form"
          :rules="rules"
          :show-require-mark="false"
          label-placement="left"
          size="small"
        >
          <n-form-item
            v-if="currentIndex == 0 || currentIndex == 1"
            :label="t('Nginx版本')"
            path="version"
          >
            <n-select
              v-model:value="form.version"
              :placeholder="t('请选择')"
              clearable
              filterable
              style="width: 280px"
              :render-label="renderLabel"
              :options="currentIndex == 0 ? compiledOptions : extremeOptions"
            >
              <template #empty>
                <n-spin v-if="loading" size="small" />
                <span v-else><n-empty /></span>
              </template>
            </n-select>
          </n-form-item>
          <template v-if="currentIndex == 2">
            <n-form-item :label="t('安装路径')" path="bin_path">
              <select-directory v-model:value="form.bin_path" type="file" />
            </n-form-item>
            <n-form-item :label="t('配置文件')" path="config_path">
              <select-directory v-model:value="form.config_path" type="file" />
            </n-form-item>
          </template>
        </n-form>

        <div class="modal-body-txt">
          {{ t('注意：切换版本可能会导致应用数据丢失！！！') }}
        </div>
      </div>
    </modal-form-layout>
  </modal-layout>
</template>
<script lang="ts" setup>
  import {
    ModalFormLayout,
    ModalLayout,
    SelectDirectory,
  } from 'gm-app-components';
  import { useI18n } from 'vue-i18n';
  import { ref, watch, h } from 'vue';
  // import { throttle } from 'lodash-es';
  import { FormInst, FormRules, NText, NTooltip } from 'naive-ui';
  import {
    getNginxVersionApi,
    installNginxApi,
    setNginxVersionApi,
  } from '@/api';
  import { locale } from '@/utils';

  const { t } = useI18n();

  const emit = defineEmits(['update:visibly', 'startInstall']);
  const props = withDefaults(
    defineProps<{
      visibly: boolean;
      type?: string;
    }>(),
    {
      type: 'auto',
    }
  );
  const rules: FormRules = {
    version: {
      required: true,
      trigger: ['blur', 'change'],
      message: t('请选择'),
    },
    bin_path: {
      required: true,
      message: t('请输入'),
    },
    config_path: {
      required: true,
      message: t('请输入'),
    },
  };
  const formRef = ref<FormInst | null>(null); // 表单实例
  const form = ref(defaultData()); // 初始化表单数据
  const tabs = [
    {
      label: t('编译安装'),
    },
    {
      label: t('极速安装'),
    },
    {
      label: t('手动选择'),
    },
  ]; // 选项卡
  const currentIndex = ref(0); // 当前选项卡索引
  const compiledOptions = ref<{ label: string; value: string }[]>([]); // 编译安装选项
  const extremeOptions = ref<{ label: string; value: string }[]>([]); // 极速安装选项
  const loading = ref(false);

  watch(
    () => props.type,
    (val) => {
      currentIndex.value = val == 'hand' ? 2 : 0;
    }
  );

  /**
   * 组件进入后初始化数据
   * **/
  const afterEnter = () => {
    form.value = defaultData();
    getVersions();
  };

  /**
   * 获取版本列表
   */
  const getVersions = () => {
    loading.value = true;
    getNginxVersionApi()
      .then((res: any) => {
        if (res.code == 200) {
          compiledOptions.value = res?.data?.compile_version?.data?.map(
            (item: any) => ({
              label: item.name,
              value: item.version,
            })
          );
          extremeOptions.value = res?.data?.package_version?.map(
            (item: any) => ({
              label: item.name,
              value: item.version,
            })
          );
        }
      })
      .finally(() => {
        loading.value = false;
      });
  };

  const closeModal = () => {
    emit('update:visibly', false);
  };

  /**
   * 提交表单
   * **/
  const submit = async ({ done }) => {
    formRef.value?.validate((errors) => {
      if (!errors) {
        if (currentIndex.value == 2) {
          setNginxVersionApi({
            bin_path: form.value.bin_path,
            config_path: form.value.config_path,
            set_type: 'manual',
          })
            .then(() => {
              emit('startInstall');
              done();
            })
            .catch(() => {
              done();
            });
          return;
        }
        installNginxApi({
          install_type: currentIndex.value == 0 ? 'compile' : 'package',
          version: form.value.version ? form.value.version : '',
        })
          .then(() => {
            emit('startInstall');
            done();
          })
          .catch(() => {
            done();
          });
      } else {
        done();
      }
    });
  };

  /**
   * 表单默认数据
   */
  function defaultData() {
    return {
      version: null,
      bin_path: '',
      config_path: '',
    };
  }

  // const handleThrottle = throttle((data) => {
  //   submit(data);
  // }, 1000, {
  //   trailing: false,
  // });
  const renderLabel = (option: any) => {
    return h(
      NTooltip,
      {
        trigger: 'hover',
        placement: 'top-start',
      },
      {
        trigger: () =>
          h(
            'div',
            {
              style: {
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '200px',
              },
            },
            option.label
          ),
        default: () => h(NText, { depth: 3 }, () => option.label),
      }
    );
  };
</script>
<style lang="scss" scoped>
  .modal-body {
    padding: 0 20px 0 20px;

    .config-tabs {
      display: inline-flex;
      margin-bottom: 40px;
      border-radius: 4px 4px 4px 4px;
      border: 1px solid var(--jm-accent-3);

      &-item {
        /* width: 76px; */
        flex-basis: auto;
        display: flex;
        align-items: center;
        padding: 0 16px;
        height: 30px;
        font-size: 12px;
        text-align: center;
        line-height: 30px;
        box-sizing: border-box;
        border: 1px solid transparent;
        position: relative;
        //top: -1px;
        border-bottom: 0;
        transition: all 0.3s;
        cursor: pointer;
        border-radius: 3px;
        color: var(--jm-accent-7);

        &.active {
          background: var(--jm-accent-3);
        }

        &.vertical {
          &:after {
            content: '';
            position: absolute;
            width: 1px;
            height: 20px;
            background: var(--jm-accent-3);
            right: -2px;
            top: 50%;
            transform: translateY(-50%);
          }
        }
      }
      .config-tabs-item.config-tabs-item-zh-CN {
        &::before {
          content: '';
          position: absolute;
          right: -1px;
          top: -1px;
          width: 24px;
          height: 24px;
          background: url('@/assets/re.png') right top no-repeat;
          background-size: contain;
        }
      }
      .config-tabs-item.config-tabs-item-en {
        &::before {
          content: '';
          position: absolute;
          right: -1px;
          top: -1px;
          width: 24px;
          height: 24px;
          background: url('@/assets/en.png') right top no-repeat;
          background-size: contain;
        }
      }
    }

    &-txt {
      color: rgba(240, 77, 60, 1);
      font-size: 12px;
    }
  }
</style>

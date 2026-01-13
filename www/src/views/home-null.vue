<template>
  <n-spin :show="false">
    <div
      v-if="!containerLoading"
      class="main"
      :style="{
        height: `${(windowHeight as number) - 185}px`,
        width: `${(containerWidth as number) - 20}px`,
      }"
    >
      <img class="main-img" src="@/assets/null.png" alt="" />
      <p class="main-txt">{{ t('检测到您未安装nginx，请选择版本') }}</p>
      <n-button
        type="primary"
        text-color="var(--jm-accent-7)"
        @click="emit('handleSelectVersion')"
      >
        {{ t('请选择') }}
      </n-button>
    </div>
  </n-spin>
</template>
<script setup lang="ts">
  import { useApp } from 'gm-app-components';
  import { useDynamicContainerWidth } from '@/hooks';
  import { useI18n } from 'vue-i18n';

  defineProps({
    containerLoading: {
      type: Boolean,
      default: false,
    },
  });

  const { t } = useI18n();
  const containerWidth = useDynamicContainerWidth();
  const { windowHeight } = useApp();
  const emit = defineEmits(['handleSelectVersion']);
</script>
<style lang="scss" scoped>
  .main {
    padding-top: 20px;
    @include flex(center, center, column);
    &-img {
      width: 62px;
    }
    &-txt {
      margin: 20px 0;
      font-size: 13px;
      color: var(--jm-accent-5);
    }
  }
</style>

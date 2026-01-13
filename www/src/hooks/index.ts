import { useElementSize } from '@vueuse/core';
import { useApp } from 'gm-app-components';
import { onMounted, ref, toRaw } from 'vue';

export const useDynamicContainerWidth = () => {
  const { windowWidth } = useApp();
  const sidebarWidth = ref(0);
  onMounted(() => {
    const { width } = useElementSize(
      document.querySelector('.sidebar') as HTMLElement
    );
    watch([width, windowWidth], (val) => {
      sidebarWidth.value = toRaw(val[1]) - toRaw(val[0]) - 50;
    });
  });

  return sidebarWidth;
};

export const serveStatus = ref(3);
export const levelName1 = ref('');
export const levelName2 = ref('');
export const repoId = ref<undefined | string>(undefined);
export const containerLoading = ref(false);

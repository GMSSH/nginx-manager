<template>
  <!-- <container-layout> -->
  <!--    需要调用init（checkstatus接口）的时候放开注释-->
  <container-layout loading @done="show = true">
    <main-view v-if="show" />
  </container-layout>
</template>
<script setup lang="ts">
  import mainView from '@/views/home-index.vue';
  import { ref } from 'vue';
  import { ContainerLayout } from 'gm-app-components';

  // 控制主视图显示状态 需要调用init（checkstatus接口）的时候默认为false
  const show = ref(false);
</script>
<style lang="scss" scoped></style>

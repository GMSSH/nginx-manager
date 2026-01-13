<template>
  <div class="container">
    <div class="container-header">
      <slot name="header"></slot>
    </div>
    <div class="container-body">
      <slot></slot>
    </div>
    <div class="container-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>
<script setup lang="ts">
  defineProps<{
    title: string;
  }>();
</script>
<style scoped lang="scss">
  .container {
    height: 100vh;
    box-sizing: border-box;
    margin-left: 30px;
    margin-right: 30px;
    flex: 1;
    @include flex(flex-start, center, column);
    &-header {
      width: 100%;
      height: 34px;
      font-weight: 600;
      font-size: 20px;
      color: var(--jm-accent-7);
      margin-top: 30px;
      margin-bottom: 20px;
    }
    &-body {
      width: 100%;
      flex: 1;
    }
    &-footer {
      width: 100%;
      margin-bottom: 30px;
    }
  }
</style>

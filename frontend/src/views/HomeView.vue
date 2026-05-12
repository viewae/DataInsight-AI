<script setup lang="ts">
import { onMounted, ref } from "vue";
import axios from "axios";

const health = ref<string>("…");

onMounted(async () => {
  try {
    const { data } = await axios.get("/health");
    health.value = JSON.stringify(data);
  } catch {
    health.value = "后端未启动或代理不可用";
  }
});
</script>

<template>
  <el-container class="page">
    <el-header>
      <h1>DataInsight AI</h1>
    </el-header>
    <el-main>
      <el-card shadow="hover">
        <template #header>开发骨架</template>
        <p>前端：Vue3 + TypeScript + Element Plus（ECharts 已列入依赖，按需引入即可）</p>
        <p>
          后端健康检查（经 Vite 代理 <code>/health</code>）：
          <code>{{ health }}</code>
        </p>
      </el-card>
    </el-main>
  </el-container>
</template>

<style scoped>
.page {
  min-height: 100%;
}
h1 {
  margin: 0;
  font-size: 1.25rem;
}
</style>

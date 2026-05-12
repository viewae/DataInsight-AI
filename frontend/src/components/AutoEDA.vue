<script setup lang="ts">
import { ref, onMounted } from "vue";
import { apiClient } from "@/api/client";

const props = defineProps<{
  datasetId: number;
}>();

const emit = defineEmits<{
  (e: "close"): void;
}>();

interface ColumnStat {
  name: string;
  dtype: string;
  missing: number;
  unique: number;
  [key: string]: unknown;
}

interface EDAResult {
  summary: string;
  column_stats: ColumnStat[];
  correlations: { col1: string; col2: string; value: number }[];
  warnings: string[];
}

const result = ref<EDAResult | null>(null);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await apiClient.post<EDAResult>("/ai/auto-eda", {
      dataset_id: props.datasetId,
    });
    result.value = data;
  } catch {
    // LLM 不可用时静默关闭，不阻塞用户操作
    emit("close");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="auto-eda" v-loading="loading">
    <div class="eda-header">
      <h3>数据概览</h3>
      <el-button size="small" text @click="emit('close')">
        <el-icon><close /></el-icon>
      </el-button>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable />

    <div v-if="result" class="eda-body">
      <el-card shadow="never" class="eda-summary">
        <p>{{ result.summary }}</p>
      </el-card>

      <el-card v-if="result.warnings.length" shadow="never" class="eda-warnings">
        <template #header>
          <span style="color: #e6a23c">⚠ 数据质量提醒</span>
        </template>
        <ul>
          <li v-for="(w, i) in result.warnings" :key="i">{{ w }}</li>
        </ul>
      </el-card>

      <el-card shadow="never" class="eda-columns">
        <template #header>列统计</template>
        <el-table :data="result.column_stats" size="small" stripe>
          <el-table-column prop="name" label="列名" />
          <el-table-column prop="dtype" label="类型" width="100" />
          <el-table-column prop="unique" label="唯一值" width="80" />
          <el-table-column prop="missing" label="缺失" width="80" />
        </el-table>
      </el-card>

      <el-card v-if="result.correlations.length" shadow="never" class="eda-corr">
        <template #header>相关性</template>
        <el-table :data="result.correlations" size="small" stripe>
          <el-table-column prop="col1" label="列1" />
          <el-table-column prop="col2" label="列2" />
          <el-table-column prop="value" label="相关系数" width="120">
            <template #default="{ row }">
              <el-tag :type="Math.abs(row.value) > 0.5 ? 'primary' : 'info'" size="small">
                {{ row.value.toFixed(3) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.auto-eda {
  margin-bottom: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
}
.eda-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #e6e6e6;
}
.eda-header h3 {
  margin: 0;
  font-size: 14px;
}
.eda-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.eda-summary {
  font-size: 14px;
  line-height: 1.6;
}
.eda-warnings ul {
  margin: 0;
  padding-left: 20px;
}
.eda-warnings li {
  font-size: 13px;
  line-height: 1.8;
}
</style>

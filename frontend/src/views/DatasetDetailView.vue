<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { apiClient } from "@/api/client";
import { useDatasetStore } from "@/stores/dataset";

const route = useRoute();
const router = useRouter();
const store = useDatasetStore();

const datasetId = Number(route.params.id);
const previewColumns = ref<string[]>([]);
const previewRows = ref<Record<string, unknown>[]>([]);
const loading = ref(true);
const creating = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    await store.fetchDetail(datasetId);
    const data = await store.fetchPreview(datasetId);
    if (data) {
      previewColumns.value = data.columns;
      previewRows.value = data.rows;
    }
  } catch {
    ElMessage.error("加载数据集详情失败");
  } finally {
    loading.value = false;
  }
});

async function startAnalysis() {
  creating.value = true;
  try {
    const { data } = await apiClient.post("/session/create", { dataset_id: datasetId });
    router.push(`/analysis/${data.id}`);
  } catch {
    ElMessage.error("创建分析会话失败");
  } finally {
    creating.value = false;
  }
}
</script>

<template>
  <div class="dataset-detail" v-loading="loading">
    <!-- Navigation header -->
    <div class="detail-header">
      <el-button @click="router.push('/datasets')" class="back-btn" text>
        <el-icon><arrow-left /></el-icon>
        返回列表
      </el-button>
      <h2 v-if="store.current">{{ store.current.name }}</h2>
      <el-button
        v-if="store.current"
        type="primary"
        :loading="creating"
        @click="startAnalysis"
      >
        <el-icon><data-analysis /></el-icon>
        开始分析
      </el-button>
    </div>

    <!-- Metadata card -->
    <el-card v-if="store.current" shadow="hover" class="detail-card">
      <template #header>
        <div class="card-title">
          <el-icon :size="16"><info-filled /></el-icon>
          <span>元数据</span>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="名称">{{ store.current.name }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ store.current.source_type }}</el-descriptions-item>
        <el-descriptions-item label="行数">{{ store.current.row_count }}</el-descriptions-item>
        <el-descriptions-item label="列数">
          {{ store.current.columns_meta?.length || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" type="success" effect="plain">已导入</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Columns info card -->
    <el-card v-if="store.current" shadow="hover" class="detail-card">
      <template #header>
        <div class="card-title">
          <el-icon :size="16"><list /></el-icon>
          <span>列信息</span>
        </div>
      </template>
      <el-table :data="store.current.columns_meta" stripe size="small">
        <el-table-column prop="name" label="列名" />
        <el-table-column prop="dtype" label="数据类型" />
      </el-table>
    </el-card>

    <!-- Data preview card -->
    <el-card v-if="previewColumns.length" shadow="hover" class="detail-card">
      <template #header>
        <div class="card-title">
          <el-icon :size="16"><view /></el-icon>
          <span>数据预览（前 {{ previewRows.length }} 行）</span>
        </div>
      </template>
      <div class="preview-table">
        <el-table :data="previewRows" stripe border size="small" max-height="500px">
          <el-table-column
            v-for="col in previewColumns"
            :key="col"
            :prop="col"
            :label="col"
            min-width="130"
          />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.dataset-detail {
  padding: 0;
}

/* ── Header ── */
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  background: #fff;
  padding: 12px 20px;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.detail-header h2 {
  margin: 0;
  flex: 1;
  font-size: 18px;
  font-weight: 600;
}
.back-btn {
  font-size: 13px;
  color: #86909c;
}

/* ── Cards ── */
.detail-card {
  margin-bottom: 16px;
}
.detail-card:last-child {
  margin-bottom: 0;
}
.detail-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #f2f3f5;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #4e5969;
}
.card-title .el-icon {
  color: #409eff;
}

/* ── Preview table wrapper ── */
.preview-table {
  margin: -4px;
}
</style>

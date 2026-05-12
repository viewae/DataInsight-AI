<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { apiClient } from "@/api/client";

interface ReportOut {
  id: number;
  title: string;
  content: string | null;
  share_token: string | null;
  created_at: string;
}

const route = useRoute();
const router = useRouter();
const reportId = Number(route.params.id);
const report = ref<ReportOut | null>(null);
const loading = ref(true);

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await apiClient.get<ReportOut>(`/report/${reportId}`);
    report.value = data;
  } catch {
    ElMessage.error("加载报告失败");
  } finally {
    loading.value = false;
  }
});

async function download() {
  const token = localStorage.getItem("datainsight_token");
  const resp = await fetch(`/api/report/${reportId}/download`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resp.ok) { ElMessage.error("下载失败"); return; }
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `report_${reportId}.html`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <div class="report-detail" v-loading="loading">
    <!-- Header -->
    <div class="detail-header">
      <el-button @click="router.push('/reports')" class="back-btn" text>
        <el-icon><arrow-left /></el-icon>
        返回列表
      </el-button>
      <h2 v-if="report">{{ report.title }}</h2>
      <el-button v-if="report" type="primary" @click="download">
        <el-icon><download /></el-icon>
        下载 HTML
      </el-button>
    </div>

    <!-- Content card -->
    <el-card v-if="report" shadow="hover" class="report-card">
      <template #header>
        <div class="card-header">
          <div class="card-title">
            <el-icon :size="16"><document /></el-icon>
            <span>报告内容</span>
          </div>
          <span class="report-time">{{ report.created_at }}</span>
        </div>
      </template>
      <div class="report-body" v-if="report.content" v-html="report.content"></div>
      <el-empty v-else description="暂无报告内容" />
    </el-card>
  </div>
</template>

<style scoped>
.report-detail {
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

/* ── Card ── */
.report-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #f2f3f5;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.report-time {
  font-size: 13px;
  color: #86909c;
}

/* ── Report body ── */
.report-body {
  line-height: 1.8;
  color: #1d2129;
}
.report-body :deep(h1),
.report-body :deep(h2) {
  margin-top: 28px;
  margin-bottom: 12px;
  font-weight: 600;
}
.report-body :deep(h3) {
  margin-top: 20px;
  font-weight: 600;
}
.report-body :deep(p) {
  margin: 0 0 12px;
}
.report-body :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}
.report-body :deep(code) {
  background: #f5f7fa;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 13px;
}
.report-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 12px 0;
}
.report-body :deep(blockquote) {
  border-left: 3px solid #409eff;
  margin: 12px 0;
  padding: 8px 16px;
  background: #f5f8ff;
  border-radius: 0 6px 6px 0;
}
.report-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}
.report-body :deep(th),
.report-body :deep(td) {
  border: 1px solid #e5e6eb;
  padding: 8px 12px;
  text-align: left;
}
.report-body :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}
</style>

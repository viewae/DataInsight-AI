<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { apiClient } from "@/api/client";

interface ReportOut {
  id: number;
  title: string;
  content: string | null;
  created_at: string;
}

interface SessionItem {
  id: number;
  title: string | null;
  dataset_id: number | null;
}

const router = useRouter();
const reports = ref<ReportOut[]>([]);
const sessions = ref<SessionItem[]>([]);
const loading = ref(false);
const genDialog = ref(false);
const genSessionId = ref<number | null>(null);
const genTitle = ref("");
const generating = ref(false);

async function fetchReports() {
  loading.value = true;
  try {
    const { data } = await apiClient.get<ReportOut[]>("/report/list");
    reports.value = data;
  } catch {
    ElMessage.error("加载报告列表失败");
  } finally {
    loading.value = false;
  }
}

async function openGenerateDialog() {
  try {
    const { data } = await apiClient.get<SessionItem[]>("/session/list");
    sessions.value = data.filter((s) => s.dataset_id);
    genDialog.value = true;
  } catch {
    ElMessage.error("加载会话列表失败");
  }
}

async function generate() {
  if (!genSessionId.value) {
    ElMessage.warning("请选择会话");
    return;
  }
  generating.value = true;
  try {
    await apiClient.post("/report/generate", {
      session_id: genSessionId.value,
      title: genTitle.value || undefined,
    });
    ElMessage.success("报告生成成功");
    genDialog.value = false;
    genSessionId.value = null;
    genTitle.value = "";
    await fetchReports();
  } catch {
    ElMessage.error("生成报告失败");
  } finally {
    generating.value = false;
  }
}

async function download(id: number) {
  const token = localStorage.getItem("datainsight_token");
  const resp = await fetch(`/api/report/${id}/download`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resp.ok) { ElMessage.error("下载失败"); return; }
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `report_${id}.html`;
  a.click();
  URL.revokeObjectURL(url);
}

async function handleDelete(id: number, title: string) {
  try {
    await ElMessageBox.confirm(`确认删除报告「${title}」？`, "确认删除", { type: "warning" });
    await apiClient.delete(`/report/${id}`);
    ElMessage.success("删除成功");
    await fetchReports();
  } catch {
    // cancelled
  }
}

onMounted(fetchReports);
</script>

<template>
  <div class="report-list-page">
    <div class="page-header">
      <div>
        <h2>报告</h2>
        <p class="page-description">查看和管理分析报告</p>
      </div>
      <el-button type="primary" @click="openGenerateDialog" size="large">
        <el-icon><plus /></el-icon>
        生成报告
      </el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="reports" v-loading="loading" empty-text="暂无报告" stripe style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="260">
          <template #default="{ row }">
            <div class="cell-title">
              <el-icon :size="16"><document /></el-icon>
              {{ row.title }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="190" />
        <el-table-column label="操作" width="280" align="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/reports/${row.id}`)">查看</el-button>
            <el-button size="small" @click="download(row.id)">下载</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row.id, row.title)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="genDialog" title="从会话生成报告" width="520px" class="gen-dialog" top="15vh">
      <el-form label-position="top">
        <el-form-item label="报告标题（可选）">
          <el-input v-model="genTitle" placeholder="留空将自动生成标题" />
        </el-form-item>
        <el-form-item label="选择会话">
          <el-select v-model="genSessionId" placeholder="选择包含分析结果的会话" style="width: 100%">
            <el-option
              v-for="s in sessions"
              :key="s.id"
              :label="s.title || `会话 #${s.id}`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="genDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="generate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.report-list-page {
  padding: 0;
}
.page-description {
  margin: 4px 0 0;
  font-size: 14px;
  color: #86909c;
}
.cell-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #1d2129;
  font-weight: 500;
}
.cell-title .el-icon {
  color: #409eff;
}
</style>

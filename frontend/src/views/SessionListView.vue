<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { apiClient } from "@/api/client";

interface SessionItem {
  id: number;
  title: string | null;
  dataset_id: number | null;
  created_at: string;
}

const router = useRouter();
const sessions = ref<SessionItem[]>([]);
const loading = ref(false);

onMounted(fetchSessions);

async function fetchSessions() {
  loading.value = true;
  try {
    const { data } = await apiClient.get<SessionItem[]>("/session/list");
    sessions.value = data;
  } catch {
    ElMessage.error("加载会话列表失败");
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: number, title: string) {
  try {
    await ElMessageBox.confirm(`确认删除会话「${title}」？`, "确认删除", { type: "warning" });
    await apiClient.delete(`/session/${id}`);
    ElMessage.success("删除成功");
    await fetchSessions();
  } catch {
    // cancelled
  }
}

function formatTime(iso: string) {
  return iso.replace("T", " ").slice(0, 16);
}
</script>

<template>
  <div class="session-list-page">
    <div class="page-header">
      <div>
        <h2>分析会话</h2>
        <p class="page-description">查看和管理所有分析会话</p>
      </div>
    </div>

    <div class="table-wrapper">
      <el-table
        :data="sessions"
        v-loading="loading"
        empty-text="暂无会话，请先在数据集中开始分析"
        stripe
        style="width: 100%"
      >
        <el-table-column label="名称" min-width="260">
          <template #default="{ row }">
            <div class="cell-name">
              <el-icon :size="16"><chat-dot-square /></el-icon>
              {{ row.title || `会话 #${row.id}` }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="数据集 ID" width="120" align="center">
          <template #default="{ row }">{{ row.dataset_id || "-" }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="router.push(`/analysis/${row.id}`)">
              查看
            </el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row.id, row.title || `会话 #${row.id}`)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.session-list-page {
  padding: 0;
}
.page-description {
  margin: 4px 0 0;
  font-size: 14px;
  color: #86909c;
}
.cell-name {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #1d2129;
  font-weight: 500;
}
.cell-name .el-icon {
  color: #409eff;
}
</style>

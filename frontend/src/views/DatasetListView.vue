<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useDatasetStore } from "@/stores/dataset";
import { apiClient } from "@/api/client";
import DatasetUploadDialog from "@/components/DatasetUploadDialog.vue";

const router = useRouter();
const store = useDatasetStore();
const uploadDialog = ref<InstanceType<typeof DatasetUploadDialog> | null>(null);
const creating = ref<number | null>(null);

onMounted(() => store.fetchList());

async function handleUpload(file: File, name: string) {
  try {
    await store.upload(file, name || undefined);
    ElMessage.success("上传成功");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "上传失败");
  }
}

async function handleDelete(id: number, rowName: string) {
  try {
    await ElMessageBox.confirm(
      `确认删除数据集「${rowName}」？此操作不可撤销。`,
      "确认删除",
      { type: "warning" }
    );
    await store.remove(id);
    ElMessage.success("删除成功");
  } catch {
    // cancelled
  }
}

async function startAnalysis(id: number) {
  creating.value = id;
  try {
    const { data } = await apiClient.post("/session/create", { dataset_id: id });
    router.push(`/analysis/${data.id}`);
  } catch {
    ElMessage.error("创建分析会话失败");
  } finally {
    creating.value = null;
  }
}
</script>

<template>
  <div class="dataset-list-page">
    <div class="page-header">
      <div>
        <h2>数据集</h2>
        <p class="page-description">上传和管理你的数据文件</p>
      </div>
      <el-button type="primary" @click="uploadDialog?.open()" size="large">
        <el-icon><upload /></el-icon>
        上传数据集
      </el-button>
    </div>

    <div class="table-wrapper">
      <el-table
        :data="store.datasets"
        v-loading="store.loading"
        empty-text="暂无数据集，点击上方按钮上传"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <div class="cell-name">
              <el-icon :size="16"><document /></el-icon>
              {{ row.name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="source_type" label="来源" width="100" />
        <el-table-column prop="row_count" label="行数" width="90" align="center" />
        <el-table-column label="列数" width="90" align="center">
          <template #default="{ row }">
            {{ row.columns_meta?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" align="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/datasets/${row.id}`)">预览</el-button>
            <el-button
              size="small"
              type="primary"
              :loading="creating === row.id"
              @click="startAnalysis(row.id)"
            >
              开始分析
            </el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row.id, row.name)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <DatasetUploadDialog ref="uploadDialog" @upload="handleUpload" />
  </div>
</template>

<style scoped>
.dataset-list-page {
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

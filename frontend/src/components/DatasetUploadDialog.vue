<script setup lang="ts">
import { ref, computed } from "vue";

const emit = defineEmits<{
  (e: "upload", file: File, name: string): void;
}>();

const visible = ref(false);
const uploadFile = ref<File | null>(null);
const uploadName = ref("");
const uploading = ref(false);

const fileSize = computed(() => {
  if (!uploadFile.value) return "";
  const s = uploadFile.value.size;
  if (s < 1024) return `${s} B`;
  if (s < 1024 * 1024) return `${(s / 1024).toFixed(1)} KB`;
  return `${(s / (1024 * 1024)).toFixed(1)} MB`;
});

function onFileChange(file: any) {
  uploadFile.value = file.raw;
  uploadName.value = file.name?.replace(/\.[^.]+$/, "") || "";
}

function onFileRemove() {
  uploadFile.value = null;
}

async function submit() {
  if (!uploadFile.value) return;
  uploading.value = true;
  try {
    emit("upload", uploadFile.value, uploadName.value);
    visible.value = false;
    uploadFile.value = null;
    uploadName.value = "";
  } finally {
    uploading.value = false;
  }
}

function open() {
  visible.value = true;
}

defineExpose({ open });
</script>

<template>
  <el-dialog v-model="visible" title="上传数据集" width="500px" :close-on-click-modal="false">
    <el-upload
      drag
      accept=".csv,.xlsx,.xls,.json"
      :auto-upload="false"
      :limit="1"
      :on-change="onFileChange"
      :on-remove="onFileRemove"
    >
      <el-icon class="upload-icon"><upload-filled /></el-icon>
      <div class="upload-text">拖拽文件到此处，或<em>点击选择</em></div>
      <template #tip>
        <div class="upload-tip">支持 CSV、Excel (.xlsx/.xls)、JSON 文件，最大 10MB</div>
      </template>
    </el-upload>
    <div v-if="uploadFile" class="file-info">
      <span class="file-name">{{ uploadFile.name }}</span>
      <span class="file-size">{{ fileSize }}</span>
    </div>
    <el-progress v-if="uploading" :percentage="100" :stroke-width="6" striped striped-flow />
    <el-input v-model="uploadName" placeholder="数据集名称（可选）" style="margin-top: 12px" />
    <template #footer>
      <el-button @click="visible = false" :disabled="uploading">取消</el-button>
      <el-button type="primary" :loading="uploading" :disabled="!uploadFile" @click="submit">
        上传
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
:deep(.el-dialog__header) {
  padding: 20px 24px 0;
  font-size: 16px;
  font-weight: 600;
}
:deep(.el-dialog__body) {
  padding: 20px 24px;
}
:deep(.el-dialog__footer) {
  padding: 0 24px 20px;
}
:deep(.el-upload-dragger) {
  border: 2px dashed #e5e6eb;
  border-radius: 12px;
  padding: 32px 16px;
  transition: all 0.25s ease;
  background: #fafafa;
}
:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f5f8ff;
}
:deep(.el-upload-dragger.is-dragover) {
  border-color: #409eff;
  background: #ecf5ff;
}
.upload-icon {
  font-size: 48px;
  color: #c9cdd4;
  transition: color 0.2s;
}
:deep(.el-upload-dragger:hover) .upload-icon {
  color: #409eff;
}
.upload-text {
  margin-top: 8px;
  color: #4e5969;
  font-size: 14px;
}
.upload-tip {
  font-size: 12px;
  color: #86909c;
  margin-top: 8px;
}
.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
}
.file-name {
  color: #1d2129;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.file-size {
  color: #86909c;
  margin-left: 12px;
  flex-shrink: 0;
}
</style>

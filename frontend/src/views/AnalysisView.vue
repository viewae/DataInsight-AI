<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { apiClient } from "@/api/client";
import { useDatasetStore } from "@/stores/dataset";
import { useSessionStore } from "@/stores/session";
import ChatMessage from "@/components/ChatMessage.vue";
import ChartRenderer from "@/components/ChartRenderer.vue";
import AutoEDA from "@/components/AutoEDA.vue";
import type { DatasetOut } from "@/stores/dataset";

const route = useRoute();
const router = useRouter();
const datasetStore = useDatasetStore();
const sessionStore = useSessionStore();

const sessionId = ref(Number(route.params.sessionId));
const question = ref("");
const messagesContainer = ref<HTMLDivElement>();
const showCharts = ref(true);
const showHistory = ref(true);
const showAutoEDA = ref(true);
const autoEDADone = ref<Set<number>>(new Set());

const sampleQuestions = [
  "这份数据有哪些关键特征？",
  "数据中是否存在异常值？",
  "各列数据的分布情况如何？",
  "有哪些值得关注的趋势？",
];

async function loadSession(sid: number) {
  sessionId.value = sid;
  await sessionStore.loadSession(sid);
  if (sessionStore.currentSession?.dataset_id) {
    const dsId = sessionStore.currentSession.dataset_id;
    await datasetStore.fetchDetail(dsId);
    showAutoEDA.value = !autoEDADone.value.has(dsId);
    autoEDADone.value.add(dsId);
  }
  await sessionStore.fetchSessions();
  scrollToBottom();
}

// 监听路由变化，切换会话时重新加载
watch(() => route.params.sessionId, (newId) => {
  if (newId) loadSession(Number(newId));
});

async function send() {
  const q = question.value.trim();
  if (!q || sessionStore.sending) return;
  question.value = "";
  await sessionStore.sendMessage(q);
  scrollToBottom();
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

watch(() => sessionStore.messages.length, scrollToBottom);

onMounted(() => loadSession(sessionId.value));

async function generateReport() {
  if (!sessionStore.currentSession) return;
  try {
    const { data } = await apiClient.post("/report/generate", {
      session_id: sessionStore.currentSession.id,
    });
    ElMessage.success("报告生成成功");
    router.push(`/reports/${data.id}`);
  } catch {
    ElMessage.error("生成报告失败");
  }
}

function switchSession(id: number) {
  if (id !== sessionId.value) router.push(`/analysis/${id}`);
}

async function deleteSession(id: number, title: string) {
  try {
    await ElMessageBox.confirm(`确认删除会话「${title}」？`, "确认删除", { type: "warning" });
    await apiClient.delete(`/session/${id}`);
    ElMessage.success("会话已删除");
    await sessionStore.fetchSessions();
    if (id === sessionId.value) {
      const next = sessionStore.sessions[0];
      router.push(next ? `/analysis/${next.id}` : "/");
    }
  } catch {
    // cancelled
  }
}

// 新建会话
const newSessionDialog = ref(false);
const availableDatasets = ref<DatasetOut[]>([]);
const selectedDatasetId = ref<number | null>(null);
const creatingSession = ref(false);

async function openNewSession() {
  try {
    const { data } = await apiClient.get<DatasetOut[]>("/dataset/list");
    availableDatasets.value = data;
    selectedDatasetId.value = null;
    newSessionDialog.value = true;
  } catch {
    ElMessage.error("加载数据集列表失败");
  }
}

async function createNewSession() {
  if (!selectedDatasetId.value) return;
  creatingSession.value = true;
  try {
    const { data } = await apiClient.post("/session/create", { dataset_id: selectedDatasetId.value });
    newSessionDialog.value = false;
    router.push(`/analysis/${data.id}`);
  } catch {
    ElMessage.error("创建会话失败");
  } finally {
    creatingSession.value = false;
  }
}
</script>

<template>
  <div class="analysis-workspace">
    <!-- left: history sidebar -->
    <div class="history-panel" v-if="showHistory">
      <div class="panel-header">
        <h3>历史会话</h3>
        <div class="panel-actions">
          <el-button size="small" @click="openNewSession" text title="新建会话">
            <el-icon><plus /></el-icon>
          </el-button>
          <el-button size="small" @click="showHistory = false" text>
            <el-icon><fold /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="dataset-info" v-if="datasetStore.current">
        <p class="ds-name">{{ datasetStore.current.name }}</p>
        <p class="ds-meta">
          {{ datasetStore.current.row_count }} 行 ·
          {{ datasetStore.current.columns_meta?.length }} 列
        </p>
      </div>
      <el-menu
        :default-active="String(sessionId)"
        class="session-menu"
        @select="(idx: string) => switchSession(Number(idx))"
      >
        <el-menu-item
          v-for="s in sessionStore.sessions"
          :key="s.id"
          :index="String(s.id)"
        >
          <span class="session-item">
            <span class="session-title">{{ s.title || `会话 #${s.id}` }}</span>
            <el-button
              size="small"
              type="danger"
              text
              class="session-delete-btn"
              @click.stop="deleteSession(s.id, s.title || `会话 #${s.id}`)"
            >
              <el-icon><delete /></el-icon>
            </el-button>
          </span>
        </el-menu-item>
      </el-menu>
    </div>
    <el-button
      v-else
      class="show-history-btn"
      size="small"
      @click="showHistory = true"
      text
    >
      <el-icon><expand /></el-icon>
    </el-button>

    <!-- center: chat area -->
    <div class="chat-area">
      <div class="chat-header">
        <h2 v-if="sessionStore.currentSession">
          {{ sessionStore.currentSession.title || `会话 #${sessionStore.currentSession.id}` }}
        </h2>
        <div class="header-actions">
          <el-button
            v-if="sessionStore.messages.length > 0"
            size="small"
            type="primary"
            plain
            @click="generateReport"
          >
            生成报告
          </el-button>
          <el-button size="small" text @click="showCharts = !showCharts">
            <el-icon><data-analysis /></el-icon>
            {{ showCharts ? "隐藏图表" : "显示图表" }}
          </el-button>
        </div>
      </div>

      <div class="messages" ref="messagesContainer">
        <AutoEDA
          v-if="showAutoEDA && sessionStore.messages.length === 0 && datasetStore.current && !sessionStore.loading"
          :dataset-id="datasetStore.current.id"
          @close="showAutoEDA = false"
        />
        <template v-if="sessionStore.messages.length === 0 && !sessionStore.loading">
          <div class="welcome">
            <h3>开始分析</h3>
            <p>输入关于数据集的问题，AI 将为你分析数据并生成图表。</p>
            <div class="suggestions">
              <el-tag
                v-for="s in sampleQuestions"
                :key="s"
                @click="question = s"
                style="cursor: pointer; margin: 4px"
              >
                {{ s }}
              </el-tag>
            </div>
          </div>
        </template>
        <ChatMessage
          v-for="msg in sessionStore.messages"
          :key="msg.id"
          :message="msg"
        />
        <div v-if="sessionStore.sending" class="typing-indicator">
          <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          placeholder="输入关于数据的问题… (Ctrl+Enter 发送)"
          :disabled="sessionStore.sending"
          @keydown.enter.ctrl="send"
        />
        <el-button
          type="primary"
          :loading="sessionStore.sending"
          :disabled="!question.trim()"
          @click="send"
          class="send-btn"
        >
          发送
        </el-button>
      </div>
    </div>

    <!-- right: chart panel -->
    <div class="chart-panel" v-if="showCharts && sessionStore.charts.length">
      <div class="panel-header">
        <h3>图表</h3>
      </div>
      <div class="chart-list">
        <div
          v-for="(chart, idx) in sessionStore.charts"
          :key="idx"
          class="chart-item"
        >
          <ChartRenderer :config="chart" />
        </div>
      </div>
    </div>
    <!-- New session dialog -->
    <el-dialog v-model="newSessionDialog" title="新建会话" width="450px" top="20vh">
      <el-form label-position="top">
        <el-form-item label="选择数据集">
          <el-select v-model="selectedDatasetId" placeholder="请选择数据集" style="width: 100%">
            <el-option
              v-for="ds in availableDatasets"
              :key="ds.id"
              :label="ds.name"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newSessionDialog = false">取消</el-button>
        <el-button type="primary" :loading="creatingSession" :disabled="!selectedDatasetId" @click="createNewSession">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.analysis-workspace {
  display: flex;
  height: calc(100vh - 56px - 40px);
  gap: 0;
  margin: -20px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* ── History panel ── */
.history-panel {
  width: 240px;
  border-right: 1px solid #e5e6eb;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
  overflow-y: auto;
}
.show-history-btn {
  position: absolute;
  left: 0;
  top: 50%;
  z-index: 10;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #e5e6eb;
  background: #fff;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
}
.panel-actions {
  display: flex;
  gap: 2px;
}
.dataset-info {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e6eb;
  background: #f0f2f5;
}
.ds-name {
  font-weight: 600;
  margin: 0 0 4px;
  font-size: 13px;
  color: #1d2129;
}
.ds-meta {
  font-size: 12px;
  color: #86909c;
  margin: 0;
}
.session-menu {
  border-right: none;
  background: transparent;
}
.session-menu :deep(.el-menu-item) {
  height: 40px;
  line-height: 40px;
  border-radius: 6px;
  margin: 2px 8px;
  font-size: 13px;
  color: #4e5969;
}
.session-menu :deep(.el-menu-item.is-active) {
  background: rgba(64, 158, 255, 0.08);
  color: #409eff;
  font-weight: 500;
}
.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
.session-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.session-delete-btn {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 4px;
}
.el-menu-item:hover .session-delete-btn {
  opacity: 1;
}

/* ── Chat area ── */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #f7f8fa;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}
.chat-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}
.header-actions {
  display: flex;
  gap: 8px;
}

/* ── Messages ── */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
.welcome {
  text-align: center;
  padding: 80px 20px 60px;
  color: #86909c;
}
.welcome h3 {
  margin: 0 0 8px;
  color: #1d2129;
  font-size: 18px;
  font-weight: 600;
}
.welcome p {
  font-size: 14px;
}
.suggestions {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}
.suggestions :deep(.el-tag) {
  padding: 8px 16px;
  font-size: 13px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.suggestions :deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.20);
}
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
  font-size: 24px;
  color: #86909c;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.dot {
  animation: pulse 1.4s infinite;
}
.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* ── Input area ── */
.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e6eb;
  background: #fff;
}
.input-area :deep(.el-textarea__inner) {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  resize: none;
}
.input-area .el-textarea {
  flex: 1;
}
.send-btn {
  align-self: flex-end;
  height: 40px;
  padding: 0 24px;
  border-radius: 10px;
}

/* ── Chart panel ── */
.chart-panel {
  width: 380px;
  border-left: 1px solid #e5e6eb;
  overflow-y: auto;
  background: #f7f8fa;
}
.chart-list {
  padding: 12px;
}
.chart-item {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.25s ease;
}
.chart-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
</style>

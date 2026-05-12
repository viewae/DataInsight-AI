<script setup lang="ts">
import { computed } from "vue";
import type { Message } from "@/types/chart";
import ChartRenderer from "./ChartRenderer.vue";

const props = defineProps<{
  message: Message;
}>();

const isUser = computed(() => props.message.role === "user");

function formatTime(iso?: string) {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
}

function renderMarkdown(text: string): string {
  // Escape HTML
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  // Code block
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");
  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  // Italic
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  // Newlines to <br>
  html = html.replace(/\n/g, "<br>");
  return html;
}
</script>

<template>
  <div class="chat-message" :class="{ 'is-user': isUser, 'is-ai': !isUser }">
    <div class="message-avatar">
      {{ isUser ? "U" : "AI" }}
    </div>
    <div class="message-bubble">
      <div class="message-time">{{ formatTime(message.created_at) }}</div>
      <div class="message-content" v-if="isUser">{{ message.content }}</div>
      <div class="message-content markdown-body" v-else v-html="renderMarkdown(message.content)"></div>
      <div
        v-if="message.chart_suggestions && message.chart_suggestions.length"
        class="message-charts"
      >
        <div
          v-for="(chart, idx) in message.chart_suggestions"
          :key="idx"
          class="chart-wrapper"
        >
          <ChartRenderer :config="chart" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 85%;
}
.chat-message.is-user {
  flex-direction: row-reverse;
  margin-left: auto;
}
.chat-message.is-ai {
  margin-right: auto;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}
.is-user .message-avatar {
  background: #409eff;
  color: #fff;
}
.is-ai .message-avatar {
  background: #67c23a;
  color: #fff;
}
.message-bubble {
  background: #fff;
  border-radius: 12px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  line-height: 1.7;
  font-size: 14px;
  min-width: 0;
  color: #1d2129;
}
.is-user .message-bubble {
  background: linear-gradient(135deg, #ecf5ff, #e8f4ff);
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.10);
}
.message-content {
  white-space: pre-wrap;
  word-break: break-word;
}
.message-time {
  font-size: 11px;
  color: #c9cdd4;
  margin-bottom: 4px;
}
.is-user .message-time {
  text-align: right;
}
.markdown-body pre {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
  margin: 8px 0;
}
.markdown-body code {
  background: #f5f7fa;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 13px;
}
.markdown-body pre code {
  background: none;
  padding: 0;
}
.message-charts {
  margin-top: 12px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}
.chart-wrapper {
  margin-bottom: 12px;
}
.chart-wrapper:last-child {
  margin-bottom: 0;
}
</style>

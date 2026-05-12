import { defineStore } from "pinia";
import { ref } from "vue";
import { apiClient } from "@/api/client";
import { ElMessage } from "element-plus";
import type { Message, ChartConfig } from "@/types/chart";

interface SessionOut {
  id: number;
  dataset_id: number | null;
  title: string | null;
  conversation_history: { role: string; content: string }[];
  created_at: string;
}

interface SessionQueryResponse {
  answer: string;
  model: string;
  chart_suggestions?: ChartConfig[];
}

export const useSessionStore = defineStore("session", () => {
  const currentSession = ref<SessionOut | null>(null);
  const sessions = ref<SessionOut[]>([]);
  const messages = ref<Message[]>([]);
  const charts = ref<ChartConfig[]>([]);
  const loading = ref(false);
  const sending = ref(false);

  async function fetchSessions() {
    try {
      const { data } = await apiClient.get<SessionOut[]>("/session/list");
      sessions.value = data;
    } catch {
      // non-critical
    }
  }

  async function createSession(datasetId: number): Promise<SessionOut> {
    const { data } = await apiClient.post<SessionOut>("/session/create", {
      dataset_id: datasetId,
    });
    currentSession.value = data;
    messages.value = [];
    charts.value = [];
    return data;
  }

  async function loadSession(id: number) {
    loading.value = true;
    try {
      const { data } = await apiClient.get<SessionOut>(`/session/${id}`);
      currentSession.value = data;
      // rebuild messages from conversation_history
      const msgs: Message[] = [];
      for (let i = 0; i < data.conversation_history.length; i += 2) {
        const userMsg = data.conversation_history[i];
        const aiMsg = data.conversation_history[i + 1];
        if (userMsg && userMsg.role === "user") {
          msgs.push({
            id: `msg-${i}`,
            role: "user",
            content: userMsg.content,
          });
        }
        if (aiMsg && aiMsg.role === "assistant") {
          msgs.push({
            id: `msg-${i + 1}`,
            role: "assistant",
            content: aiMsg.content,
          });
        }
      }
      messages.value = msgs;
    } catch {
      ElMessage.error("加载会话失败");
    } finally {
      loading.value = false;
    }
  }

  async function sendMessage(question: string) {
    if (!currentSession.value) return null;
    sending.value = true;

    // optimistically add user message
    const userMsg: Message = {
      id: `msg-${Date.now()}-user`,
      role: "user",
      content: question,
      created_at: new Date().toISOString(),
    };
    messages.value.push(userMsg);

    try {
      const { data } = await apiClient.post<SessionQueryResponse>(
        `/session/${currentSession.value.id}/query`,
        { question }
      );

      const aiMsg: Message = {
        id: `msg-${Date.now()}-ai`,
        role: "assistant",
        content: data.answer,
        chart_suggestions: data.chart_suggestions || undefined,
        created_at: new Date().toISOString(),
      };
      messages.value.push(aiMsg);

      if (data.chart_suggestions) {
        charts.value.push(...data.chart_suggestions);
      }

      return data;
    } catch (err: any) {
      // remove optimistic user message on error
      messages.value = messages.value.filter((m) => m.id !== userMsg.id);
      const detail = err?.response?.data?.detail || "请求失败";
      ElMessage.error(detail);
      return null;
    } finally {
      sending.value = false;
    }
  }

  return {
    currentSession,
    sessions,
    messages,
    charts,
    loading,
    sending,
    fetchSessions,
    createSession,
    loadSession,
    sendMessage,
  };
});

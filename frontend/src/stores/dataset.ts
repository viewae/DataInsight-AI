import { defineStore } from "pinia";
import { ref } from "vue";
import { apiClient } from "@/api/client";
import { ElMessage } from "element-plus";

export interface DatasetOut {
  id: number;
  name: string;
  source_type: string;
  row_count: number;
  columns_meta: { name: string; dtype: string }[];
}

export interface PreviewData {
  columns: string[];
  rows: Record<string, unknown>[];
}

export const useDatasetStore = defineStore("dataset", () => {
  const datasets = ref<DatasetOut[]>([]);
  const current = ref<DatasetOut | null>(null);
  const loading = ref(false);
  const previewCache = ref<Record<number, PreviewData>>({});

  async function fetchList() {
    loading.value = true;
    try {
      const { data } = await apiClient.get<DatasetOut[]>("/dataset/list");
      datasets.value = data;
    } catch {
      ElMessage.error("加载数据集列表失败");
    } finally {
      loading.value = false;
    }
  }

  async function fetchDetail(id: number) {
    loading.value = true;
    try {
      const { data } = await apiClient.get<DatasetOut>(`/dataset/${id}`);
      current.value = data;
      return data;
    } catch {
      ElMessage.error("加载数据集详情失败");
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPreview(id: number): Promise<PreviewData | null> {
    if (previewCache.value[id]) return previewCache.value[id];
    try {
      const { data } = await apiClient.get<PreviewData>(`/dataset/${id}/preview`);
      previewCache.value[id] = data;
      return data;
    } catch {
      ElMessage.error("加载数据预览失败");
      return null;
    }
  }

  async function upload(file: File, name?: string) {
    const form = new FormData();
    form.append("file", file);
    if (name) form.append("name", name);
    const { data } = await apiClient.post<DatasetOut>("/dataset/upload", form);
    await fetchList();
    return data;
  }

  async function remove(id: number) {
    await apiClient.delete(`/dataset/${id}`);
    delete previewCache.value[id];
    if (current.value?.id === id) current.value = null;
    await fetchList();
  }

  return { datasets, current, loading, fetchList, fetchDetail, fetchPreview, upload, remove };
});

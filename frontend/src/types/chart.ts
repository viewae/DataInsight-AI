export interface ChartConfig {
  id?: number;
  chart_type: "bar" | "line" | "pie" | "scatter" | "histogram";
  title: string;
  x_axis?: string;
  y_axis?: string;
  aggregation?: "sum" | "count" | "avg" | "none";
  data: Record<string, unknown>[];
  config?: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  chart_suggestions?: ChartConfig[];
  created_at?: string;
}

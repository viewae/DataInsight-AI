<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
import { init, use } from "echarts/core";
import { BarChart, LineChart, PieChart, ScatterChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsOption } from "echarts";
import type { ChartConfig } from "@/types/chart";

use([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  CanvasRenderer,
]);

const props = defineProps<{
  config: ChartConfig;
}>();

const chartRef = ref<HTMLDivElement>();
let instance: ReturnType<typeof init> | null = null;

function buildOption(c: ChartConfig): EChartsOption {
  const base: EChartsOption = {
    title: { text: c.title, left: "center", textStyle: { fontSize: 14 } },
    tooltip: { trigger: "axis" },
    grid: { left: 50, right: 20, bottom: 50, top: 50 },
    toolbox: {
      feature: {
        saveAsImage: { title: "保存图片" },
        dataZoom: { title: { zoom: "缩放", back: "还原" } },
      },
      iconStyle: { borderColor: "#86909c" },
    },
  };

  if (!c.data || c.data.length === 0) return base;

  if (c.chart_type === "pie") {
    return {
      ...base,
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: "55%",
          data: c.data.map((d) => {
            const keys = Object.keys(d);
            return { name: String(d[keys[0]]), value: Number(d[keys[1]]) };
          }),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0,0,0,0.5)",
            },
          },
        },
      ],
    } as EChartsOption;
  }

  const xField = c.x_axis || Object.keys(c.data[0])[0];
  const yField = c.y_axis || Object.keys(c.data[0])[1];

  if (c.chart_type === "scatter") {
    const hasXY = c.data.length > 0 && "x" in c.data[0] && "y" in c.data[0];
    if (hasXY) {
      const labels = c.data.map((d: any) => d.name || "");
      return {
        ...base,
        xAxis: { type: "value" },
        yAxis: { type: "value" },
        tooltip: {
          trigger: "item",
          formatter: (p: any) => {
            const name = labels[p.dataIndex] ? `${labels[p.dataIndex]}<br/>` : "";
            return `${name}X: ${p.data[0]}<br/>Y: ${p.data[1]}`;
          },
        },
        series: [{
          type: "scatter",
          data: c.data.map((d: any) => [d.x, d.y]),
          symbolSize: 12,
          label: {
            show: true,
            position: "right",
            formatter: (p: any) => labels[p.dataIndex],
            fontSize: 11,
          },
          itemStyle: { color: "#409eff" },
        }],
      } as EChartsOption;
    }
    // fallback: 无 x/y 字段时用 name/value
    const labels = c.data.map((d: any) => String(d.name || ""));
    return {
      ...base,
      xAxis: { type: "value", name: "序号" },
      yAxis: { type: "value", name: "值" },
      tooltip: { trigger: "item", formatter: (p: any) => `${labels[p.dataIndex]}<br/>Y: ${p.data[1]}` },
      series: [{
        type: "scatter",
        data: c.data.map((d: any, i: number) => [i, Number(d.value || 0)]),
        symbolSize: 12,
        label: {
          show: true,
          position: "right",
          formatter: (p: any) => labels[p.dataIndex],
          fontSize: 11,
        },
        itemStyle: { color: "#409eff" },
      }],
    } as EChartsOption;
  }

  const categories = c.data.map((d) => String(d[xField]));
  const values = c.data.map((d) => Number(d[yField]) || 0);

  return {
    ...base,
    xAxis: { type: "category", data: categories, axisLabel: { rotate: 30 } },
    yAxis: { type: "value" },
    series: [
      {
        type: (c.chart_type === "histogram" ? "bar" : c.chart_type) as
          | "bar"
          | "line",
        data: values,
        itemStyle:
          c.chart_type === "bar" || c.chart_type === "histogram"
            ? { borderRadius: [4, 4, 0, 0] }
            : undefined,
      },
    ],
  } as EChartsOption;
}

function render() {
  if (!chartRef.value) return;
  if (!instance) {
    instance = init(chartRef.value);
  }
  instance.setOption(buildOption(props.config), { notMerge: true });
  instance.resize();
}

onMounted(async () => {
  await nextTick();
  render();
});

watch(
  () => props.config,
  () => render(),
  { deep: true }
);

const observer = new ResizeObserver(() => instance?.resize());
onMounted(() => {
  if (chartRef.value) observer.observe(chartRef.value);
});
onUnmounted(() => {
  observer.disconnect();
  instance?.dispose();
});
</script>

<template>
  <div ref="chartRef" class="chart-renderer"></div>
</template>

<style scoped>
.chart-renderer {
  width: 100%;
  height: 300px;
}
</style>

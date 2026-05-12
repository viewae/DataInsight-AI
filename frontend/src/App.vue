<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <el-config-provider namespace="el">
    <RouterView />
  </el-config-provider>
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
}

html, body, #app {
  margin: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, "Noto Sans SC", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background: #f0f2f5;
  color: #1d2129;
}

/* ── Scrollbar ── */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #c9cdd4;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #a8adb5;
}

/* ── Element Plus card override for consistent depth ── */
.el-card {
  border: none !important;
  border-radius: 8px !important;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.el-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.el-card.is-hover-shadow:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.10) !important;
}

/* ── Consistent page styles ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.page-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 20px 24px;
}

/* ── Table wrapper ── */
.table-wrapper {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 4px 0;
}
</style>

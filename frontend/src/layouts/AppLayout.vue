<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { useRouter, useRoute } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside width="220px" class="app-sidebar">
      <div class="sidebar-header">
        <div class="logo-mark">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none">
            <rect width="32" height="32" rx="8" fill="#409eff"/>
            <path d="M9 22V13l7 5 7-8v12H9z" fill="#fff"/>
          </svg>
        </div>
        <span class="logo-text">DataInsight</span>
      </div>

      <el-menu
        router
        :default-active="route.path"
        class="sidebar-menu"
        :collapse="false"
      >
        <el-menu-item index="/">
          <el-icon><home-filled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/datasets">
          <el-icon><folder /></el-icon>
          <span>数据集</span>
        </el-menu-item>
        <el-menu-item index="/sessions">
          <el-icon><chat-dot-square /></el-icon>
          <span>会话</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><document /></el-icon>
          <span>报告</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="user-badge">
          <el-avatar :size="32" class="user-avatar">
            {{ auth.user?.username?.charAt(0)?.toUpperCase() || "U" }}
          </el-avatar>
          <div class="user-meta">
            <span class="user-name">{{ auth.user?.username || "用户" }}</span>
            <span class="user-role">{{ auth.user?.role === "admin" ? "管理员" : "普通用户" }}</span>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- Main area -->
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="→">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path.startsWith('/datasets')">
              数据集
            </el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path.startsWith('/sessions')">
              会话
            </el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path.startsWith('/reports')">
              报告
            </el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path.startsWith('/analysis')">
              分析
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="user-info">
            {{ auth.user?.username }}
          </span>
          <el-button size="small" @click="handleLogout" class="logout-btn">
            退出
          </el-button>
        </div>
      </el-header>

      <el-main class="app-main">
        <div class="page-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* ── Layout ── */
.app-layout {
  height: 100vh;
  background: #f0f2f5;
}

/* ── Sidebar ── */
.app-sidebar {
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #1d2a3a 0%, #172433 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.04);
  overflow: hidden;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}
.logo-mark {
  display: flex;
  align-items: center;
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 8px 0;
}
.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 6px;
  color: #a3aec2;
  font-size: 14px;
  transition: all 0.2s ease;
}
.sidebar-menu :deep(.el-menu-item .el-icon) {
  color: #7a88a0;
  font-size: 18px;
  margin-right: 8px;
}
.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.06);
  color: #d0d7e3;
}
.sidebar-menu :deep(.el-menu-item:hover .el-icon) {
  color: #a3aec2;
}
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
  position: relative;
}
.sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: "";
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #409eff;
  border-radius: 0 3px 3px 0;
}
.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #409eff;
}

/* ── Sidebar footer ── */
.sidebar-footer {
  flex-shrink: 0;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  background: #409eff;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
}
.user-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #d0d7e3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  font-size: 11px;
  color: #7a88a0;
}

/* ── Header ── */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}
.header-left {
  display: flex;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-info {
  font-size: 13px;
  font-weight: 500;
  color: #4e5969;
}
.logout-btn {
  font-size: 12px;
}

/* ── Main content ── */
.app-main {
  background: #f0f2f5;
  overflow-y: auto;
  padding: 0;
}
.page-content {
  padding: 20px 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>

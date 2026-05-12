<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
</script>

<template>
  <div class="dashboard">
    <!-- Welcome banner -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h2>欢迎回来，{{ auth.user?.username || "用户" }}</h2>
        <p>{{ auth.user?.email }}</p>
      </div>
      <div class="banner-icon">
        <svg viewBox="0 0 120 80" width="120" height="80" fill="none">
          <rect x="10" y="30" width="20" height="40" rx="3" fill="#fff" fill-opacity="0.15"/>
          <rect x="36" y="15" width="20" height="55" rx="3" fill="#fff" fill-opacity="0.25"/>
          <rect x="62" y="25" width="20" height="45" rx="3" fill="#fff" fill-opacity="0.15"/>
          <rect x="88" y="10" width="20" height="60" rx="3" fill="#fff" fill-opacity="0.25"/>
        </svg>
      </div>
    </div>

    <!-- Stats row -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-icon datasets">
            <el-icon :size="24"><folder /></el-icon>
          </div>
          <div class="stat-body">
            <span class="stat-label">数据集</span>
            <span class="stat-value">上传和管理数据文件</span>
          </div>
          <router-link to="/datasets" class="stat-action">
            <el-icon><arrow-right /></el-icon>
          </router-link>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-icon analysis">
            <el-icon :size="24"><data-analysis /></el-icon>
          </div>
          <div class="stat-body">
            <span class="stat-label">分析会话</span>
            <span class="stat-value">AI 驱动的数据探索</span>
          </div>
          <router-link to="/datasets" class="stat-action">
            <el-icon><arrow-right /></el-icon>
          </router-link>
        </div>
      </el-col>
    </el-row>

    <!-- Quick actions -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="action-card">
          <template #header>
            <div class="card-title">
              <el-icon :size="18"><folder-add /></el-icon>
              <span>数据集</span>
            </div>
          </template>
          <p>上传和管理你的数据文件，支持 CSV、Excel、JSON 格式</p>
          <div class="card-actions">
            <router-link to="/datasets">
              <el-button type="primary" plain>前往数据集</el-button>
            </router-link>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="action-card">
          <template #header>
            <div class="card-title">
              <el-icon :size="18"><document /></el-icon>
              <span>报告</span>
            </div>
          </template>
          <p>查看分析报告，下载 HTML 格式的分析结果文档</p>
          <div class="card-actions">
            <router-link to="/reports">
              <el-button type="success" plain>前往报告</el-button>
            </router-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
/* ── Welcome banner ── */
.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1d2a3a 0%, #2a3f5a 100%);
  border-radius: 12px;
  padding: 28px 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.10);
}
.banner-content h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 600;
  color: #fff;
}
.banner-content p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.55);
}
.banner-icon {
  flex-shrink: 0;
  opacity: 0.9;
}

/* ── Stats row ── */
.stats-row {
  margin-bottom: 24px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.25s ease, transform 0.25s ease;
  position: relative;
}
.stat-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-icon.datasets {
  background: #e8f4ff;
  color: #409eff;
}
.stat-icon.analysis {
  background: #e8ffec;
  color: #00b42a;
}
.stat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 2px;
}
.stat-value {
  font-size: 13px;
  color: #86909c;
}

.stat-action {
  color: #c9cdd4;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
}
.stat-card:hover .stat-action {
  color: #409eff;
}

/* ── Action cards ── */
.action-card {
  margin-bottom: 4px;
}
.action-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f2f3f5;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
}
.action-card p {
  color: #4e5969;
  font-size: 14px;
  margin: 0 0 16px;
  line-height: 1.6;
}
.card-actions {
  display: flex;
  gap: 8px;
}
</style>

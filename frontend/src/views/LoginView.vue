<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";

const router = useRouter();
const auth = useAuthStore();

const form = reactive({ email: "", password: "" });
const loading = ref(false);

async function handleLogin() {
  loading.value = true;
  try {
    await auth.login(form.email, form.password);
    ElMessage.success("登录成功");
    router.push("/datasets");
  } catch (err: any) {
    const msg = err?.response?.data?.detail || "登录失败，请检查邮箱和密码";
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <!-- Decorative background shapes -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="login-container">
      <!-- Brand section -->
      <div class="brand-section">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" width="40" height="40" fill="none">
            <rect width="40" height="40" rx="10" fill="#fff" fill-opacity="0.2"/>
            <path d="M12 28V16l8 6 8-10v16H12z" fill="#fff"/>
          </svg>
        </div>
        <h1 class="brand-title">DataInsight AI</h1>
        <p class="brand-desc">智能数据洞察平台</p>
      </div>

      <!-- Login card -->
      <div class="login-card">
        <div class="card-header">
          <h2>欢迎回来</h2>
          <p class="subtitle">登录你的账号继续使用</p>
        </div>

        <el-form
          :model="form"
          label-position="top"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item label="邮箱" required>
            <el-input
              v-model="form.email"
              type="email"
              placeholder="you@example.com"
              size="large"
              prefix-icon="Message"
            />
          </el-form-item>
          <el-form-item label="密码" required>
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="输入密码"
              size="large"
              prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              size="large"
              class="submit-btn"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="footer-link">
          还没有账号？
          <router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a2a3a 0%, #0d1b2a 50%, #1a2a3a 100%);
  overflow: hidden;
}

/* ── Decorative floating shapes ── */
.bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
}
.shape-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #409eff, transparent);
  top: -200px;
  right: -150px;
  animation: float1 20s ease-in-out infinite;
}
.shape-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #409eff, transparent);
  bottom: -100px;
  left: -100px;
  animation: float2 25s ease-in-out infinite;
}
.shape-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #36cfc9, transparent);
  top: 40%;
  left: 60%;
  animation: float3 18s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 40px); }
}
@keyframes float2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-20px, -30px); }
}
@keyframes float3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(40px, -20px); }
}

/* ── Layout ── */
.login-container {
  position: relative;
  display: flex;
  gap: 60px;
  align-items: center;
  z-index: 1;
}

/* ── Brand section ── */
.brand-section {
  color: #fff;
  text-align: right;
  max-width: 280px;
}
.brand-icon {
  display: inline-flex;
  margin-bottom: 16px;
}
.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}
.brand-desc {
  font-size: 15px;
  opacity: 0.6;
  margin: 0;
  line-height: 1.6;
}

/* ── Login card ── */
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 16px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.30),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  padding: 40px 36px 32px;
}

.card-header {
  margin-bottom: 28px;
}
.card-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 600;
  color: #1d2129;
}
.subtitle {
  margin: 0;
  font-size: 14px;
  color: #86909c;
}

/* ── Form ── */
.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}
.login-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #4e5969;
  padding-bottom: 6px;
}
.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e6eb inset;
  padding: 4px 12px;
  transition: box-shadow 0.2s ease;
}
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}
.login-form :deep(.el-input__inner) {
  height: 40px;
}
.login-form :deep(.el-input__prefix) {
  margin-right: 8px;
}
.login-form :deep(.el-input__prefix-inner) .el-icon {
  font-size: 16px;
  color: #c9cdd4;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  margin-top: 4px;
}

/* ── Footer ── */
.footer-link {
  text-align: center;
  font-size: 14px;
  color: #86909c;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f2f3f5;
}
.footer-link a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}
.footer-link a:hover {
  text-decoration: underline;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    gap: 32px;
    padding: 24px;
  }
  .brand-section {
    text-align: center;
  }
  .login-card {
    width: 100%;
    padding: 28px 24px;
  }
}
</style>

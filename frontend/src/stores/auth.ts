import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { apiClient } from "@/api/client";
import type { AxiosError } from "axios";

interface UserPublic {
  id: number;
  email: string;
  username: string;
  role: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface QuotaResponse {
  quota_limit: number;
  quota_used: number;
  remaining: number;
}

const TOKEN_KEY = "datainsight_token";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const user = ref<UserPublic | null>(null);
  const quota = ref<QuotaResponse | null>(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!token.value);

  function _saveToken(t: string) {
    token.value = t;
    localStorage.setItem(TOKEN_KEY, t);
  }

  function _clearAuth() {
    token.value = null;
    user.value = null;
    quota.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  async function login(email: string, password: string) {
    loading.value = true;
    try {
      const { data } = await apiClient.post<TokenResponse>("/auth/login", {
        email,
        password,
      });
      _saveToken(data.access_token);
      await fetchProfile();
      await fetchQuota();
    } finally {
      loading.value = false;
    }
  }

  async function register(email: string, username: string, password: string) {
    loading.value = true;
    try {
      const { data } = await apiClient.post<TokenResponse>("/auth/register", {
        email,
        username,
        password,
      });
      _saveToken(data.access_token);
      await fetchProfile();
      await fetchQuota();
    } finally {
      loading.value = false;
    }
  }

  async function fetchProfile() {
    if (!token.value) return;
    try {
      const { data } = await apiClient.get<UserPublic>("/auth/profile");
      user.value = data;
    } catch {
      _clearAuth();
    }
  }

  async function fetchQuota() {
    if (!token.value) return;
    try {
      const { data } = await apiClient.get<QuotaResponse>("/auth/quota");
      quota.value = data;
    } catch {
      // quota fetch failure is non-critical
    }
  }

  function logout() {
    _clearAuth();
  }

  // try to restore session on init
  if (token.value) {
    fetchProfile();
    fetchQuota();
  }

  return {
    token,
    user,
    quota,
    loading,
    isAuthenticated,
    login,
    register,
    fetchProfile,
    fetchQuota,
    logout,
  };
});

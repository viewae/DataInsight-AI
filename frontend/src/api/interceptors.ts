import type { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

const TOKEN_KEY = "datainsight_token";

export function setupInterceptors(api: AxiosInstance) {
  api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        // avoid redirect on auth endpoints
        const url = error.config?.url ?? "";
        if (!url.startsWith("/auth/")) {
          window.location.href = "/login";
        }
      }
      return Promise.reject(error);
    },
  );
}

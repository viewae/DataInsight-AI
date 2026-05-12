import axios from "axios";

import { setupInterceptors } from "./interceptors";

/** 调用同源 /api，开发环境由 Vite 代理到 FastAPI */
export const apiClient = axios.create({
  baseURL: "/api",
  timeout: 120_000,
});

setupInterceptors(apiClient);

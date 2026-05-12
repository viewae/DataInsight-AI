import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { guest: true },
    },
    {
      path: "/",
      component: () => import("@/layouts/AppLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "home",
          component: () => import("@/views/DashboardView.vue"),
        },
        {
          path: "datasets",
          name: "datasets",
          component: () => import("@/views/DatasetListView.vue"),
        },
        {
          path: "datasets/:id",
          name: "dataset-detail",
          component: () => import("@/views/DatasetDetailView.vue"),
        },
        {
          path: "reports",
          name: "reports",
          component: () => import("@/views/ReportListView.vue"),
        },
        {
          path: "reports/:id",
          name: "report-detail",
          component: () => import("@/views/ReportDetailView.vue"),
        },
        {
          path: "sessions",
          name: "sessions",
          component: () => import("@/views/SessionListView.vue"),
        },
        {
          path: "analysis/:sessionId",
          name: "analysis",
          component: () => import("@/views/AnalysisView.vue"),
        },
      ],
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: "login" });
  } else if (to.meta.guest && auth.isAuthenticated) {
    next({ name: "home" });
  } else {
    next();
  }
});

export default router;

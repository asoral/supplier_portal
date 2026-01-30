import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../pages/Register.vue')
  },
  {
    path: '/tenders',
    name: 'Tenders',
    component: () => import('../pages/Tenders.vue')
  },
  {
    path: '/tenders/:id',
    name: 'TenderDetail',
    component: () => import('../pages/TenderDetail.vue')
  },
  {
    path: '/contracts',
    name: 'Contracts',
    component: () => import('../pages/Contracts.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../pages/Dashboard.vue')
  },
  {
    path: '/saved-tenders',
    name: 'SavedTenders',
    component: () => import('../pages/SavedTenders.vue')
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: () => import('../pages/Invoices.vue')
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('../pages/Documents.vue')
  },
  {
    path: '/integrations',
    name: 'Integrations',
    component: () => import('../pages/Integrations.vue')
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: () => import('../pages/Catalog.vue')
  },
  {
    path: '/deliveries',
    component: () => import('../pages/Deliveries.vue')
  },
  {
    path: '/queries',
    name: 'Queries',
    component: () => import('../pages/Queries.vue')
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('../pages/Help.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../pages/Profile.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/supplier-portal'),
  routes
})

// [FIX] Strict Auth Guard
// Prevent access to protected routes if not authenticated
router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login', '/register', '/help', '/'];
  const authRequired = !publicPages.includes(to.path);
  const { useAuthStore } = await import('../stores/auth');
  const authStore = useAuthStore();

  // If page requires auth and user is not logged in
  if (authRequired && !authStore.isAuthenticated) {
    // Try to initialize first (in case of page reload)
    await authStore.initializeAuth();

    if (!authStore.isAuthenticated) {
      // Still not authenticated? Redirect to login
      return next('/login');
    }
  }

  next();
})

export default router

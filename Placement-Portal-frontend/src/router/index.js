import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user';
import LoginPage from '../pages/LoginPage.vue';
import RegisterPage from '../pages/RegisterPage.vue';
import AdminDashboard from '../pages/AdminDashboard.vue';
import CompanyDashboard from '../pages/CompanyDashboard.vue';
import StudentDashboard from '../pages/StudentDashboard.vue';
import DriveDetails from '../pages/DriveDetails.vue';
import ApplicationDetails from '../pages/ApplicationDetails.vue';

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'company' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/drive/:id',
    name: 'DriveDetails',
    component: DriveDetails,
    meta: { requiresAuth: true }
  },
  {
    path: '/application/:id',
    name: 'ApplicationDetails',
    component: ApplicationDetails,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const userStore = useUserStore();

  // If a logged-in user hits the login/register page (e.g. by
  // pressing back), treat it as an implicit logout so they cannot
  // continue using the existing token.
  if ((to.name === 'Login' || to.name === 'Register') && token) {
    localStorage.clear();
    // also clear pinia store if available
    try { userStore.logout(); } catch (e) {}
    // allow navigation to the login/register route normally
  }

  if (to.meta.requiresAuth) {
    if (!token) {
      next('/');
    } else if (to.meta.role && to.meta.role !== role) {
      next('/');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
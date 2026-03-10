<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <router-link to="/" class="navbar-brand">
        <strong>🎓 Placement Portal</strong>
      </router-link>
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link to="/" class="nav-link">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link to="/register" class="nav-link">Register</router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <span class="nav-link" v-if="userRole">
              <strong>{{ roleLabel }}</strong>
            </span>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <button @click="logout" class="btn btn-sm btn-danger">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';

const router = useRouter();
const userStore = useUserStore();

const isAuthenticated = computed(() => !!userStore.token);
const userRole = computed(() => userStore.role);
const roleLabel = computed(() => {
  const labels = {
    'admin': '👨‍💼 Admin',
    'company': '🏢 Company',
    'student': '👨‍🎓 Student'
  };
  return labels[userStore.role] || userStore.role;
});

const logout = () => {
  userStore.logout();
  router.push('/');
};
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
}
</style>

<template>
  <div class="container-fluid d-flex justify-content-center align-items-center min-vh-100 bg-light">
    <div class="row w-100">
      <!-- Login Form -->
      <div class="col-md-6 d-flex justify-content-center">
        <div class="card p-4 shadow" style="width: 100%; max-width: 400px;">
          <h4 class="text-center mb-4">Login Form</h4>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <input 
                v-model="loginForm.email" 
                type="email" 
                class="form-control" 
                placeholder="Email"
                required 
              />
            </div>
            <div class="mb-3">
              <input 
                v-model="loginForm.password" 
                type="password" 
                class="form-control" 
                placeholder="Password"
                required 
              />
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
            <p class="text-center mt-3 small">
              Don't have an account? 
              <router-link to="/register" class="text-primary">Register here</router-link>
            </p>
          </form>
          <div v-if="loginError" class="alert alert-danger mt-3">{{ loginError }}</div>
        </div>
      </div>

      <!-- Register Form Preview -->
      <div class="col-md-6 d-flex justify-content-center">
        <div class="card p-4 shadow" style="width: 100%; max-width: 400px; opacity: 0.7;">
          <h4 class="text-center mb-4">Register Form</h4>
          <div class="text-center text-muted">
            <small>Switch to Register tab to create new account</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import api from '../utils/api';

const loginForm = ref({
  email: '',
  password: ''
});
const loginError = ref('');
const router = useRouter();
const userStore = useUserStore();

onMounted(() => {
  if (userStore.token) {
    if (userStore.role === 'admin') router.push('/admin/dashboard');
    else if (userStore.role === 'company') router.push('/company/dashboard');
    else if (userStore.role === 'student') router.push('/student/dashboard');
  }
});

const handleLogin = async () => {
  loginError.value = '';
  try {
    const res = await api.post('/auth/login', {
      email: loginForm.value.email,
      password: loginForm.value.password
    });
    
    // Store token and role globally in Pinia
    userStore.setAuth(res.data.access_token, res.data.role);
    
    // Redirect based on the role returned by the backend
    if (res.data.role === 'admin') {
      router.push('/admin/dashboard');
    } else if (res.data.role === 'company') {
      router.push('/company/dashboard');
    } else if (res.data.role === 'student') {
      router.push('/student/dashboard');
    }
  } catch (err) {
    loginError.value = err.response?.data?.message || "Server unreachable";
  }
};
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}
</style>
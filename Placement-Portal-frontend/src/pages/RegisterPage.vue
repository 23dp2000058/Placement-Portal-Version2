<template>
  <div class="container-fluid d-flex justify-content-center align-items-center min-vh-100 bg-light">
    <div class="card p-5 shadow" style="width: 100%; max-width: 500px;">
      <h4 class="text-center mb-4">Register Form</h4>
      
      <form @submit.prevent="handleRegister">
        <!-- Role Selection -->
        <div class="mb-3">
          <label class="form-label">Register as:</label>
          <div class="btn-group w-100" role="group">
            <input 
              type="radio" 
              class="btn-check" 
              name="role" 
              id="student" 
              value="student"
              v-model="registerForm.role"
            />
            <label class="btn btn-outline-primary" for="student">Student</label>
            
            <input 
              type="radio" 
              class="btn-check" 
              name="role" 
              id="company" 
              value="company"
              v-model="registerForm.role"
            />
            <label class="btn btn-outline-primary" for="company">Company</label>
          </div>
        </div>

        <!-- Common Fields -->
        <div class="mb-3">
          <input 
            v-model="registerForm.name" 
            type="text" 
            class="form-control" 
            placeholder="Full Name / Company Name"
            required 
          />
        </div>

        <div class="mb-3">
          <input 
            v-model="registerForm.email" 
            type="email" 
            class="form-control" 
            placeholder="Email"
            required 
          />
        </div>

        <div class="mb-3">
          <input 
            v-model="registerForm.password" 
            type="password" 
            class="form-control" 
            placeholder="Password"
            required 
          />
        </div>

        <!-- Student-specific fields -->
        <template v-if="registerForm.role === 'student'">
          <div class="mb-3">
            <input 
              v-model="registerForm.branch" 
              type="text" 
              class="form-control" 
              placeholder="Branch"
              required 
            />
          </div>
          <div class="mb-3">
            <input 
              v-model="registerForm.cgpa" 
              type="number" 
              step="0.01" 
              class="form-control" 
              placeholder="CGPA"
              required 
            />
          </div>
          <div class="mb-3">
            <input 
              v-model="registerForm.year" 
              type="number" 
              class="form-control" 
              placeholder="Graduation Year"
              required 
            />
          </div>
        </template>

        <!-- Company-specific field -->
        <div v-if="registerForm.role === 'company'" class="mb-3">
          <input 
            v-model="registerForm.industry" 
            type="text" 
            class="form-control" 
            placeholder="Industry"
            required 
          />
        </div>

        <button type="submit" class="btn btn-success w-100">Register</button>
        <p class="text-center mt-3 small">
          Already have an account? 
          <router-link to="/" class="text-primary">Login here</router-link>
        </p>
      </form>

      <div v-if="registerError" class="alert alert-danger mt-3">{{ registerError }}</div>
      <div v-if="registerSuccess" class="alert alert-success mt-3">{{ registerSuccess }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../utils/api';

const registerForm = ref({
  name: '',
  email: '',
  password: '',
  role: 'student',
  branch: '',
  cgpa: '',
  year: '',
  industry: ''
});
const registerError = ref('');
const registerSuccess = ref('');
const router = useRouter();

const handleRegister = async () => {
  registerError.value = '';
  registerSuccess.value = '';
  
  try {
    const payload = {
      name: registerForm.value.name,
      email: registerForm.value.email,
      password: registerForm.value.password,
      role: registerForm.value.role
    };

    if (registerForm.value.role === 'student') {
      payload.branch = registerForm.value.branch;
      payload.cgpa = registerForm.value.cgpa;
      payload.year = registerForm.value.year;
    } else if (registerForm.value.role === 'company') {
      payload.industry = registerForm.value.industry;
    }

    const res = await api.post('/auth/register', payload);
    
    registerSuccess.value = res.data.message || 'Registration successful! Redirecting to login...';
    
    setTimeout(() => {
      router.push('/');
    }, 2000);
  } catch (err) {
    registerError.value = err.response?.data?.message || "Registration failed";
  }
};
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}
</style>

// src/stores/user.js
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('role') || ''
  }),
  actions: {
    setAuth(token, role) {
      this.token = token;
      this.role = role;
      localStorage.setItem('token', token);
      localStorage.setItem('role', role);
    },
    logout() {
      this.token = '';
      this.role = '';
      localStorage.clear();
    }
  }
});
<template>
  <div class="container-fluid p-4">
    <router-link :to="previousPage" class="btn btn-secondary mb-3">← Back</router-link>
    
    <div v-if="application" class="row">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Application Details</h4>
          </div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-6">
                <p><strong>Student Name:</strong> {{ application.student_name }}</p>
                <p><strong>Email:</strong> {{ application.student_email }}</p>
                <p><strong>Department:</strong> {{ application.department }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Company:</strong> {{ application.company_name }}</p>
                <p><strong>Position:</strong> {{ application.position }}</p>
                <p><strong>Drive Name:</strong> {{ application.drive_name }}</p>
              </div>
            </div>

            <div class="row mb-4">
              <div class="col-md-6">
                <p><strong>Applied Date:</strong> {{ formatDate(application.applied_date) }}</p>
                <p><strong>Status:</strong>
                  <span 
                    :class="{
                      'badge bg-warning': application.status === 'pending',
                      'badge bg-success': application.status === 'approved',
                      'badge bg-danger': application.status === 'rejected'
                    }"
                  >
                    {{ application.status }}
                  </span>
                </p>
              </div>
              <div class="col-md-6">
                <p v-if="application.result">
                  <strong>Result:</strong> 
                  <span class="badge bg-info">{{ application.result }}</span>
                </p>
                <p v-if="application.offer_letter">
                  <strong>Offer Letter:</strong>
                  <a :href="application.offer_letter" target="_blank" class="btn btn-sm btn-outline-primary">Download</a>
                </p>
              </div>
            </div>

            <div class="mb-4">
              <h6>Qualifications</h6>
              <ul>
                <li>CGPA: {{ application.cgpa }}</li>
                <li>Backlog: {{ application.backlog || 'None' }}</li>
                <li>Skills: {{ application.skills || 'Not specified' }}</li>
              </ul>
            </div>

            <div v-if="canUpdateStatus" class="mt-4">
              <h6>Update Status</h6>
              <button v
                v-if="application.status === 'pending'" 
                class="btn btn-success me-2" 
                @click="updateStatus('approved')"
              >
                Approve
              </button>
              <button 
                v-if="application.status === 'pending'" 
                class="btn btn-danger" 
                @click="updateStatus('rejected')"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div v-if="application.resume" class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Resume</h6>
          </div>
          <div class="card-body">
            <a :href="application.resume" target="_blank" class="btn btn-outline-primary w-100">
              Download Resume
            </a>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-info">
      Loading application details...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import api from '../utils/api';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const application = ref(null);
const previousPage = ref('/');

const canUpdateStatus = computed(() => {
  return userStore.role === 'company' || userStore.role === 'admin';
});

onMounted(async () => {
  try {
    const res = await api.get(`/application/${route.params.id}`);
    application.value = res.data;

    // Set previousPage based on role
    if (userStore.role === 'student') {
      previousPage.value = '/student/dashboard';
    } else if (userStore.role === 'company') {
      previousPage.value = '/company/dashboard';
    } else if (userStore.role === 'admin') {
      previousPage.value = '/admin/dashboard';
    }
  } catch (err) {
    console.error('Error loading application:', err);
  }
});

const updateStatus = async (status) => {
  try {
    await api.put(`/application/${route.params.id}`, { status });
    application.value.status = status;
    alert('Application updated successfully!');
  } catch (err) {
    alert('Failed to update: ' + (err.response?.data?.message || 'Unknown error'));
  }
};

const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
};
</script>

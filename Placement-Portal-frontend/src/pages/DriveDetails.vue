<template>
  <div class="container-fluid p-4">
    <router-link to="/" class="btn btn-secondary mb-3">← Back</router-link>
    
    <div v-if="drive" class="row">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">{{ drive.name }}</h4>
          </div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-6">
                <p><strong>Company:</strong> {{ drive.company_name }}</p>
                <p><strong>Position:</strong> {{ drive.position }}</p>
                <p><strong>Package:</strong> ₹{{ drive.package }} LPA</p>
                <p><strong>Location:</strong> {{ drive.location }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Drive Date:</strong> {{ formatDate(drive.date) }}</p>
                <p><strong>Status:</strong> 
                  <span :class="['badge', drive.status === 'active' ? 'bg-success' : 'bg-danger']">
                    {{ drive.status }}
                  </span>
                </p>
                <p><strong>Total Applicants:</strong> {{ drive.applicant_count || 0 }}</p>
              </div>
            </div>

            <div class="mb-4">
              <h6>Description</h6>
              <p>{{ drive.description || 'No description provided' }}</p>
            </div>

            <div class="d-flex gap-2">
              <button v-if="!hasApplied" @click="applyNow" class="btn btn-success">Apply Now</button>
              <button @click="$router.back()" class="btn btn-outline-secondary">Close</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Drive Information</h6>
          </div>
          <div class="card-body">
            <div class="mb-2">
              <span class="text-muted small">Qualification</span>
              <p class="small">{{ drive.qualification || 'Any' }}</p>
            </div>
            <div class="mb-2">
              <span class="text-muted small">Experience</span>
              <p class="small">{{ drive.experience || 'Fresher' }}</p>
            </div>
            <div class="mb-2">
              <span class="text-muted small">CGPA Cutoff</span>
              <p class="small">{{ drive.cgpa_cutoff || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-info">
      Loading drive details...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../utils/api';

const route = useRoute();
const router = useRouter();
const drive = ref(null);
const hasApplied = ref(false);

onMounted(async () => {
  try {
    const res = await api.get(`/drive/${route.params.id}`);
    drive.value = res.data;

    // Check if student has already applied
    const appliedRes = await api.get(`/student/check-application/${route.params.id}`);
    hasApplied.value = appliedRes.data.has_applied || false;
  } catch (err) {
    console.error('Error loading drive:', err);
  }
});

const applyNow = async () => {
  try {
    await api.post(`/student/apply`, { drive_id: route.params.id });
    hasApplied.value = true;
    alert('Application submitted successfully!');
  } catch (err) {
    alert('Failed to apply: ' + (err.response?.data?.message || 'Unknown error'));
  }
};

const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
};
</script>

<template>
  <div class="container-fluid p-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Welcome {{ studentName }}</h2>
      <button @click="logout" class="btn btn-danger">Logout</button>
    </div>

    <div class="row">
      <!-- Left Column: Organizations & Applications -->
      <div class="col-lg-8">
        <!-- Organizations -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Organizations</h6>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Company</th>
                  <th>Position</th>
                  <th>Package</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="organizations.length === 0">
                  <td colspan="5" class="text-center text-muted small">No organizations available</td>
                </tr>
                <tr v-for="org in organizations" :key="org.id">
                  <td class="small">{{ org.company_name }}</td>
                  <td class="small">{{ org.position }}</td>
                  <td class="small">₹{{ org.package }}</td>
                  <td>
                    <span :class="getStatusBadge(org.status)" class="badge">
                      {{ org.status }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-xs btn-outline-primary" @click="viewDrive(org.id)">View More</button>
                    <button 
                      v-if="!hasApplied(org.id)" 
                      class="btn btn-xs btn-outline-success" 
                      @click="applyToDrive(org.id)"
                    >
                      Apply
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Applied Drives -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Applied Drives</h6>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Company</th>
                  <th>Position</th>
                  <th>Applied Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="appliedDrives.length === 0">
                  <td colspan="5" class="text-center text-muted small">No applied drives</td>
                </tr>
                <tr v-for="drive in appliedDrives" :key="drive.id">
                  <td class="small">{{ drive.company_name }}</td>
                  <td class="small">{{ drive.position }}</td>
                  <td class="small">{{ formatDate(drive.applied_date) }}</td>
                  <td>
                    <span 
                      :class="{
                        'badge bg-warning': drive.status === 'pending',
                        'badge bg-success': drive.status === 'approved',
                        'badge bg-danger': drive.status === 'rejected'
                      }"
                    >
                      {{ drive.status }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-xs btn-outline-info" @click="viewApplication(drive.application_id)">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: Application History & Drive Details -->
      <div class="col-lg-4">
        <!-- Student Application History -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Student Application History</h6>
          </div>
          <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Drive</th>
                  <th>Department</th>
                  <th>Apply Date</th>
                  <th>Status</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="applicationHistory.length === 0">
                  <td colspan="5" class="text-center text-muted small">No history</td>
                </tr>
                <tr v-for="app in applicationHistory" :key="app.id">
                  <td class="small">{{ app.drive_name }}</td>
                  <td class="small">{{ app.department }}</td>
                  <td class="small">{{ formatDate(app.applied_date) }}</td>
                  <td>
                    <span 
                      :class="{
                        'badge bg-warning': app.status === 'pending',
                        'badge bg-success': app.status === 'approved',
                        'badge bg-danger': app.status === 'rejected'
                      }"
                    >
                      {{ app.status }}
                    </span>
                  </td>
                  <td>
                    <span v-if="app.result" class="small">{{ app.result }}</span>
                    <span v-else class="text-muted small">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Selected Drive Details Card -->
        <div v-if="selectedDrive" class="card">
          <div class="card-header bg-primary text-white">
            <h6 class="mb-0">{{ selectedDrive.company_name }}</h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <p class="small mb-1"><strong>Position:</strong></p>
              <p class="small">{{ selectedDrive.position }}</p>
            </div>
            <div class="mb-3">
              <p class="small mb-1"><strong>Package:</strong></p>
              <p class="small">₹{{ selectedDrive.package }} LPA</p>
            </div>
            <div class="mb-3">
              <p class="small mb-1"><strong>Location:</strong></p>
              <p class="small">{{ selectedDrive.location }}</p>
            </div>
            <div class="mb-3">
              <p class="small mb-1"><strong>Description:</strong></p>
              <p class="small">{{ selectedDrive.description }}</p>
            </div>
            <div class="d-flex gap-2">
              <button 
                v-if="!hasApplied(selectedDrive.id)" 
                @click="applyToDrive(selectedDrive.id)" 
                class="btn btn-success btn-sm"
              >
                Apply Now
              </button>
              <button @click="selectedDrive = null" class="btn btn-outline-secondary btn-sm">
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="message" :class="['alert', { 'alert-success': message.type === 'success', 'alert-danger': message.type === 'error' }]" class="mt-3">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import api from '../utils/api';

const router = useRouter();
const userStore = useUserStore();

const studentName = ref('');
const organizations = ref([]);
const appliedDrives = ref([]);
const applicationHistory = ref([]);
const selectedDrive = ref(null);
const message = ref(null);

onMounted(() => {
  if (userStore.role !== 'student') {
    router.push('/');
  }
  loadData();
});

const loadData = async () => {
  try {
    const [profileRes, orgsRes, appliedRes, historyRes] = await Promise.all([
      api.get('/student/profile'),
      api.get('/student/drives'),
      api.get('/student/applied-drives'),
      api.get('/student/application-history')
    ]);

    studentName.value = profileRes.data?.name || 'Student';
    organizations.value = orgsRes.data || [];
    appliedDrives.value = appliedRes.data || [];
    applicationHistory.value = historyRes.data || [];
  } catch (err) {
    showMessage('Failed to load data', 'error');
  }
};

const hasApplied = (driveId) => {
  return appliedDrives.value.some(d => d.id === driveId);
};

const applyToDrive = async (driveId) => {
  if (!confirm('Confirm your application?')) return;

  try {
    await api.post(`/student/apply`, { drive_id: driveId });
    
    const drive = organizations.value.find(d => d.id === driveId);
    if (drive) {
      appliedDrives.value.push({
        ...drive,
        applied_date: new Date().toISOString(),
        status: 'pending'
      });
    }
    
    showMessage('Application submitted successfully', 'success');
    loadData();
  } catch (err) {
    showMessage(err.response?.data?.message || 'Failed to apply', 'error');
  }
};

const viewDrive = (driveId) => {
  selectedDrive.value = organizations.value.find(d => d.id === driveId) || null;
};

const viewApplication = (appId) => {
  router.push(`/application/${appId}`);
};

const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
};

const getStatusBadge = (status) => {
  const badges = {
    'active': 'bg-success',
    'closed': 'bg-danger',
    'pending': 'bg-warning'
  };
  return badges[status] || 'bg-secondary';
};

const logout = () => {
  userStore.logout();
  router.push('/');
};

const showMessage = (text, type) => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = null;
  }, 3000);
};
</script>

<style scoped>
.btn-xs {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}
</style>

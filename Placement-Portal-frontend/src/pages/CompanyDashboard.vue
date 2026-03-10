<template>
  <div class="container-fluid p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h4">Welcome, {{ companyName }}</h2>
      <button @click="logout" class="btn btn-sm btn-outline-danger">Logout</button>
    </div>

    <div class="row">
      <div class="col-lg-8">
        
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-bold">Active Placement Drives</h6>
              <button @click="showCreateDriveForm = true" class="btn btn-sm btn-primary">+ Create Drive</button>
            </div>
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr class="small text-uppercase">
                  <th>#</th>
                  <th>Drive Name</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading"><td colspan="5" class="text-center py-4">Loading...</td></tr>
                <tr v-else-if="upcomingDrives.length === 0">
                  <td colspan="5" class="text-center text-muted py-4">No active drives found.</td>
                </tr>
                <tr v-for="(drive, idx) in upcomingDrives" :key="drive.driveid">
                  <td>{{ idx + 1 }}</td>
                  <td class="fw-bold">{{ drive.driveid }}</td>
                  <td>{{ formatDate(drive.drivedate) }}</td>
                  <td>
                    <span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle">
                      {{ drive.companyapprovalstatus }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary me-2" @click="showApplications(drive)">Manage Apps</button>
                    <button class="btn btn-sm btn-light" @click="markCompleted(drive.driveid)">Close</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedDrive" class="card shadow-sm border-primary">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Applications for {{ selectedDrive.driveid }}</h6>
            <button class="btn-close btn-close-white" @click="closeApplications"></button>
          </div>
          <div class="table-responsive">
            <table class="table table-sm mb-0">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Status</th>
                  <th class="text-end">Decision</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in filteredApplications" :key="app.applicationid">
                  <td>{{ app.studentid }}</td>
                  <td>
                    <span :class="getStatusBadge(app.application_status)">{{ app.application_status }}</span>
                  </td>
                  <td class="text-end">
                    <div v-if="app.application_status === 'Applied'">
                      <button class="btn btn-xs btn-success me-1" @click="updateApplicationStatus(app.applicationid, 'Shortlisted')">Shortlist</button>
                      <button class="btn btn-xs btn-danger" @click="updateApplicationStatus(app.applicationid, 'Rejected')">Reject</button>
                    </div>
                    <span v-else class="text-muted small">Decided</span>
                  </td>
                </tr>
                <tr v-if="filteredApplications.length === 0">
                  <td colspan="3" class="text-center py-3 text-muted">No students have applied yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card shadow-sm border-0 bg-light">
          <div class="card-body">
            <h6 class="fw-bold mb-3">Drive Overview</h6>
            <div class="d-flex justify-content-between mb-2">
              <span>Total Applications</span>
              <span class="badge bg-dark">{{ applications.length }}</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span>Pending Review</span>
              <span class="badge bg-warning text-dark">{{ applications.filter(a => a.application_status === 'Applied').length }}</span>
            </div>
            <hr>
            <small class="text-muted">Deadline: March 10, 2026</small>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateDriveForm" class="modal-custom-overlay">
      <div class="modal-custom-content">
        <h5>New Placement Drive</h5>
        <form @submit.prevent="createDrive">
          <div class="mb-3">
            <label class="small">Drive ID (Unique)</label>
            <input v-model="driveForm.driveid" type="text" class="form-control" placeholder="e.g. DRIVE_001" required />
          </div>
          <div class="mb-3">
            <label class="small">Date</label>
            <input v-model="driveForm.drivedate" type="date" class="form-control" required />
          </div>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-secondary w-50" @click="showCreateDriveForm = false">Cancel</button>
            <button type="submit" class="btn btn-primary w-50">Launch</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="message" :class="`alert-toast alert alert-${message.type === 'success' ? 'success' : 'danger'}`">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import api from '../utils/api';

const router = useRouter();
const userStore = useUserStore();

// State
const companyName = ref('');
const upcomingDrives = ref([]);
const applications = ref([]);
const selectedDrive = ref(null);
const showCreateDriveForm = ref(false);
const message = ref(null);
const loading = ref(false);

const driveForm = ref({
  driveid: '',
  drivedate: ''
});

onMounted(() => {
  if (userStore.role !== 'company') router.push('/');
  loadData();
});

const loadData = async () => {
  loading.value = true;
  try {
    const [drivesRes, appRes] = await Promise.all([
      api.get('/company/drives'),
      api.get('/company/applications')
    ]);
    upcomingDrives.value = drivesRes.data || [];
    applications.value = appRes.data || [];
    companyName.value = userStore.email; // Fallback to email if name is missing
  } catch (err) {
    showMessage('Error fetching data', 'error');
  } finally {
    loading.value = false;
  }
};

const createDrive = async () => {
  try {
    await api.post('/company/drives', driveForm.value);
    showMessage('Drive launched successfully!', 'success');
    showCreateDriveForm.value = false;
    driveForm.value = { driveid: '', drivedate: '' };
    loadData();
  } catch (err) {
    showMessage('Failed to create drive', 'error');
  }
};

const updateApplicationStatus = async (appId, status) => {
  try {
    await api.put(`/company/applications/${appId}`, { status });
    const app = applications.value.find(a => a.applicationid === appId);
    if (app) app.application_status = status;
    showMessage(`Student ${status}`, 'success');
  } catch (err) {
    showMessage('Status update failed', 'error');
  }
};

const showApplications = (drive) => {
  selectedDrive.value = drive;
};

const closeApplications = () => {
  selectedDrive.value = null;
};

const filteredApplications = computed(() => {
  if (!selectedDrive.value) return [];
  return applications.value.filter(a => a.drive_id === selectedDrive.value.driveid);
});

const showMessage = (text, type) => {
  message.value = { text, type };
  setTimeout(() => message.value = null, 3000);
};

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : 'N/A';

const getStatusBadge = (status) => {
  if (status === 'Shortlisted') return 'badge bg-success';
  if (status === 'Rejected') return 'badge bg-danger';
  return 'badge bg-warning text-dark';
};

const logout = () => {
  userStore.logout();
  router.push('/');
};
</script>

<style scoped>
.modal-custom-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: center; align-items: center;
  z-index: 1050;
}
.modal-custom-content {
  background: white; padding: 2rem; border-radius: 12px;
  width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.alert-toast {
  position: fixed; bottom: 20px; right: 20px;
  min-width: 250px; z-index: 2000;
}
.btn-xs { padding: 0.1rem 0.4rem; font-size: 0.7rem; }
</style>
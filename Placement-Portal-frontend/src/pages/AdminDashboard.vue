<template>
  <div class="container-fluid p-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Welcome Admin</h2>
      <div class="d-flex gap-2 align-items-center">
        <div class="input-group" style="width: 300px;">
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Search..."
          />
          <button class="btn btn-outline-primary" @click="performSearch">Search</button>
        </div>
        <button @click="logout" class="btn btn-danger">Logout</button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="row">
      <!-- Left Section: Companies & Students -->
      <div class="col-lg-4">
        <!-- Registered Companies -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Registered Companies</h6>
          </div>
          <div class="card-body" style="max-height: 300px; overflow-y: auto;">
            <div v-if="companies.length === 0" class="text-muted small">No companies registered</div>
            <div v-for="comp in companies" :key="comp.id" class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
              <span>
                {{ comp.name }}
                <span v-if="comp.is_blacklisted" class="badge bg-warning ms-2">Blacklisted</span>
              </span>
              <div class="btn-group">
                <button 
                  @click="toggleCompanyBlacklist(comp)" 
                  class="btn btn-sm" 
                  :class="comp.is_blacklisted ? 'btn-outline-success' : 'btn-outline-warning'"
                >
                  {{ comp.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
                <button @click="deleteCompany(comp.id)" class="btn btn-sm btn-outline-danger">Delete</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Registered Students -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Registered Students</h6>
          </div>
          <div class="card-body" style="max-height: 300px; overflow-y: auto;">
            <div v-if="students.length === 0" class="text-muted small">No students registered</div>
            <div v-for="student in students" :key="student.id" class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
              <span>
                {{ student.name }}
                <span v-if="student.is_blacklisted" class="badge bg-warning ms-2">Blacklisted</span>
              </span>
              <div class="btn-group">
                <button 
                  @click="toggleStudentBlacklist(student)" 
                  class="btn btn-sm" 
                  :class="student.is_blacklisted ? 'btn-outline-success' : 'btn-outline-warning'"
                >
                  {{ student.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
                <button @click="deleteStudent(student.id)" class="btn btn-sm btn-outline-danger">Delete</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Company Applications -->
        <div class="card">
          <div class="card-header bg-success text-white border">
            <h6 class="mb-0">Company Applications</h6>
          </div>
          <div class="card-body" style="max-height: 300px; overflow-y: auto;">
            <div v-if="companyApplications.length === 0" class="text-muted small">No pending applications</div>
            <div v-for="app in companyApplications" :key="app.id" class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
              <span>{{ app.company_name }}</span>
              <button @click="approveCompany(app.id)" class="btn btn-sm btn-outline-success">Approve</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Section: Drives & Applications -->
      <div class="col-lg-4">
        <!-- Upcoming Drives -->
        <div class="card mb-4">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Upcoming Drives</h6>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Drive Name</th>
                  <th>Company</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="drives.length === 0">
                  <td colspan="3" class="text-center text-muted small">No drives scheduled</td>
                </tr>
                <tr v-for="drive in drives" :key="drive.id">
                  <td>{{ drive.name }}</td>
                  <td>{{ drive.company_name }}</td>
                  <td>
                    <button class="btn btn-xs btn-outline-primary" @click="viewDrive(drive.id)">View</button>
                    <button class="btn btn-xs btn-outline-warning" @click="markDriveCompleted(drive.id)">Mark Completed</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Closed Drives -->
        <div class="card">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Closed Drives</h6>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Drive Name</th>
                  <th>Company</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="closedDrives.length === 0">
                  <td colspan="3" class="text-center text-muted small">No closed drives</td>
                </tr>
                <tr v-for="drive in closedDrives" :key="drive.id">
                  <td>{{ drive.name }}</td>
                  <td>{{ drive.company_name }}</td>
                  <td>
                    <button class="btn btn-xs btn-outline-info" @click="viewDrive(drive.id)">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Section: Applications -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header bg-light border">
            <h6 class="mb-0">Student Applications</h6>
          </div>
          <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
            <table class="table table-sm table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th>Student</th>
                  <th>Drive</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="studentApplications.length === 0">
                  <td colspan="4" class="text-center text-muted small">No applications</td>
                </tr>
                <tr v-for="app in studentApplications" :key="app.id">
                  <td class="small">{{ app.student_name }}</td>
                  <td class="small">{{ app.drive_name }}</td>
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
                    <button class="btn btn-xs btn-outline-info" @click="viewApplication(app.id)">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
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

const searchQuery = ref('');
const companies = ref([]);
const students = ref([]);
const companyApplications = ref([]);
const drives = ref([]);
const closedDrives = ref([]);
const studentApplications = ref([]);
const message = ref(null);

// Check authentication
onMounted(() => {
  if (userStore.role !== 'admin') {
    router.push('/');
  }
  loadData();
});

const loadData = async () => {
  try {
    const [compRes, studRes, appRes, drivesRes, appStudRes] = await Promise.all([
      api.get('/admin/companies'),
      api.get('/admin/students'),
      api.get('/admin/company-applications'),
      api.get('/admin/drive'),         // backend routes under /admin/drive
      api.get('/admin/student-applications')
    ]);

    companies.value = compRes.data || [];
    students.value = studRes.data || [];
    companyApplications.value = appRes.data || [];

    // map backend drives (which use drive_id) into shape with `id` so our
    // tables and viewDrive helper work consistently
    const allDrives = (drivesRes.data || []).map(d => ({ ...d, id: d.drive_id }));
    drives.value = allDrives.filter(d => d.status === 'approved');
    closedDrives.value = allDrives.filter(d => d.status !== 'approved');

    studentApplications.value = appStudRes.data || [];
  } catch (err) {
    showMessage('Failed to load data', 'error');
  }
};

const deleteCompany = async (companyId) => {
  if (!confirm('Are you sure?')) return;
  try {
    await api.delete(`/admin/company/${companyId}`);
    companies.value = companies.value.filter(c => c.id !== companyId);
    showMessage('Company deleted', 'success');
  } catch (err) {
    showMessage('Failed to delete company', 'error');
  }
};

const toggleCompanyBlacklist = async (comp) => {
  try {
    const newStatus = !comp.is_blacklisted;
    await api.post(`/admin/blacklist/company/${comp.id}`, { status: newStatus });
    comp.is_blacklisted = newStatus;
    showMessage(`Company ${newStatus ? 'blacklisted' : 'reactivated'}`, 'success');
  } catch (err) {
    showMessage('Failed to update blacklist status', 'error');
  }
};

const deleteStudent = async (studentId) => {
  if (!confirm('Are you sure?')) return;
  try {
    await api.delete(`/admin/student/${studentId}`);
    students.value = students.value.filter(s => s.id !== studentId);
    showMessage('Student deleted', 'success');
  } catch (err) {
    showMessage('Failed to delete student', 'error');
  }
};

const toggleStudentBlacklist = async (student) => {
  try {
    const newStatus = !student.is_blacklisted;
    await api.post(`/admin/blacklist/student/${student.id}`, { status: newStatus });
    student.is_blacklisted = newStatus;
    showMessage(`Student ${newStatus ? 'blacklisted' : 'reactivated'}`, 'success');
  } catch (err) {
    showMessage('Failed to update blacklist status', 'error');
  }
};

const approveCompany = async (appId) => {
  try {
    await api.post(`/admin/company-application/${appId}/approve`);
    companyApplications.value = companyApplications.value.filter(a => a.id !== appId);
    showMessage('Company approved', 'success');
  } catch (err) {
    showMessage('Failed to approve company', 'error');
  }
};

const performSearch = () => {
  if (!searchQuery.value) {
    loadData();
    return;
  }
  // Search functionality to be implemented
};

const viewDrive = (driveId) => {
  // driveId should already be normalized to actual drive ID; if undefined,
  // no navigation occurs
  if (!driveId) return;
  router.push(`/drive/${driveId}`);
};

const markDriveCompleted = async (driveId) => {
  if (!confirm('Mark this drive as completed?')) return;
  try {
    await api.put(`/admin/drive/${driveId}`, { status: 'closed' });
    // move drive from upcoming list to closed list
    const idx = drives.value.findIndex(d => d.id === driveId);
    if (idx !== -1) {
      const [d] = drives.value.splice(idx, 1);
      d.status = 'closed';
      closedDrives.value.push(d);
    }
    showMessage('Drive marked completed', 'success');
  } catch (err) {
    showMessage('Failed to update drive', 'error');
  }
};

const viewApplication = (appId) => {
  router.push(`/application/${appId}`);
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
<template>
  <div class="personal-data-container">
    <el-card class="personal-data-card">
      <h2 class="personal-title">Personal Data</h2>
      <el-form :model="userData" :rules="rules" ref="userFormRef" label-width="170px">
        <el-form-item label="Username" prop="username">
          <el-input v-model="userData.username" disabled />
        </el-form-item>

        <el-form-item label="Phone" prop="phone">
          <el-input v-model="userData.phone" placeholder="Enter phone number" />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input v-model="userData.email" placeholder="Enter email address" />
        </el-form-item>

        <el-form-item label="ID Number" prop="idNumber">
          <el-input v-model="userData.idNumber" placeholder="Enter ID number" />
        </el-form-item>

        <el-form-item label="Home Address" prop="homeAddress">
          <el-input v-model="userData.homeAddress" placeholder="Enter home address" />
        </el-form-item>

        <el-form-item label="Company" prop="company">
          <el-input v-model="userData.company" placeholder="Enter company name" />
        </el-form-item>

        <el-form-item label="Company Address" prop="companyAddress">
          <el-input v-model="userData.companyAddress" placeholder="Enter company address" />
        </el-form-item>

        <!-- Password Change Section -->
        <template v-if="showChangePassword">
          <el-form-item label="Old Password" prop="oldPassword">
            <el-input v-model="userData.oldPassword" type="password" placeholder="Enter old password" />
          </el-form-item>

          <el-form-item label="New Password" prop="newPassword">
            <el-input v-model="userData.newPassword" type="password" placeholder="Enter new password" />
          </el-form-item>

          <el-form-item label="Confirm New Password" prop="confirmNewPassword">
            <el-input v-model="userData.confirmNewPassword" type="password" placeholder="Confirm new password" />
          </el-form-item>
        </template>

        <!-- Buttons -->
        <el-form-item>
          <div class="btn-group">
            <el-button type="warning" @click="showChangePassword = !showChangePassword">
              {{ showChangePassword ? 'Cancel Change' : 'Change Password' }}
            </el-button>
            <el-button type="primary" @click="updateUserInfo" :loading="loading.update">Update</el-button>
            <el-button @click="goBack">Back</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PersonalDataPage',
  data() {
    return {
      userData: {
        username: '',
        phone: '',
        email: '',
        idNumber: '',
        homeAddress: '',
        company: '',
        companyAddress: '',
        oldPassword: '',
        newPassword: '',
        confirmNewPassword: ''
      },
      loading: { update: false },
      showChangePassword: false,
      rules: {
        phone: [{ required: true, message: 'Please enter phone number', trigger: 'blur' }],
        email: [
          { required: true, message: 'Please enter email', trigger: 'blur' },
          { type: 'email', message: 'Invalid email address', trigger: 'blur' }
        ],
        idNumber: [{ required: true, message: 'Please enter ID number', trigger: 'blur' }],
        homeAddress: [{ required: true, message: 'Please enter home address', trigger: 'blur' }],
        company: [{ required: true, message: 'Please enter company name', trigger: 'blur' }],
        companyAddress: [{ required: true, message: 'Please enter company address', trigger: 'blur' }],
        oldPassword: [{ required: true, message: 'Please enter old password', trigger: 'blur' }],
        newPassword: [{ required: true, message: 'Please enter new password', trigger: 'blur' }],
        confirmNewPassword: [
          { required: true, message: 'Please confirm new password', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (value !== this.userData.newPassword) {
                callback(new Error('Passwords do not match'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ]
      }
    };
  },
  created() {
    this.fetchUserInfo();
  },
  methods: {
    fetchUserInfo() {
      axios.get(`http://localhost:5050/api/user?username=${localStorage.getItem('username')}`)
        .then(res => {
          this.userData = res.data.data;
        })
        .catch(() => {
          this.$message.error('Failed to fetch user data');
        });
    },
    updateUserInfo() {
      this.$refs.userFormRef.validate(valid => {
        if (!valid) return;
        this.loading.update = true;
        axios.put('http://localhost:5050/api/user', this.userData)
          .then(() => {
            this.$message.success('User data updated successfully');
            this.fetchUserInfo();
          })
          .catch(() => {
            this.$message.error('Failed to update user data');
          })
          .finally(() => {
            this.loading.update = false;
          });
      });
    },
    goBack() {
      this.$router.push('/home');
    }
  }
};
</script>

<style scoped>
.personal-data-container {
  padding: 40px;
  background-color: #f5f7fa;
}

.personal-data-card {
  width: 560px;
  margin: 0 auto;
  padding: 30px 20px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.personal-title {
  text-align: center;
  margin-bottom: 20px;
}

.btn-group {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}
</style>


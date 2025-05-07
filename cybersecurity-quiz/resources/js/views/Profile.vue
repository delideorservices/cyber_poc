<template>
    <div class="profile-page container">
      <h1>Your Profile</h1>
      
      <div v-if="loading" class="loader">
        Loading profile...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else>
        <div class="card profile-card">
          <div class="profile-header">
            <div class="avatar">
              {{ getInitials(profile.name) }}
            </div>
            <div class="profile-info">
              <h2>{{ profile.name }}</h2>
              <p>{{ profile.email }}</p>
              <p v-if="profile.sector && profile.role">
                {{ profile.role.name }} at {{ profile.sector.name }} sector
              </p>
            </div>
          </div>
        </div>
        
        <div class="tab-navigation">
          <button 
            v-for="(tab, index) in tabs" 
            :key="index"
            :class="['tab-button', { active: currentTab === index }]"
            @click="currentTab = index"
          >
            {{ tab }}
          </button>
        </div>
        
        <!-- Personal Information Tab -->
        <div v-if="currentTab === 0" class="tab-content card">
          <h3>Personal Information</h3>
          
          <form @submit.prevent="updatePersonalInfo" class="profile-form">
            <div class="form-group">
              <label for="name" class="form-label">Full Name</label>
              <input 
                id="name"
                v-model="form.name"
                type="text" 
                class="form-control" 
                required
                placeholder="Enter your full name"
              >
            </div>
            
            <div class="form-group">
              <label for="gender" class="form-label">Gender</label>
              <select id="gender" v-model="form.gender" class="form-control">
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="age" class="form-label">Age</label>
              <input 
                id="age"
                v-model.number="form.age"
                type="number" 
                class="form-control" 
                min="18"
                max="100"
                placeholder="Enter your age"
              >
            </div>
            
            <div class="form-group">
              <button type="submit" class="btn btn-primary" :disabled="updating">
                {{ updating ? 'Updating...' : 'Update Personal Information' }}
              </button>
            </div>
          </form>
        </div>
        
        <!-- Professional Information Tab -->
        <div v-if="currentTab === 1" class="tab-content card">
          <h3>Professional Information</h3>
          
          <form @submit.prevent="updateProfessionalInfo" class="profile-form">
            <div class="form-group">
              <label for="sector" class="form-label">Sector</label>
              <select 
                id="sector" 
                v-model="form.sector_id" 
                class="form-control"
                @change="onSectorChange"
              >
                <option value="">Select sector</option>
                <option v-for="sector in sectors" :key="sector.id" :value="sector.id">
                  {{ sector.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="role" class="form-label">Role</label>
              <select id="role" v-model="form.role_id" class="form-control" :disabled="!form.sector_id">
                <option value="">Select role</option>
                <option v-for="role in filteredRoles" :key="role.id" :value="role.id">
                  {{ role.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="years_experience" class="form-label">Years of Experience</label>
              <input 
                id="years_experience"
                v-model.number="form.years_experience"
                type="number" 
                class="form-control" 
                min="0"
                max="50"
                placeholder="Enter years of experience"
              >
            </div>
            
            <div class="form-group">
              <label for="learning_goal" class="form-label">Learning Goal</label>
              <textarea 
                id="learning_goal"
                v-model="form.learning_goal"
                class="form-control" 
                rows="3"
                placeholder="What do you hope to achieve with cybersecurity training?"
              ></textarea>
            </div>
            
            <div class="form-group">
              <button type="submit" class="btn btn-primary" :disabled="updating">
                {{ updating ? 'Updating...' : 'Update Professional Information' }}
              </button>
            </div>
          </form>
        </div>
        
        <!-- Skills & Certifications Tab -->
        <div v-if="currentTab === 2" class="tab-content card">
          <h3>Skills & Certifications</h3>
          
          <div class="skills-section">
            <div class="section-header">
              <h4>Your Skills</h4>
              <button 
                type="button" 
                class="btn btn-sm btn-primary"
                @click="showSkillModal = true"
              >
                Add Skill
              </button>
            </div>
            
            <div v-if="profile.skills && profile.skills.length === 0" class="empty-state">
              You haven't added any skills yet.
            </div>
            
            <div v-else class="skills-list">
              <div 
                v-for="skill in profile.skills" 
                :key="skill.id"
                class="skill-card"
              >
                <div class="skill-info">
                  <h5>{{ skill.name }}</h5>
                  <div class="skill-rating">
                    <span 
                      v-for="n in 5" 
                      :key="n"
                      :class="['rating-star', { filled: n <= skill.pivot.proficiency_level }]"
                    >★</span>
                  </div>
                </div>
                <button 
                  type="button" 
                  class="btn-icon remove"
                  @click="removeSkill(skill.id)"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
          
          <div class="certifications-section">
            <div class="section-header">
              <h4>Your Certifications</h4>
              <button 
                type="button" 
                class="btn btn-sm btn-primary"
                @click="showCertModal = true"
              >
                Add Certification
              </button>
            </div>
            
            <div v-if="profile.certifications && profile.certifications.length === 0" class="empty-state">
              You haven't added any certifications yet.
            </div>
            
            <div v-else class="certifications-list">
              <div 
                v-for="cert in profile.certifications" 
                :key="cert.id"
                class="cert-card"
              >
                <div class="cert-info">
                  <h5>{{ cert.name }}</h5>
                  <p v-if="cert.provider" class="cert-provider">{{ cert.provider }}</p>
                  <div class="cert-dates">
                    <span v-if="cert.pivot.obtained_date">
                      Obtained: {{ formatDate(cert.pivot.obtained_date) }}
                    </span>
                    <span v-if="cert.pivot.expiry_date" class="cert-expiry">
                      Expires: {{ formatDate(cert.pivot.expiry_date) }}
                    </span>
                  </div>
                </div>
                <button 
                  type="button" 
                  class="btn-icon remove"
                  @click="removeCertification(cert.id)"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Account Settings Tab -->
        <div v-if="currentTab === 3" class="tab-content card">
          <h3>Account Settings</h3>
          
          <form @submit.prevent="updatePassword" class="profile-form">
            <div class="form-group">
              <label for="current_password" class="form-label">Current Password</label>
              <input 
                id="current_password"
                v-model="passwordForm.current_password"
                type="password" 
                class="form-control" 
                required
                placeholder="Enter your current password"
              >
            </div>
            
            <div class="form-group">
              <label for="new_password" class="form-label">New Password</label>
              <input 
                id="new_password"
                v-model="passwordForm.new_password"
                type="password" 
                class="form-control" 
                required
                placeholder="Enter a new password"
              >
            </div>
            
            <div class="form-group">
              <label for="new_password_confirmation" class="form-label">Confirm New Password</label>
              <input 
                id="new_password_confirmation"
                v-model="passwordForm.new_password_confirmation"
                type="password" 
                class="form-control" 
                required
                placeholder="Confirm your new password"
              >
            </div>
            
            <div class="form-group">
              <button type="submit" class="btn btn-primary" :disabled="updatingPassword">
                {{ updatingPassword ? 'Updating...' : 'Update Password' }}
              </button>
            </div>
          </form>
          
          <div class="danger-zone">
            <h4>Danger Zone</h4>
            <p>These actions are irreversible!</p>
            
            <button class="btn btn-danger" @click="confirmDeleteAccount">
              Delete Account
            </button>
          </div>
        </div>
      </div>
      
      <!-- Skill Modal -->
      <div v-if="showSkillModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h4>Add Skill</h4>
            <button type="button" class="modal-close" @click="showSkillModal = false">×</button>
          </div>
          <div class="modal-body">
          <div class="form-group">
            <label for="skill_id" class="form-label">Select Skill</label>
            <select id="skill_id" v-model="skillForm.skill_id" class="form-control">
              <option value="">Select a skill</option>
              <option 
                v-for="skill in availableSkills" 
                :key="skill.id" 
                :value="skill.id"
              >
                {{ skill.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Proficiency Level</label>
            <div class="rating-selector">
              <button 
                v-for="level in 5" 
                :key="level"
                type="button"
                :class="['rating-btn', { active: skillForm.proficiency_level >= level }]"
                @click="skillForm.proficiency_level = level"
              >
                {{ level }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="showSkillModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="addSkill"
            :disabled="!skillForm.skill_id"
          >
            Add Skill
          </button>
        </div>
      </div>
    </div>
    
    <!-- Certification Modal -->
    <div v-if="showCertModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h4>Add Certification</h4>
          <button type="button" class="modal-close" @click="showCertModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="certification_id" class="form-label">Select Certification</label>
            <select id="certification_id" v-model="certForm.certification_id" class="form-control">
              <option value="">Select a certification</option>
              <option 
                v-for="cert in availableCertifications" 
                :key="cert.id" 
                :value="cert.id"
              >
                {{ cert.name }} {{ cert.provider ? `(${cert.provider})` : '' }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="obtained_date" class="form-label">Obtained Date</label>
            <input 
              id="obtained_date"
              v-model="certForm.obtained_date"
              type="date" 
              class="form-control"
            >
          </div>
          
          <div class="form-group">
            <label for="expiry_date" class="form-label">Expiry Date</label>
            <input 
              id="expiry_date"
              v-model="certForm.expiry_date"
              type="date" 
              class="form-control"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="showCertModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="addCertification"
            :disabled="!certForm.certification_id"
          >
            Add Certification
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h4>Delete Account</h4>
          <button type="button" class="modal-close" @click="showDeleteModal = false">×</button>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            Are you sure you want to delete your account? This action cannot be undone.
          </p>
          <p class="warning-text">
            All your data, including quiz results and progress, will be permanently deleted.
          </p>
          
          <div class="form-group">
            <label for="delete_confirmation" class="form-label">
              Type "DELETE" to confirm
            </label>
            <input 
              id="delete_confirmation"
              v-model="deleteConfirmation"
              type="text" 
              class="form-control" 
              placeholder="Type DELETE here"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="showDeleteModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-danger" 
            @click="deleteAccount"
            :disabled="deleteConfirmation !== 'DELETE'"
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Profile',
  data() {
    return {
      loading: true,
      updating: false,
      updatingPassword: false,
      error: '',
      profile: {},
      currentTab: 0,
      tabs: ['Personal Information', 'Professional Information', 'Skills & Certifications', 'Account Settings'],
      form: {
        name: '',
        gender: '',
        age: null,
        sector_id: '',
        role_id: '',
        years_experience: null,
        learning_goal: ''
      },
      passwordForm: {
        current_password: '',
        new_password: '',
        new_password_confirmation: ''
      },
      sectors: [],
      roles: [],
      allSkills: [],
      allCertifications: [],
      
      // Skill modal
      showSkillModal: false,
      skillForm: {
        skill_id: '',
        proficiency_level: 1
      },
      
      // Certification modal
      showCertModal: false,
      certForm: {
        certification_id: '',
        obtained_date: '',
        expiry_date: ''
      },
      
      // Delete account modal
      showDeleteModal: false,
      deleteConfirmation: ''
    }
  },
  computed: {
    filteredRoles() {
      if (!this.form.sector_id) return [];
      return this.roles.filter(role => role.sector_id === parseInt(this.form.sector_id));
    },
    
    availableSkills() {
      // Filter out skills that the user already has
      const userSkillIds = this.profile.skills ? this.profile.skills.map(s => s.id) : [];
      return this.allSkills.filter(skill => !userSkillIds.includes(skill.id));
    },
    
    availableCertifications() {
      // Filter out certifications that the user already has
      const userCertIds = this.profile.certifications ? this.profile.certifications.map(c => c.id) : [];
      return this.allCertifications.filter(cert => !userCertIds.includes(cert.id));
    }
  },
  created() {
    this.fetchProfile();
    this.fetchSectors();
    this.fetchRoles();
    this.fetchSkills();
    this.fetchCertifications();
  },
  methods: {
    async fetchProfile() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await axios.get('/api/profile', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
        
        // Initialize form with profile data
        this.form = {
          name: this.profile.name || '',
          gender: this.profile.gender || '',
          age: this.profile.age || null,
          sector_id: this.profile.sector_id || '',
          role_id: this.profile.role_id || '',
          years_experience: this.profile.years_experience || null,
          learning_goal: this.profile.learning_goal || ''
        };
      } catch (error) {
        console.error('Error fetching profile:', error);
        this.error = 'Failed to load profile. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchSectors() {
      try {
        const response = await axios.get('/api/sectors', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.sectors = response.data;
      } catch (error) {
        console.error('Error fetching sectors:', error);
      }
    },
    
    async fetchRoles() {
      try {
        const response = await axios.get('/api/roles', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.roles = response.data;
      } catch (error) {
        console.error('Error fetching roles:', error);
      }
    },
    
    async fetchSkills() {
      try {
        const response = await axios.get('/api/skills', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.allSkills = response.data;
      } catch (error) {
        console.error('Error fetching skills:', error);
      }
    },
    
    async fetchCertifications() {
      try {
        const response = await axios.get('/api/certifications', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.allCertifications = response.data;
      } catch (error) {
        console.error('Error fetching certifications:', error);
      }
    },
    
    onSectorChange() {
      // Reset role when sector changes
      this.form.role_id = '';
    },
    
    async updatePersonalInfo() {
      this.updating = true;
      
      try {
        const response = await axios.put('/api/profile', {
          name: this.form.name,
          gender: this.form.gender,
          age: this.form.age
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
        alert('Personal information updated successfully');
      } catch (error) {
        console.error('Error updating profile:', error);
        alert('Failed to update personal information. Please try again.');
      } finally {
        this.updating = false;
      }
    },
    
    async updateProfessionalInfo() {
      this.updating = true;
      
      try {
        const response = await axios.put('/api/profile', {
          sector_id: this.form.sector_id,
          role_id: this.form.role_id,
          years_experience: this.form.years_experience,
          learning_goal: this.form.learning_goal
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
        alert('Professional information updated successfully');
      } catch (error) {
        console.error('Error updating profile:', error);
        alert('Failed to update professional information. Please try again.');
      } finally {
        this.updating = false;
      }
    },
    
    async updatePassword() {
      if (this.passwordForm.new_password !== this.passwordForm.new_password_confirmation) {
        alert('New passwords do not match');
        return;
      }
      
      this.updatingPassword = true;
      
      try {
        await axios.put('/api/password', this.passwordForm, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        alert('Password updated successfully');
        
        // Reset form
        this.passwordForm = {
          current_password: '',
          new_password: '',
          new_password_confirmation: ''
        };
      } catch (error) {
        console.error('Error updating password:', error);
        alert('Failed to update password. ' + (error.response?.data?.message || 'Please try again.'));
      } finally {
        this.updatingPassword = false;
      }
    },
    
    async addSkill() {
      try {
        const response = await axios.put('/api/profile/skills', {
          skill_id: this.skillForm.skill_id,
          proficiency_level: this.skillForm.proficiency_level
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
        this.showSkillModal = false;
        
        // Reset form
        this.skillForm = {
          skill_id: '',
          proficiency_level: 1
        };
      } catch (error) {
        console.error('Error adding skill:', error);
        alert('Failed to add skill. Please try again.');
      }
    },
    
    async removeSkill(skillId) {
      if (!confirm('Are you sure you want to remove this skill?')) return;
      
      try {
        const response = await axios.delete(`/api/profile/skills/${skillId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
      } catch (error) {
        console.error('Error removing skill:', error);
        alert('Failed to remove skill. Please try again.');
      }
    },
    
    async addCertification() {
      try {
        const response = await axios.put('/api/profile/certifications', {
          certification_id: this.certForm.certification_id,
          obtained_date: this.certForm.obtained_date || null,
          expiry_date: this.certForm.expiry_date || null
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
        this.showCertModal = false;
        
        // Reset form
        this.certForm = {
          certification_id: '',
          obtained_date: '',
          expiry_date: ''
        };
      } catch (error) {
        console.error('Error adding certification:', error);
        alert('Failed to add certification. Please try again.');
      }
    },
    
    async removeCertification(certId) {
      if (!confirm('Are you sure you want to remove this certification?')) return;
      
      try {
        const response = await axios.delete(`/api/profile/certifications/${certId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.profile = response.data;
      } catch (error) {
        console.error('Error removing certification:', error);
        alert('Failed to remove certification. Please try again.');
      }
    },
    
    confirmDeleteAccount() {
      this.showDeleteModal = true;
      this.deleteConfirmation = '';
    },
    
    async deleteAccount() {
      if (this.deleteConfirmation !== 'DELETE') return;
      
      try {
        await axios.delete('/api/profile', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        // Log the user out
        this.$store.dispatch('auth/logout');
        this.$router.push('/login');
      } catch (error) {
        console.error('Error deleting account:', error);
        alert('Failed to delete account. Please try again.');
      } finally {
        this.showDeleteModal = false;
      }
    },
    
    getInitials(name) {
      if (!name) return '';
      
      return name
        .split(' ')
        .map(part => part[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  }
}
</script>

<style scoped>
.profile-page {
  padding: 2rem 0;
}

.loader, .error {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #ef4444;
}

.card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.profile-header {
  display: flex;
  align-items: center;
}

.avatar {
  width: 4rem;
  height: 4rem;
  background-color: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-right: 1.5rem;
}

.profile-info h2 {
  margin-bottom: 0.25rem;
}

.profile-info p {
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.tab-navigation {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
  overflow-x: auto;
}

.tab-button {
  padding: 0.75rem 1.25rem;
  background-color: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #4b5563;
  white-space: nowrap;
}

.tab-button:hover {
  color: #111827;
}

.tab-button.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  padding: 1.5rem;
}

.profile-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.skills-list, .certifications-list {
  margin-bottom: 2rem;
}

.skill-card, .cert-card {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.skill-info, .cert-info {
  flex: 1;
}

.skill-info h5, .cert-info h5 {
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.skill-rating {
  display: flex;
}

.rating-star {
  color: #d1d5db;
  margin-right: 0.25rem;
}

.rating-star.filled {
  color: #f59e0b;
}

.cert-provider {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.cert-dates {
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  gap: 1rem;
}

.cert-expiry {
  color: #ef4444;
}

.btn-icon {
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-icon.remove {
  color: #ef4444;
}

.btn-icon.remove:hover {
  background-color: #fee2e2;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.rating-selector {
  display: flex;
  gap: 0.5rem;
}

.rating-btn {
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.rating-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.danger-zone {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f3f4f6;
}

.danger-zone h4 {
  color: #ef4444;
}

.danger-zone p {
  color: #6b7280;
  margin-bottom: 1rem;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  border: 1px solid #ef4444;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.warning-text {
  color: #ef4444;
  font-weight: 500;
  margin-bottom: 1rem;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h4 {
  margin-bottom: 0;
}

.modal-close {
  background-color: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}
</style>
<template>
  <div class="profile-container">
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Loading profile...</span>
    </div>
    
    <div v-else-if="error" class="error-message">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{{ error }}</span>
    </div>
    
    <div v-else class="profile-content">
      <h1 class="page-title">Your Profile</h1>
      
      <!-- Profile Card -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar">
            {{ getInitials(profile.name) }}
          </div>
          <div class="profile-info">
            <h2>{{ profile.name }}</h2>
            <p class="profile-email">{{ profile.email }}</p>
            <p v-if="profile.sector && profile.role" class="profile-role">
              {{ profile.role.name }} at {{ profile.sector.name }} sector
            </p>
          </div>
        </div>
      </div>
      
      <!-- Tabs -->
      <div class="tabs-container">
        <div class="tabs-header">
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
        <div v-if="currentTab === 0" class="tab-content">
          <div class="section-header">
            <div class="section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <h3>Personal Information</h3>
          </div>
          
          <form @submit.prevent="updatePersonalInfo" class="profile-form">
            <div class="form-group">
              <label for="name">Full Name</label>
              <div class="input-container">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <input 
                  id="name"
                  v-model="form.name"
                  type="text" 
                  required
                  placeholder="Enter your full name"
                >
              </div>
            </div>
            
            <div class="form-group">
              <label for="gender">Gender</label>
              <div class="select-container">
                <select id="gender" v-model="form.gender">
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="age">Age</label>
              <div class="input-container">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <input 
                  id="age"
                  v-model.number="form.age"
                  type="number" 
                  min="18"
                  max="100"
                  placeholder="Enter your age"
                >
              </div>
            </div>
            
            <div class="form-action">
              <button type="submit" class="btn-primary" :disabled="updating">
                <span>{{ updating ? 'Updating...' : 'Update Personal Information' }}</span>
                <div v-if="updating" class="btn-spinner"></div>
              </button>
            </div>
          </form>
        </div>
        
        <!-- Professional Information Tab -->
        <div v-if="currentTab === 1" class="tab-content">
          <div class="section-header">
            <div class="section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
              </svg>
            </div>
            <h3>Professional Information</h3>
          </div>
          
          <form @submit.prevent="updateProfessionalInfo" class="profile-form">
            <div class="form-group">
              <label for="sector">Sector</label>
              <div class="select-container">
                <select 
                  id="sector" 
                  v-model="form.sector_id" 
                  @change="onSectorChange"
                >
                  <option value="">Select sector</option>
                  <option v-for="sector in sectors" :key="sector.id" :value="sector.id">
                    {{ sector.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="role">Role</label>
              <div class="select-container">
                <select 
                  id="role" 
                  v-model="form.role_id" 
                  :disabled="!form.sector_id"
                >
                  <option value="">Select role</option>
                  <option v-for="role in filteredRoles" :key="role.id" :value="role.id">
                    {{ role.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="years_experience">Years of Experience</label>
              <div class="input-container">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <input 
                  id="years_experience"
                  v-model.number="form.years_experience"
                  type="number" 
                  min="0"
                  max="50"
                  placeholder="Enter years of experience"
                >
              </div>
            </div>
            
            <div class="form-group">
              <label for="learning_goal">Learning Goal</label>
              <textarea 
                id="learning_goal"
                v-model="form.learning_goal"
                rows="3"
                placeholder="What do you hope to achieve with cybersecurity training?"
              ></textarea>
            </div>
            
            <div class="form-action">
              <button type="submit" class="btn-primary" :disabled="updating">
                <span>{{ updating ? 'Updating...' : 'Update Professional Information' }}</span>
                <div v-if="updating" class="btn-spinner"></div>
              </button>
            </div>
          </form>
        </div>
        
        <!-- Skills & Certifications Tab -->
        <div v-if="currentTab === 2" class="tab-content">
          <!-- Skills Section -->
          <div class="sub-section">
            <div class="section-header">
              <div class="section-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
              </div>
              <h3>Your Skills</h3>
              <button 
                type="button" 
                class="btn-secondary add-button"
                @click="showSkillModal = true"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add Skill
              </button>
            </div>
            
            <div v-if="profile.skills && profile.skills.length === 0" class="empty-state">
              <div class="empty-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
              </div>
              <p>You haven't added any skills yet</p>
              <button 
                type="button" 
                class="btn-secondary add-button-empty"
                @click="showSkillModal = true"
              >
                Add your first skill
              </button>
            </div>
            
            <div v-else class="skills-list">
              <div 
                v-for="skill in profile.skills" 
                :key="skill.id"
                class="skill-card"
              >
                <div class="skill-info">
                  <h4>{{ skill.name }}</h4>
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
                  class="btn-icon"
                  @click="removeSkill(skill.id)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Certifications Section -->
          <div class="sub-section">
            <div class="section-header">
              <div class="section-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path>
                  <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Z"></path>
                  <path d="m8.5 8.5 7 7"></path>
                </svg>
              </div>
              <h3>Your Certifications</h3>
              <button 
                type="button" 
                class="btn-secondary add-button"
                @click="showCertModal = true"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add Certification
              </button>
            </div>
            
            <div v-if="profile.certifications && profile.certifications.length === 0" class="empty-state">
              <div class="empty-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path>
                  <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Z"></path>
                  <path d="m8.5 8.5 7 7"></path>
                </svg>
              </div>
              <p>You haven't added any certifications yet</p>
              <button 
                type="button" 
                class="btn-secondary add-button-empty"
                @click="showCertModal = true"
              >
                Add your first certification
              </button>
            </div>
            
            <div v-else class="certs-list">
              <div 
                v-for="cert in profile.certifications" 
                :key="cert.id"
                class="cert-card"
              >
                <div class="cert-info">
                  <h4>{{ cert.name }}</h4>
                  <p v-if="cert.provider" class="cert-provider">{{ cert.provider }}</p>
                  <div class="cert-dates">
                    <span v-if="cert.pivot.obtained_date" class="date-tag obtained">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                      </svg>
                      Obtained: {{ formatDate(cert.pivot.obtained_date) }}
                    </span>
                    <span v-if="cert.pivot.expiry_date" class="date-tag expiry">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                      </svg>
                      Expires: {{ formatDate(cert.pivot.expiry_date) }}
                    </span>
                  </div>
                </div>
                <button 
                  type="button" 
                  class="btn-icon"
                  @click="removeCertification(cert.id)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Account Settings Tab -->
        <div v-if="currentTab === 3" class="tab-content">
          <div class="section-header">
            <div class="section-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
            </div>
            <h3>Account Settings</h3>
          </div>
          
          <!-- Password Update Form -->
          <div class="password-section">
            <h4>Change Password</h4>
            <form @submit.prevent="updatePassword" class="profile-form">
              <div class="form-group">
                <label for="current_password">Current Password</label>
                <div class="input-container">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  <input 
                    id="current_password"
                    v-model="passwordForm.current_password"
                    type="password" 
                    required
                    placeholder="Enter your current password"
                  >
                </div>
              </div>
              
              <div class="form-group">
                <label for="new_password">New Password</label>
                <div class="input-container">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  <input 
                    id="new_password"
                    v-model="passwordForm.new_password"
                    type="password" 
                    required
                    placeholder="Enter a new password"
                  >
                </div>
              </div>
              
              <div class="form-group">
                <label for="new_password_confirmation">Confirm New Password</label>
                <div class="input-container">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 12l2 2 4-4"></path>
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  <input 
                    id="new_password_confirmation"
                    v-model="passwordForm.new_password_confirmation"
                    type="password" 
                    required
                    placeholder="Confirm your new password"
                  >
                </div>
              </div>
              
              <div class="form-action">
                <button type="submit" class="btn-primary" :disabled="updatingPassword">
                  <span>{{ updatingPassword ? 'Updating...' : 'Update Password' }}</span>
                  <div v-if="updatingPassword" class="btn-spinner"></div>
                </button>
              </div>
            </form>
          </div>
          
          <!-- Danger Zone -->
          <div class="danger-zone">
            <h4>Danger Zone</h4>
            <p>Once you delete your account, there is no going back. Please be certain.</p>
            
            <button class="btn-danger" @click="confirmDeleteAccount">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18"></path>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path>
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Skill Modal -->
    <div v-if="showSkillModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h4>Add Skill</h4>
          <button type="button" class="modal-close" @click="showSkillModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="skill_id">Select Skill</label>
            <div class="select-container">
              <select id="skill_id" v-model="skillForm.skill_id">
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
          </div>
          
          <div class="form-group">
            <label>Proficiency Level</label>
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
            class="btn-text" 
            @click="showSkillModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn-primary" 
            @click="addSkill"
            :disabled="!skillForm.skill_id"
          >
            Add Skill
          </button>
        </div>
      </div>
    </div>
    
    <!-- Certification Modal -->
    <div v-if="showCertModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h4>Add Certification</h4>
          <button type="button" class="modal-close" @click="showCertModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="certification_id">Select Certification</label>
            <div class="select-container">
              <select id="certification_id" v-model="certForm.certification_id">
                ```vue
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
          </div>
          
          <div class="form-group">
            <label for="obtained_date">Obtained Date</label>
            <div class="input-container">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <input 
                id="obtained_date"
                v-model="certForm.obtained_date"
                type="date" 
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="expiry_date">Expiry Date</label>
            <div class="input-container">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <input 
                id="expiry_date"
                v-model="certForm.expiry_date"
                type="date" 
              >
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn-text" 
            @click="showCertModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn-primary" 
            @click="addCertification"
            :disabled="!certForm.certification_id"
          >
            Add Certification
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header danger">
          <h4>Delete Account</h4>
          <button type="button" class="modal-close" @click="showDeleteModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="warning-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          
          <p class="warning-text">
            Are you sure you want to delete your account? This action cannot be undone.
          </p>
          <p class="warning-description">
            All your data, including quiz results and progress, will be permanently deleted.
          </p>
          
          <div class="form-group">
            <label for="delete_confirmation">
              Type "DELETE" to confirm
            </label>
            <div class="input-container">
              <input 
                id="delete_confirmation"
                v-model="deleteConfirmation"
                type="text" 
                placeholder="Type DELETE here"
              >
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn-text" 
            @click="showDeleteModal = false"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn-danger" 
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
/* Professional dark-themed design matching the dashboard */
:root {
  --primary-bg: #f8f9fa;
  --card-bg: #ffffff;
  --text-color: #333333;
  --text-secondary: #6c757d;
  --primary-color: #1a73e8;
  --primary-hover: #1765cc;
  --secondary-color: #5f6368;
  --border-color: #e0e0e0;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  --border-radius: 8px;
  --danger-color: #d93025;
}

.profile-container {
  font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px 20px;
  color: var(--text-color);
  background-color: var(--primary-bg);
}

/* Page title */
.page-title {
  font-size: 28px;
  font-weight: 500;
  margin-bottom: 25px;
  color: var(--text-color);
}

/* Loading state */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(26, 115, 232, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error state */
.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 30px 0;
  padding: 20px;
  color: var(--danger-color);
  background-color: #fce8e6;
  border-radius: var(--border-radius);
}

/* Profile card */
.profile-card {
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
}

.profile-header {
  display: flex;
  align-items: center;
}

.avatar {
  width: 70px;
  height: 70px;
  background-color: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 600;
  color: white;
  margin-right: 25px;
}

.profile-info h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 500;
}

.profile-email {
  color: var(--text-secondary);
  margin: 0 0 6px 0;
  font-size: 15px;
}

.profile-role {
  color: var(--text-secondary);
  margin: 0;
  font-size: 15px;
}

/* Tabs */
.tabs-container {
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background-color: #f1f3f4;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.tab-button {
  padding: 16px 24px;
  background-color: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-button:hover {
  color: var(--text-color);
  background-color: rgba(0, 0, 0, 0.03);
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-content {
  padding: 30px;
}

/* Section headers */
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.section-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e8f0fe;
  margin-right: 12px;
}

.section-icon svg {
  color: var(--primary-color);
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--text-color);
  flex: 1;
}

.sub-section {
  margin-bottom: 40px;
}

/* Form elements */
.profile-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-container svg {
  position: absolute;
  left: 12px;
  color: var(--secondary-color);
}

.input-container input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 15px;
  background-color: #f1f3f4;
}

.input-container input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
  background-color: white;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 15px;
  font-family: inherit;
  background-color: #f1f3f4;
  resize: vertical;
  min-height: 100px;
}

textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
  background-color: white;
}

.select-container {
  position: relative;
}

.select-container select {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 15px;
  background-color: #f1f3f4;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235f6368' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.select-container select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
  background-color: white;
}

.select-container select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-action {
  margin-top: 30px;
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #e8f0fe;
  color: var(--primary-color);
  border: none;
  border-radius: var(--border-radius);
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #d2e3fc;
}

.btn-text {
  background-color: transparent;
  color: var(--secondary-color);
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 16px;
}

.btn-text:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: var(--border-radius);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #fce8e6;
  color: var(--danger-color);
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger:hover {
  background-color: #fadbd8;
}

.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.add-button {
  height: 36px;
}

.add-button-empty {
  margin-top: 15px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background-color: transparent;
  color: var(--secondary-color);
  cursor: pointer;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Skills and certifications sections */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  border: 1px dashed var(--border-color);
  border-radius: var(--border-radius);
  background-color: #f8f9fa;
}

.empty-state .empty-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #f1f3f4;
  margin-bottom: 16px;
  color: var(--secondary-color);
}

.empty-state p {
  margin: 0 0 5px 0;
  font-size: 15px;
  color: var(--text-secondary);
}

.skills-list, .certs-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.skill-card, .cert-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.skill-info, .cert-info {
  flex: 1;
}

.skill-info h4, .cert-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
}

.skill-rating {
  display: flex;
}

.rating-star {
  color: #e0e0e0;
  font-size: 18px;
}

.rating-star.filled {
  color: #fbbc04;
}

.cert-provider {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.cert-dates {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  white-space: nowrap;
}

.date-tag.obtained {
  background-color: #e6f4ea;
  color: #137333;
}

.date-tag.expiry {
  background-color: #fce8e6;
  color: #c5221f;
}

/* Rating selector */
.rating-selector {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.rating-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background-color: white;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
}

.rating-btn.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* Password section */
.password-section {
  margin-bottom: 40px;
}

.password-section h4 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 20px;
  color: var(--text-color);
}

/* Danger zone */
.danger-zone {
  margin-top: 15px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.danger-zone h4 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
  color: var(--danger-color);
}

.danger-zone p {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header.danger {
  border-bottom-color: #fce8e6;
}

.modal-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.modal-header.danger h4 {
  color: var(--danger-color);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: var(--secondary-color);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  gap: 12px;
}

/* Warning styles for delete account */
.warning-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  color: var(--danger-color);
}

.warning-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--danger-color);
  margin-bottom: 10px;
  text-align: center;
}

.warning-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  text-align: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .tabs-header {
    overflow-x: auto;
  }
  
  .tab-button {
    padding: 16px 15px;
    font-size: 14px;
  }
  
  .tab-content {
    padding: 20px;
  }
  
  .skills-list, .certs-list {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .section-header {
    flex-wrap: wrap;
  }
  
  .section-header .btn-secondary {
    margin-top: 10px;
    margin-left: auto;
  }
}
</style>
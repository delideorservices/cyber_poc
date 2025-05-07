<template>
    <div class="register-page container">
      <div class="card">
        <h1 class="text-center">Register</h1>
        <div v-if="errorMessage" class="alert alert-danger">
          {{ errorMessage }}
        </div>
        
        <form @submit.prevent="register" class="register-form">
          <!-- Step indicator -->
          <div class="registration-steps">
            <div 
              v-for="(step, index) in steps" 
              :key="index"
              :class="['step', { 'active': currentStep === index, 'completed': currentStep > index }]"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-label">{{ step }}</div>
            </div>
          </div>
          
          <!-- Step 1: Basic Information -->
          <div v-if="currentStep === 0" class="step-content">
            <h3>Basic Information</h3>
            
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
              <div v-if="errors.name" class="form-error">{{ errors.name[0] }}</div>
            </div>
            
            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <input 
                id="email"
                v-model="form.email"
                type="email" 
                class="form-control" 
                required
                placeholder="Enter your email"
              >
              <div v-if="errors.email" class="form-error">{{ errors.email[0] }}</div>
            </div>
            
            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <input 
                id="password"
                v-model="form.password"
                type="password" 
                class="form-control" 
                required
                placeholder="Enter a password"
              >
              <div v-if="errors.password" class="form-error">{{ errors.password[0] }}</div>
            </div>
            
            <div class="form-group">
              <label for="password_confirmation" class="form-label">Confirm Password</label>
              <input 
                id="password_confirmation"
                v-model="form.password_confirmation"
                type="password" 
                class="form-control" 
                required
                placeholder="Confirm your password"
              >
            </div>
          </div>
          
          <!-- Step 2: Personal Information -->
          <div v-if="currentStep === 1" class="step-content">
            <h3>Personal Information</h3>
            
            <div class="form-group">
              <label for="gender" class="form-label">Gender</label>
              <select id="gender" v-model="form.gender" class="form-control">
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
              <div v-if="errors.gender" class="form-error">{{ errors.gender[0] }}</div>
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
              <div v-if="errors.age" class="form-error">{{ errors.age[0] }}</div>
            </div>
          </div>
          
          <!-- Step 3: Sector and Role -->
          <div v-if="currentStep === 2" class="step-content">
            <h3>Professional Information</h3>
            
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
              <div v-if="errors.sector_id" class="form-error">{{ errors.sector_id[0] }}</div>
            </div>
            
            <div class="form-group">
              <label for="role" class="form-label">Role</label>
              <select id="role" v-model="form.role_id" class="form-control" :disabled="!form.sector_id">
                <option value="">Select role</option>
                <option v-for="role in filteredRoles" :key="role.id" :value="role.id">
                  {{ role.name }}
                </option>
              </select>
              <div v-if="errors.role_id" class="form-error">{{ errors.role_id[0] }}</div>
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
              <div v-if="errors.years_experience" class="form-error">{{ errors.years_experience[0] }}</div>
            </div>
          </div>
          
          <!-- Step 4: Skills and Certifications -->
          <div v-if="currentStep === 3" class="step-content">
            <h3>Skills and Certifications</h3>
            
            <div class="form-group">
              <label class="form-label">Select Your Skills (Choose up to 3)</label>
              <div class="skills-container">
                <div 
                  v-for="skill in skills" 
                  :key="skill.id"
                  :class="['skill-item', { 'selected': isSkillSelected(skill.id) }]"
                  @click="toggleSkill(skill.id)"
                >
                  {{ skill.name }}
                </div>
              </div>
              <div v-if="errors.skills" class="form-error">{{ errors.skills[0] }}</div>
            </div>
            
            <div class="form-group" v-if="selectedSkills.length > 0">
              <label class="form-label">Rate Your Proficiency</label>
              <div v-for="skillId in selectedSkills" :key="skillId" class="skill-rating">
                <div class="skill-name">{{ getSkillName(skillId) }}</div>
                <div class="rating-selector">
                  <div 
                    v-for="level in 5" 
                    :key="level"
                    :class="['rating-option', { 'selected': getSkillProficiency(skillId) >= level }]"
                    @click="setSkillProficiency(skillId, level)"
                  >
                    {{ level }}
                  </div>
                </div>
              </div>
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
              <div v-if="errors.learning_goal" class="form-error">{{ errors.learning_goal[0] }}</div>
            </div>
          </div>
          
          <!-- Navigation buttons -->
          <div class="form-nav">
            <button 
              v-if="currentStep > 0" 
              type="button" 
              class="btn btn-secondary" 
              @click="prevStep"
            >
              Previous
            </button>
            
            <button 
              v-if="currentStep < steps.length - 1" 
              type="button" 
              class="btn btn-primary" 
              @click="nextStep"
            >
              Next
            </button>
            
            <button 
              v-else 
              type="submit" 
              class="btn btn-success" 
              :disabled="loading"
            >
              {{ loading ? 'Registering...' : 'Complete Registration' }}
            </button>
          </div>
        </form>
        
        <div class="text-center mt-4">
          <p>Already have an account? <router-link to="/login">Login</router-link></p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'Register',
    data() {
      return {
        steps: [
          'Basic Information', 
          'Personal Information', 
          'Professional Information', 
          'Skills and Certifications'
        ],
        currentStep: 0,
        form: {
          name: '',
          email: '',
          password: '',
          password_confirmation: '',
          gender: '',
          age: null,
          sector_id: '',
          role_id: '',
          years_experience: null,
          learning_goal: '',
          skills: []
        },
        loading: false,
        errorMessage: '',
        errors: {},
        sectors: [],
        roles: [],
        skills: [],
        selectedSkills: [],
        skillProficiencies: {}
      }
    },
    computed: {
      filteredRoles() {
        if (!this.form.sector_id) return [];
        return this.roles.filter(role => role.sector_id === this.form.sector_id);
      }
    },
    created() {
      this.fetchSectors();
      this.fetchRoles();
      this.fetchSkills();
    },
    methods: {
      async fetchSectors() {
        try {
          const response = await axios.get('/api/sectors');
          this.sectors = response.data;
        } catch (error) {
          console.error('Error fetching sectors:', error);
        }
      },
      
      async fetchRoles() {
        try {
          const response = await axios.get('/api/roles');
          this.roles = response.data;
        } catch (error) {
          console.error('Error fetching roles:', error);
        }
      },
      
      async fetchSkills() {
        try {
          const response = await axios.get('/api/skills');
          this.skills = response.data;
        } catch (error) {
          console.error('Error fetching skills:', error);
        }
      },
      
      onSectorChange() {
        // Reset role when sector changes
        this.form.role_id = '';
      },
      
      isSkillSelected(skillId) {
        return this.selectedSkills.includes(skillId);
      },
      
      toggleSkill(skillId) {
        const index = this.selectedSkills.indexOf(skillId);
        if (index === -1) {
          // Only allow up to 3 skills
          if (this.selectedSkills.length >= 3) return;
          
          this.selectedSkills.push(skillId);
          this.skillProficiencies[skillId] = 1; // Default proficiency
        } else {
          this.selectedSkills.splice(index, 1);
          delete this.skillProficiencies[skillId];
        }
        
        // Update form.skills
        this.updateFormSkills();
      },
      
      getSkillName(skillId) {
        const skill = this.skills.find(s => s.id === skillId);
        return skill ? skill.name : '';
      },
      
      getSkillProficiency(skillId) {
        return this.skillProficiencies[skillId] || 1;
      },
      
      setSkillProficiency(skillId, level) {
        this.skillProficiencies[skillId] = level;
        
        // Update form.skills
        this.updateFormSkills();
      },
      
      updateFormSkills() {
        this.form.skills = this.selectedSkills.map(skillId => ({
          id: skillId,
          proficiency_level: this.skillProficiencies[skillId] || 1
        }));
      },
      
      validateCurrentStep() {
        this.errors = {};
        
        // Validate step 1
        if (this.currentStep === 0) {
          if (!this.form.name) this.errors.name = ['Name is required'];
          if (!this.form.email) this.errors.email = ['Email is required'];
          if (!this.form.password) this.errors.password = ['Password is required'];
          if (this.form.password !== this.form.password_confirmation) {
            this.errors.password = ['Passwords do not match'];
          }
        }
        
        // Validate step 2
        else if (this.currentStep === 1) {
          // Age is optional, but if provided, must be valid
          if (this.form.age && (this.form.age < 18 || this.form.age > 100)) {
            this.errors.age = ['Age must be between 18 and 100'];
          }
        }
        
        // Validate step 3
        else if (this.currentStep === 2) {
          if (!this.form.sector_id) this.errors.sector_id = ['Sector is required'];
          if (!this.form.role_id) this.errors.role_id = ['Role is required'];
        }
        
        return Object.keys(this.errors).length === 0;
      },
      
      nextStep() {
        if (this.validateCurrentStep()) {
          this.currentStep++;
        }
      },
      
      prevStep() {
        this.currentStep--;
      },
      
      async register() {
        if (!this.validateCurrentStep()) {
          return;
        }
        
        this.loading = true;
        this.errorMessage = '';
        
        try {
          await this.$store.dispatch('auth/register', this.form);
          this.$router.push('/dashboard');
        } catch (error) {
          console.error('Registration error:', error);
          
          if (error.response?.data?.errors) {
            this.errors = error.response.data.errors;
            this.errorMessage = 'Please correct the errors in the form.';
          } else {
            this.errorMessage = error.response?.data?.message || 'Registration failed. Please try again.';
          }
        } finally {
          this.loading = false;
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .register-page {
    max-width: 700px;
    margin: 2rem auto;
  }
  
  .text-center {
    text-align: center;
  }
  
  .mt-4 {
    margin-top: 1rem;
  }
  
  .alert {
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid transparent;
    border-radius: 0.25rem;
  }
  
  .alert-danger {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
  }
  
  .form-error {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  .registration-steps {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2rem;
    position: relative;
  }
  
  .registration-steps::before {
    content: '';
    position: absolute;
    top: 1rem;
    left: 0;
    right: 0;
    height: 2px;
    background-color: #e5e7eb;
    z-index: 0;
  }
  
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 1;
  }
  
  .step-number {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background-color: #e5e7eb;
    color: #4b5563;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  
  .step.active .step-number {
    background-color: #3b82f6;
    color: white;
  }
  
  .step.completed .step-number {
    background-color: #10b981;
    color: white;
  }
  
  .step-label {
    font-size: 0.75rem;
    color: #6b7280;
  }
  
  .step.active .step-label {
    color: #111827;
    font-weight: 600;
  }
  
  .step-content {
    margin-bottom: 2rem;
  }
  
  .form-nav {
    display: flex;
    justify-content: space-between;
  }
  
  .skills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .skill-item {
    padding: 0.5rem 1rem;
    background-color: #f3f4f6;
    border-radius: 9999px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .skill-item:hover {
    background-color: #e5e7eb;
  }
  
  .skill-item.selected {
    background-color: #dbeafe;
    border: 1px solid #93c5fd;
  }
  
  .skill-rating {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    background-color: #f9fafb;
    border-radius: 0.25rem;
  }
  
  .skill-name {
    flex: 1;
    font-weight: 500;
  }
  
  .rating-selector {
    display: flex;
    gap: 0.25rem;
  }
  
  .rating-option {
    width: 1.75rem;
    height: 1.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #e5e7eb;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .rating-option:hover {
    background-color: #d1d5db;
  }
  
  .rating-option.selected {
    background-color: #3b82f6;
    color: white;
  }
  
  .btn-success {
    color: white;
    background-color: #10b981;
    border: 1px solid #10b981;
  }
  
  .btn-success:hover {
    background-color: #059669;
  }
  </style>
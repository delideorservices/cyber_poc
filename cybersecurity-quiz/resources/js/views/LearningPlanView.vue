<template>
  <div class="learning-plan-page">
    <h1 class="page-title">Your Learning Plan</h1>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <span>Loading your learning plan...</span>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!learningPlan" class="empty-card">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
      </div>
      <h2>No Learning Plan Found</h2>
      <p>Generate a personalized learning plan based on your quiz results and skill gaps</p>
      <button class="btn-primary" @click="generatePlan" :disabled="generating">
        {{ generating ? 'Generating...' : 'Generate Learning Plan' }}
      </button>
    </div>
    
    <!-- Learning Plan Content -->
    <div v-else class="plan-container">
      <div class="plan-header">
        <div>
          <h2>{{ learningPlan.title }}</h2>
          <p class="plan-description">{{ learningPlan.description }}</p>
        </div>
        <div class="plan-meta">
          <div class="meta-item">
            <span class="meta-label">Status:</span>
            <span class="status-badge" :class="learningPlan.status">
              {{ learningPlan.status }}
            </span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Target Date:</span>
            <span>{{ formatDate(learningPlan.target_completion_date) }}</span>
          </div>
        </div>
      </div>
      
      <div class="plan-progress">
        <div class="progress-header">
          <h3>Overall Progress</h3>
          <span class="progress-percentage">{{ learningPlan.overall_progress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-filled" :style="{ width: `${learningPlan.overall_progress}%` }"></div>
        </div>
      </div>
      
      <h3 class="modules-title">Learning Modules</h3>
      
      <div class="modules-list">
        <div v-for="module in learningPlan.modules" :key="module.id" 
             class="module-card" :class="module.status">
          <div class="module-header">
            <div class="module-title-area">
              <h4>{{ module.title }}</h4>
              <span class="module-type-badge" :class="module.module_type">
                {{ formatModuleType(module.module_type) }}
              </span>
            </div>
            <div class="module-status-area">
              <span class="status-indicator" :class="module.status"></span>
              <span class="status-text">{{ formatStatus(module.status) }}</span>
            </div>
          </div>
          
          <p class="module-description">{{ module.description }}</p>
          
          <div class="module-meta">
            <div class="meta-tag">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>{{ module.estimated_hours }} hours</span>
            </div>
            
            <div class="meta-tag">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h13l4-3.5L18 6z"></path>
                <path d="M12 13v9"></path>
                <path d="M12 2v4"></path>
              </svg>
              <span>{{ formatDifficulty(module.difficulty_level) }}</span>
            </div>
          </div>
          
          <div class="module-actions">
            <button class="btn-module" @click="startModule(module)" 
                    :disabled="module.status === 'completed'">
              {{ getButtonText(module) }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'LearningPlanView',
  data() {
    return {
      generating: false
    }
  },
  computed: {
    ...mapGetters({
      learningPlan: 'learningPlan/learningPlan',
      loading: 'learningPlan/loading',
      error: 'learningPlan/error'
    })
  },
  created() {
    this.fetchLearningPlan()
  },
  methods: {
    ...mapActions({
      fetchLearningPlanAction: 'learningPlan/fetchLearningPlan',
      generateLearningPlanAction: 'learningPlan/generateLearningPlan',
      startModuleAction: 'learningPlan/startModule'
    }),
    async fetchLearningPlan() {
      try {
        await this.fetchLearningPlanAction()
      } catch (error) {
        console.error('Error fetching learning plan:', error)
      }
    },
    async generatePlan() {
      this.generating = true
      try {
        await this.generateLearningPlanAction()
      } catch (error) {
        console.error('Error generating learning plan:', error)
      } finally {
        this.generating = false
      }
    },
    async startModule(module) {
      try {
        const response = await this.startModuleAction(module.id)
        
        // Navigate based on module type
        if (module.module_type === 'quiz') {
          this.$router.push(`/quizzes/${module.content_reference_id}`)
        } else if (module.module_type === 'practice') {
          this.$router.push(`/skill-improvement/practice/${module.content_reference_id}`)
        } else if (module.module_type === 'resource') {
          this.$router.push(`/resources/${module.content_reference_id}`)
        }
      } catch (error) {
        console.error('Error starting module:', error)
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },
    formatModuleType(type) {
      const types = {
        'quiz': 'Quiz',
        'practice': 'Practice',
        'resource': 'Resource',
        'assessment': 'Assessment'
      }
      return types[type] || type
    },
    formatStatus(status) {
      const statuses = {
        'not_started': 'Not Started',
        'in_progress': 'In Progress',
        'completed': 'Completed'
      }
      return statuses[status] || status
    },
    formatDifficulty(level) {
      const levels = {
        1: 'Beginner',
        2: 'Easy',
        3: 'Intermediate',
        4: 'Advanced',
        5: 'Expert'
      }
      return levels[level] || level
    },
    getButtonText(module) {
      if (module.status === 'not_started') {
        return 'Start'
      } else if (module.status === 'in_progress') {
        return 'Continue'
      } else {
        return 'Completed'
      }
    }
  }
}
</script>
<style scoped>
.learning-plan-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #333;
}

/* Loading State */
.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(26, 115, 232, 0.1);
  border-radius: 50%;
  border-top-color: #1a73e8;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.empty-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #f1f3f4;
  margin-bottom: 24px;
  color: #5f6368;
}

.empty-card h2 {
  font-size: 20px;
  margin: 0 0 10px;
  font-weight: 500;
}

.empty-card p {
  margin: 0 0 24px;
  color: #5f6368;
  max-width: 400px;
}

/* Plan Container */
.plan-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.plan-header h2 {
  font-size: 20px;
  margin: 0 0 8px;
  color: #333;
  font-weight: 500;
}

.plan-description {
  color: #5f6368;
  margin: 0;
  max-width: 600px;
}

.plan-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-weight: 500;
  color: #5f6368;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.completed {
  background-color: #e0f2f1;
  color: #00796b;
}

.status-badge.archived {
  background-color: #f5f5f5;
  color: #757575;
}

/* Progress Section */
.plan-progress {
  margin-bottom: 32px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-header h3 {
  font-size: 16px;
  margin: 0;
  font-weight: 500;
  color: #333;
}

.progress-percentage {
  font-weight: 500;
  color: #333;
}

.progress-bar {
  height: 8px;
  background-color: #f1f3f4;
  border-radius: 4px;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  background-color: #1a73e8;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Modules Section */
.modules-title {
  font-size: 18px;
  margin: 0 0 16px;
  font-weight: 500;
  color: #333;
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-card {
  background-color: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  padding: 20px;
  transition: box-shadow 0.3s ease;
}

.module-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.module-card.completed {
  border-left: 4px solid #00796b;
}

.module-card.in_progress {
  border-left: 4px solid #1a73e8;
}

.module-card.not_started {
  border-left: 4px solid #9e9e9e;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.module-title-area h4 {
  font-size: 16px;
  margin: 0 0 8px;
  font-weight: 500;
  color: #333;
}

.module-type-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background-color: #f1f3f4;
  color: #5f6368;
}

.module-type-badge.quiz {
  background-color: #e8f0fe;
  color: #1a73e8;
}

.module-type-badge.practice {
  background-color: #e6f4ea;
  color: #137333;
}

.module-type-badge.resource {
  background-color: #fef7e0;
  color: #ea8600;
}

.module-type-badge.assessment {
  background-color: #fce8e6;
  color: #c5221f;
}

.module-status-area {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.completed {
  background-color: #00796b;
}

.status-indicator.in_progress {
  background-color: #1a73e8;
}

.status-indicator.not_started {
  background-color: #9e9e9e;
}

.status-text {
  font-size: 12px;
  color: #5f6368;
}

.module-description {
  color: #5f6368;
  margin: 0 0 16px;
  font-size: 14px;
}

.module-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5f6368;
}

.meta-tag svg {
  color: #5f6368;
}

.module-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-module {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-module:hover {
  background-color: #1765cc;
}

.btn-module:disabled {
  background-color: #dadce0;
  color: #5f6368;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #1765cc;
}

.btn-primary:disabled {
  background-color: #dadce0;
  color: #5f6368;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .plan-header, .module-header {
    flex-direction: column;
  }
  
  .plan-meta {
    margin-top: 16px;
  }
  
  .meta-item {
    justify-content: flex-start;
  }
}
</style>
<template>
  <div class="learning-plan-container">
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Loading your learning plan...</span>
    </div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="!learningPlan" class="empty-state">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
      </div>
      <p>You don't have a learning plan yet</p>
      <button class="btn-primary generate-btn" @click="generateLearningPlan" :disabled="generating">
        <span>{{ generating ? 'Generating...' : 'Generate Learning Plan' }}</span>
        <div v-if="generating" class="btn-spinner"></div>
      </button>
    </div>
    
    <div v-else class="learning-plan-content">
      <div class="plan-header">
        <h2>{{ learningPlan.title }}</h2>
        <div class="plan-status" :class="learningPlan.status">
          {{ learningPlan.status }}
        </div>
      </div>
      
      <div class="plan-description">
        {{ learningPlan.description }}
      </div>
      
      <div class="plan-progress">
        <div class="progress-label">
          <span>Overall Progress</span>
          <span>{{ learningPlan.overall_progress }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: learningPlan.overall_progress + '%' }"></div>
        </div>
      </div>
      
      <div class="plan-modules">
        <h3>Modules</h3>
        
        <div v-for="module in learningPlan.modules" :key="module.id" class="module-card" :class="module.status">
          <div class="module-header">
            <h4>{{ module.title }}</h4>
            <div class="module-status">{{ module.status }}</div>
          </div>
          
          <div class="module-description">{{ module.description }}</div>
          
          <div class="module-meta">
            <div class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>{{ module.estimated_hours }} hours</span>
            </div>
            
            <div class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h13l4-3.5L18 6z"></path>
                <path d="M12 13v9"></path>
                <path d="M12 2v4"></path>
              </svg>
              <span>{{ module.difficulty_level }}</span>
            </div>
          </div>
          
          <div class="module-actions">
            <button class="btn-primary" @click="startModule(module)" :disabled="module.status === 'completed'">
              <span>{{ getModuleButtonText(module) }}</span>
              <svg v-if="module.status !== 'completed'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LearningPlanComponent',
  data() {
    return {
      generating: false
    }
  },
  computed: {
    learningPlan() {
      return this.$store.getters['learningPlan/plan'];
    },
    loading() {
      return this.$store.getters['learningPlan/loading'];
    },
    error() {
      return this.$store.getters['learningPlan/error'];
    }
  },
  created() {
    this.fetchLearningPlan();
  },
  methods: {
    async fetchLearningPlan() {
      try {
        await this.$store.dispatch('learningPlan/fetchLearningPlan');
      } catch (error) {
        console.error('Error fetching learning plan:', error);
      }
    },
    
    async generateLearningPlan() {
      this.generating = true;
      try {
        await this.$store.dispatch('learningPlan/generateLearningPlan');
      } catch (error) {
        console.error('Error generating learning plan:', error);
      } finally {
        this.generating = false;
      }
    },
    
    async startModule(module) {
      try {
        await this.$store.dispatch('learningPlan/startModule', module.id);
        
        // Redirect based on module type
        const moduleType = module.module_type;
        if (moduleType === 'quiz') {
          this.$router.push(`/quizzes/${module.content_reference_id}`);
        } else if (moduleType === 'practice') {
          this.$router.push(`/skill-improvement/practice/${module.content_reference_id}`);
        } else if (moduleType === 'resource') {
          this.$router.push(`/resources/${module.content_reference_id}`);
        }
      } catch (error) {
        console.error('Error starting module:', error);
      }
    },
    
    getModuleButtonText(module) {
      if (module.status === 'not_started') {
        return 'Start';
      } else if (module.status === 'in_progress') {
        return 'Continue';
      } else {
        return 'Completed';
      }
    }
  }
}
</script>

<style scoped>

/* Include your existing loading, empty state, and button styles */
</style>
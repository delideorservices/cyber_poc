<template>
  <div class="quiz-details-container">
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Loading quiz...</span>
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-else class="quiz-content">
      <div class="quiz-header">
        <h1>{{ quiz.title }}</h1>
        <p class="quiz-description">{{ quiz.description }}</p>
      </div>
      
      <div class="info-card">
        <div class="info-item">
          <span class="info-label">Topic:</span> 
          <span class="info-value">{{ quiz.topic_name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Difficulty:</span> 
          <span class="difficulty-level">
            <span 
              v-for="n in 5" 
              :key="n" 
              :class="['difficulty-star', { active: n <= quiz.difficulty_level }]"
            >★</span>
          </span>
        </div>
      </div>
      
      <div class="action-buttons">
        <button @click="$router.push(`/quizzes/${quiz.id}/start`)" class="btn-primary">
          <span>Start Quiz</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"></path>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </button>
        <button @click="$router.push('/dashboard')" class="btn-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5"></path>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Back to Dashboard</span>
        </button>
      </div>
      
      <div class="chapters-section">
        <div class="section-header">
          <div class="section-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </div>
          <h2>Chapters</h2>
        </div>
        
        <div class="chapters-list">
          <div v-for="chapter in quiz.chapters" :key="chapter.id" class="chapter-card">
            <h3>{{ chapter.title }}</h3>
            <p class="chapter-description">{{ chapter.description }}</p>
            <div class="chapter-footer">
              <div class="chapter-stats">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>{{ chapter.questions.length }} questions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizDetails',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: '',
      quiz: null
    }
  },
  created() {
    this.fetchQuiz();
  },
  methods: {
    async fetchQuiz() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await this.$store.dispatch('quiz/fetchQuiz', this.id);
        this.quiz = response.data;
      } catch (error) {
        console.error('Error fetching quiz:', error);
        this.error = 'Failed to load quiz. Please try again.';
      } finally {
        this.loading = false;
      }
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
}

.quiz-details-container {
  font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 25px 20px;
  color: var(--text-color);
  background-color: var(--primary-bg);
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
  margin: 30px 0;
  padding: 20px;
  color: #d93025;
  background-color: #fce8e6;
  border-radius: var(--border-radius);
  text-align: center;
}

/* Quiz Content */
.quiz-header {
  margin-bottom: 25px;
}

.quiz-header h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 500;
  color: var(--text-color);
}

.quiz-description {
  margin: 0;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* Info Card */
.info-card {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 20px;
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  margin-bottom: 25px;
  border: 1px solid var(--border-color);
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: 500;
  margin-right: 8px;
  color: var(--text-secondary);
}

.info-value {
  font-weight: 400;
  color: var(--text-color);
}

.difficulty-level {
  display: inline-flex;
}

.difficulty-star {
  color: #e0e0e0;
  font-size: 18px;
}

.difficulty-star.active {
  color: #fbbc04;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
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

.btn-primary:active {
  transform: translateY(1px);
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--secondary-color);
  background-color: #f1f3f4;
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #e8eaed;
}

/* Chapters Section */
.chapters-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
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

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: var(--text-color);
}

.chapters-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.chapter-card {
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chapter-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chapter-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color);
}

.chapter-description {
  margin: 0 0 15px 0;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chapter-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.chapter-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.chapter-stats svg {
  color: var(--primary-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .chapters-list {
    grid-template-columns: 1fr;
  }
}
</style>
<template>
  <div class="dashboard-container">
    <!-- Main content area with two columns -->
    <div class="content-container">
      <!-- Left column: Start New Quiz -->
      <div class="quiz-card">
        <div class="card-header">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="16"></line>
              <line x1="8" y1="12" x2="16" y2="12"></line>
            </svg>
          </div>
          <h3>Start New Quiz</h3>
        </div>
        
        <div class="card-content">
          <div class="form-label">Select a topic</div>
          
          <div v-if="loadingTopics" class="loading-indicator">
            <div class="spinner"></div>
            <span>Loading topics...</span>
          </div>
          <div v-else-if="topicsError" class="error-message">{{ topicsError }}</div>
          <div v-else class="quiz-form">
            <div class="select-container">
              <select 
                v-model="selectedTopicId" 
                class="topic-select"
              >
                <option value="" disabled selected>Choose a topic</option>
                <option v-for="topic in topics" :key="topic.id" :value="topic.id">
                  {{ topic.name }}
                </option>
              </select>
            </div>
            
            <button 
              class="btn-primary" 
              @click="startQuiz" 
              :disabled="!selectedTopicId || generatingQuiz"
            >
              <span>{{ generatingQuiz ? 'Generating...' : 'Start Quiz' }}</span>
              <svg v-if="!generatingQuiz" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
              <div v-else class="btn-spinner"></div>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Right column: Your Quizzes -->
      <div class="quiz-card">
        <div class="card-header">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <h3>Your Quizzes</h3>
        </div>
        
        <div class="card-content">
          <div v-if="loadingQuizzes" class="loading-indicator">
            <div class="spinner"></div>
            <span>Loading quizzes...</span>
          </div>
          <div v-else-if="quizzesError" class="error-message">{{ quizzesError }}</div>
          <div v-else-if="!quizzesList || quizzesList.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <p>No quizzes found</p>
          </div>
          <div v-else class="quizzes-list">
            <div v-for="quiz in quizzesList" :key="quiz.id" class="quiz-item">
              <div class="quiz-info">
                <div class="quiz-topic">
                  Topic: {{ quiz.topic ? quiz.topic.name : (quiz.topic_name || 'General') }}
                </div>
              </div>
              <button class="btn-secondary" @click="$router.push(`/quizzes/${quiz.id}`)">
                <span>Continue</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      selectedTopicId: '',
      generatingQuiz: false,
      searchQuery: '',
      currentPage: 1,
      filteredQuizzes: []
    }
  },
  computed: {
    user() {
      return this.$store.getters['auth/user'];
    },
    topics() {
      return this.$store.getters['topic/topics'];
    },
    quizzes() {
      return this.$store.getters['quiz/quizzes'];
    },
    quizzesList() {
      // Handle both array and paginated object formats
      if (!this.quizzes) return [];
      
      // If filtered quizzes exist and have length, use them
      if (this.filteredQuizzes && this.filteredQuizzes.length > 0) {
        return this.filteredQuizzes;
      }
      
      // Check if quizzes is a paginated response
      if (this.quizzes.data) {
        return this.quizzes.data;
      }
      
      // If quizzes is a direct array
      if (Array.isArray(this.quizzes)) {
        return this.quizzes;
      }
      
      return [];
    },
    loadingTopics() {
      return this.$store.getters['topic/loading'];
    },
    loadingQuizzes() {
      return this.$store.getters['quiz/loading'];
    },
    topicsError() {
      return this.$store.getters['topic/error'];
    },
    quizzesError() {
      return this.$store.getters['quiz/error'];
    },
    totalPages() {
      if (this.quizzes && this.quizzes.last_page) {
        return this.quizzes.last_page;
      }
      return 1;
    }
  },
  created() {
    this.fetchTopics();
    this.fetchQuizzes();
  },
  methods: {
    async fetchTopics() {
      try {
        await this.$store.dispatch('topic/fetchTopics');
      } catch (error) {
        console.error('Error fetching topics:', error);
      }
    },
    
    async fetchQuizzes(page = 1) {
      try {
        this.currentPage = page;
        await this.$store.dispatch('quiz/fetchQuizzes', { page });
        this.searchQuizzes();
      } catch (error) {
        console.error('Error fetching quizzes:', error);
      }
    },
    
    searchQuizzes() {
      if (!this.quizzesList) {
        this.filteredQuizzes = [];
        return;
      }
      
      const query = this.searchQuery.toLowerCase().trim();
      if (!query) {
        this.filteredQuizzes = [...this.quizzesList];
        return;
      }
      
      this.filteredQuizzes = this.quizzesList.filter(quiz => {
        const topicName = quiz.topic ? quiz.topic.name : 
                         (quiz.topic_name ? quiz.topic_name : '');
        
        return quiz.title?.toLowerCase().includes(query) || 
               topicName.toLowerCase().includes(query);
      });
    },
    
    async startQuiz() {
      if (!this.selectedTopicId) return;
      
      this.generatingQuiz = true;
      try {
        const response = await this.$store.dispatch('quiz/generateQuiz', this.selectedTopicId);
        
        if (response.data && response.data.status === 'success') {
          this.$router.push(`/quizzes/${response.data.quiz_id}`);
        }
      } catch (error) {
        console.error('Error generating quiz:', error);
        alert('Failed to generate quiz. Please try again.');
      } finally {
        this.generatingQuiz = false;
      }
    }
  }
}
</script>

<style scoped>
/* Professional dark-themed design */
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

.dashboard-container {
  font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
  color: var(--text-color);
  background-color: var(--primary-bg);
}

/* Content layout */
.content-container {
  display: flex;
  gap: 30px;
  margin-top: 25px;
}

.quiz-card {
  flex: 1;
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* Card Headers */
.card-header {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid var(--border-color);
}

.card-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e8f0fe;
  margin-right: 12px;
}

.card-icon svg {
  color: var(--primary-color);
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color);
}

.card-content {
  padding: 20px;
}

/* Form Elements */
.form-label {
  font-size: 14px;
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-weight: 500;
}

.select-container {
  position: relative;
  margin-bottom: 20px;
}

.topic-select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  color: var(--text-color);
  background-color: var(--card-bg);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%235f6368' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
}

.topic-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
}

/* Buttons */
.btn-primary {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 16px;
  font-size: 14px;
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

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  background-color: var(--secondary-color);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--primary-color);
  background-color: #e8f0fe;
  border: none;
  border-radius: var(--border-radius);
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #d2e3fc;
}

/* Quiz List */
.quizzes-list {
  display: flex;
  flex-direction: column;
}

.quiz-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.quiz-item:last-child {
  border-bottom: none;
}

.quiz-info {
  display: flex;
  flex-direction: column;
}

.quiz-topic {
  font-size: 14px;
  color: var(--text-color);
  font-weight: 400;
}

/* Loading and Empty States */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  color: var(--text-secondary);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(26, 115, 232, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  margin: 20px 0;
  padding: 15px;
  color: #d93025;
  background-color: #fce8e6;
  border-radius: var(--border-radius);
  font-size: 14px;
  text-align: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-secondary);
}

.empty-icon {
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
  margin: 0;
  font-size: 14px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .content-container {
    flex-direction: column;
  }
  
  .quiz-card {
    margin-bottom: 20px;
  }
}
</style>
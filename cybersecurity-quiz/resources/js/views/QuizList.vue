<template>
    <div class="quiz-list container">
      <h1>My Quizzes</h1>
      
      <div v-if="loading" class="loader">
        Loading quizzes...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="quizzes.length === 0" class="empty-state">
        <p>You haven't taken any quizzes yet.</p>
        <router-link to="/dashboard" class="btn btn-primary">Start a Quiz</router-link>
      </div>
      
      <div v-else>
        <div class="quiz-status-tabs">
          <button 
            :class="['tab-btn', { active: currentStatus === 'all' }]"
            @click="setStatusFilter('all')"
          >
            All Quizzes
          </button>
          <button 
            :class="['tab-btn', { active: currentStatus === 'completed' }]"
            @click="setStatusFilter('completed')"
          >
            Completed
          </button>
          <button 
            :class="['tab-btn', { active: currentStatus === 'in_progress' }]"
            @click="setStatusFilter('in_progress')"
          >
            In Progress
          </button>
        </div>
        
        <div class="quiz-cards">
          <div 
            v-for="quiz in filteredQuizzes" 
            :key="quiz.id"
            class="quiz-card"
          >
            <div class="quiz-info">
              <h3>{{ quiz.title }}</h3>
              <p class="quiz-topic">{{ quiz.topic_name }}</p>
              <div class="quiz-meta">
                <span class="quiz-date">Created: {{ formatDate(quiz.created_at) }}</span>
                <span 
                  :class="['quiz-status', quiz.completed ? 'completed' : 'in-progress']"
                >
                  {{ quiz.completed ? 'Completed' : 'In Progress' }}
                </span>
              </div>
              <div v-if="quiz.completed" class="quiz-score">
                Score: <span :class="getScoreClass(quiz.score)">{{ Math.round(quiz.score) }}%</span>
              </div>
            </div>
            <div class="quiz-actions">
              <router-link 
                :to="quiz.completed ? `/results/${quiz.result_id}` : `/quizzes/${quiz.id}`" 
                class="btn btn-primary"
              >
                {{ quiz.completed ? 'View Results' : 'Continue Quiz' }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'QuizList',
    data() {
      return {
        loading: true,
        error: '',
        quizzes: [],
        currentStatus: 'all'
      }
    },
    computed: {
      filteredQuizzes() {
        if (this.currentStatus === 'all') {
          return this.quizzes;
        } else if (this.currentStatus === 'completed') {
          return this.quizzes.filter(quiz => quiz.completed);
        } else {
          return this.quizzes.filter(quiz => !quiz.completed);
        }
      }
    },
    created() {
      this.fetchQuizzes();
    },
    methods: {
      async fetchQuizzes() {
        this.loading = true;
        this.error = '';
        
        try {
          const response = await this.$store.dispatch('quiz/fetchQuizzes');
          this.quizzes = response.data;
        } catch (error) {
          console.error('Error fetching quizzes:', error);
          this.error = 'Failed to load quizzes. Please try again.';
        } finally {
          this.loading = false;
        }
      },
      
      setStatusFilter(status) {
        this.currentStatus = status;
      },
      
      formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      },
      
      getScoreClass(score) {
        if (score >= 90) return 'excellent';
        if (score >= 80) return 'good';
        if (score >= 70) return 'average';
        if (score >= 60) return 'fair';
        return 'poor';
      }
    }
  }
  </script>
  
  <style scoped>
  .quiz-list {
    padding: 2rem 0;
  }
  
  .loader, .error, .empty-state {
    text-align: center;
    padding: 2rem;
  }
  
  .error {
    color: #ef4444;
  }
  
  .quiz-status-tabs {
    display: flex;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
  }
  
  .tab-btn {
    padding: 0.75rem 1.25rem;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    font-weight: 500;
    color: #4b5563;
  }
  
  .tab-btn:hover {
    color: #111827;
  }
  
  .tab-btn.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }
  
  .quiz-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  
  .quiz-card {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .quiz-info {
    padding: 1.5rem;
    flex: 1;
  }
  
  .quiz-info h3 {
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
  }
  
  .quiz-topic {
    color: #4b5563;
    margin-bottom: 1rem;
  }
  
  .quiz-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }
  
  .quiz-date {
    color: #6b7280;
  }
  
  .quiz-status {
    font-weight: 600;
  }
  
  .quiz-status.completed {
    color: #10b981;
  }
  
  .quiz-status.in-progress {
    color: #f59e0b;
  }
  
  .quiz-score {
    font-size: 0.875rem;
    margin-top: 0.5rem;
  }
  
  .quiz-score .excellent {
    color: #10b981;
  }
  
  .quiz-score .good {
    color: #3b82f6;
  }
  
  .quiz-score .average {
    color: #f59e0b;
  }
  
  .quiz-score .fair {
    color: #f97316;
  }
  
  .quiz-score .poor {
    color: #ef4444;
  }
  
  .quiz-actions {
    padding: 1rem 1.5rem;
    background-color: #f9fafb;
    border-top: 1px solid #e5e7eb;
  }
  
  .quiz-actions .btn {
    width: 100%;
  }
  </style>
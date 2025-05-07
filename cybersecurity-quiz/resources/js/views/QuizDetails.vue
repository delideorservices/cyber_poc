<template>
    <div class="quiz-details container">
      <div v-if="loading" class="loader">
        Loading quiz...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else>
        <h1>{{ quiz.title }}</h1>
        <p class="quiz-description">{{ quiz.description }}</p>
        
        <div class="quiz-info">
          <div class="info-item">
            <span class="info-label">Topic:</span> {{ quiz.topic_name }}
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
        
        <div class="quiz-actions">
          <router-link :to="`/quizzes/${quiz.id}/start`" class="btn btn-primary">
            Start Quiz
          </router-link>
          <router-link to="/dashboard" class="btn btn-secondary">
            Back to Dashboard
          </router-link>
        </div>
        
        <div class="chapter-list">
          <h2>Chapters</h2>
          <div v-for="chapter in quiz.chapters" :key="chapter.id" class="chapter-card">
            <h3>{{ chapter.title }}</h3>
            <p>{{ chapter.description }}</p>
            <div class="chapter-stats">
              <span>{{ chapter.questions.length }} questions</span>
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
  .quiz-details {
    padding: 2rem 0;
  }
  
  .loader, .error {
    text-align: center;
    padding: 2rem;
  }
  
  .error {
    color: #ef4444;
  }
  
  .quiz-description {
    margin-bottom: 1.5rem;
    color: #4b5563;
  }
  
  .quiz-info {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: #f9fafb;
    border-radius: 0.5rem;
  }
  
  .info-item {
    display: flex;
    align-items: center;
  }
  
  .info-label {
    font-weight: 600;
    margin-right: 0.5rem;
  }
  
  .difficulty-level {
    display: inline-flex;
  }
  
  .difficulty-star {
    color: #d1d5db;
  }
  
  .difficulty-star.active {
    color: #f59e0b;
  }
  
  .quiz-actions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
  }
  
  .btn-secondary {
    color: #4b5563;
    background-color: white;
    border: 1px solid #d1d5db;
  }
  
  .btn-secondary:hover {
    background-color: #f9fafb;
  }
  
  .chapter-list {
    margin-top: 2rem;
  }
  
  .chapter-card {
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    background-color: white;
  }
  
  .chapter-stats {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
  }
  </style>
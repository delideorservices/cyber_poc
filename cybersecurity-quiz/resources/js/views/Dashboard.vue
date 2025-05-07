<template>
    <div class="dashboard container">
      <h1>Dashboard</h1>
      
      <div class="dashboard-content">
        <div class="welcome-message">
          <h2>Welcome, {{ user ? user.name : 'User' }}!</h2>
          <p>Select a topic to start a new quiz or continue with your existing quizzes.</p>
        </div>
        
        <div class="dashboard-sections">
          <div class="new-quiz-section">
            <h3>Start New Quiz</h3>
            <div v-if="loadingTopics" class="loading">Loading topics...</div>
            <div v-else-if="topicsError" class="error">{{ topicsError }}</div>
            <div v-else>
              <div class="form-group">
                <label for="topic" class="form-label">Select Topic</label>
                <select id="topic" v-model="selectedTopicId" class="form-control">
                  <option value="">Select a topic</option>
                  <option v-for="topic in topics" :key="topic.id" :value="topic.id">
                    {{ topic.name }}
                  </option>
                </select>
              </div>
              <button 
                class="btn btn-primary" 
                @click="startQuiz" 
                :disabled="!selectedTopicId || generatingQuiz"
              >
                {{ generatingQuiz ? 'Generating...' : 'Start Quiz' }}
              </button>
            </div>
          </div>
          
          <div class="recent-quizzes-section">
            <h3>Your Recent Quizzes</h3>
            <div v-if="loadingQuizzes" class="loading">Loading quizzes...</div>
            <div v-else-if="quizzesError" class="error">{{ quizzesError }}</div>
            <div v-else-if="quizzes.length === 0" class="empty-state">
              You haven't taken any quizzes yet.
            </div>
            <div v-else>
              <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-item">
                <h4>{{ quiz.title }}</h4>
                <p>Topic: {{ quiz.topic_name }}</p>
                <div class="quiz-actions">
                  <router-link :to="`/quizzes/${quiz.id}`" class="btn btn-primary">
                    {{ quiz.completed ? 'View Results' : 'Continue Quiz' }}
                  </router-link>
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
    name: 'Dashboard',
    data() {
      return {
        selectedTopicId: '',
        generatingQuiz: false,
        quizzesError: null,
        topicsError: null
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
        return this.$store.getters['quiz/quizzes'] || [];
      },
      loadingTopics() {
        return this.$store.getters['topic/loading'];
      },
      loadingQuizzes() {
        return this.$store.getters['quiz/loading'];
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
          this.topicsError = 'Failed to load topics';
        }
      },
      
      async fetchQuizzes() {
        try {
          await this.$store.dispatch('quiz/fetchQuizzes');
        } catch (error) {
          console.error('Error fetching quizzes:', error);
          this.quizzesError = 'Failed to load quizzes';
        }
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
  .dashboard {
    padding: 2rem 0;
  }
  
  .dashboard-content {
    margin-top: 1.5rem;
  }
  
  .welcome-message {
    margin-bottom: 2rem;
  }
  
  .dashboard-sections {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
  }
  
  .new-quiz-section, .recent-quizzes-section {
    flex: 1;
    min-width: 300px;
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  .form-control {
    display: block;
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    font-weight: 500;
    cursor: pointer;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
    border: none;
  }
  
  .btn-primary:hover {
    background-color: #2563eb;
  }
  
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .quiz-item {
    padding: 1rem 0;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .quiz-item:last-child {
    border-bottom: none;
  }
  
  .quiz-actions {
    margin-top: 0.5rem;
  }
  
  .loading, .error, .empty-state {
    padding: 1rem;
    text-align: center;
    color: #6b7280;
  }
  
  .error {
    color: #ef4444;
  }
  </style>
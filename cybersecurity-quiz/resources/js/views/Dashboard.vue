<template>
  <div class="dashboard-container">
    <!-- User greeting section -->
    <div class="user-greeting">
      <div class="avatar">
        <span>{{ getUserInitials() }}</span>
      </div>
      <div class="greeting-text">
        <h2>Welcome back, {{ user ? user.name : 'User' }}!</h2>
        <p>Ready to enhance your skills today?</p>
      </div>
    </div>
    
    <!-- Stats cards -->
    <!-- <div class="stats-container">
      <div class="stat-card">
        <div class="stat-icon total-icon"></div>
        <div class="stat-content">
          <div class="stat-label">Total Quizzes</div>
          <div class="stat-value">{{ totalQuizzesCount }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon completed-icon"></div>
        <div class="stat-content">
          <div class="stat-label">Completed</div>
          <div class="stat-value">{{ completedQuizzes }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon progress-icon"></div>
        <div class="stat-content">
          <div class="stat-label">In Progress</div>
          <div class="stat-value">{{ inProgressQuizzes }}</div>
        </div>
      </div>
    </div>
     -->
    <!-- Main content area with two columns -->
    <div class="content-container">
      <!-- Left column: Start New Quiz -->
      <div class="start-quiz-container">
        <h3>Start New Quiz</h3>
        
        <div v-if="loadingTopics" class="loading">Loading topics...</div>
        <div v-else-if="topicsError" class="error">{{ topicsError }}</div>
        <div v-else class="quiz-form">
          <div class="form-group">
            <label for="topic">Select a topic</label>
            <select 
              id="topic" 
              v-model="selectedTopicId" 
              class="form-select"
            >
              <option value="">Choose a topic</option>
              <option v-for="topic in topics" :key="topic.id" :value="topic.id">
                {{ topic.name }}
              </option>
            </select>
          </div>
          
          <button 
            class="btn-start-quiz" 
            @click="startQuiz" 
            :disabled="!selectedTopicId || generatingQuiz"
          >
            {{ generatingQuiz ? 'Generating...' : 'Start Quiz' }}
          </button>
        </div>
      </div>
      
      <!-- Right column: Your Quizzes -->
      <div class="your-quizzes-container">
        <div class="quizzes-header">
          <h3>Your Quizzes</h3>
          <div class="search-container">
            <input 
              type="text" 
              placeholder="Search quizzes..." 
              v-model="searchQuery"
              @input="searchQuizzes"
              class="search-input"
            >
          </div>
        </div>
        
        <div v-if="loadingQuizzes" class="loading">Loading quizzes...</div>
        <div v-else-if="quizzesError" class="error">{{ quizzesError }}</div>
        <div v-else-if="!quizzesList || quizzesList.length === 0" class="empty-state">
          <div class="empty-icon"></div>
          <h4>No quizzes found</h4>
          <p>You haven't taken any quizzes yet or no results match your search.</p>
        </div>
        <div v-else class="quizzes-list">
          <div v-for="quiz in quizzesList" :key="quiz.id" class="quiz-item">
            <h4>{{ quiz.title }}</h4>
            <p v-if="quiz.topic">Topic: {{ quiz.topic.name }}</p>
            <p v-else-if="quiz.topic_name">Topic: {{ quiz.topic_name }}</p>
            <div class="quiz-actions">
              <router-link :to="`/quizzes/${quiz.id}`" class="btn-continue">
                {{ quiz.completed ? 'View Results' : 'Continue Quiz' }}
              </router-link>
            </div>
          </div>
          
          <!-- Pagination -->
          <div class="pagination" v-if="totalPages > 1">
            <button 
              class="pagination-btn" 
              :disabled="currentPage === 1"
              @click="changePage(currentPage - 1)"
            >
              Previous
            </button>
            <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
            <button 
              class="pagination-btn" 
              :disabled="currentPage === totalPages"
              @click="changePage(currentPage + 1)"
            >
              Next
            </button>
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
      topicsError: null,
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
    totalQuizzesCount() {
      // Return the total if it's in a paginated response
      if (this.quizzes && this.quizzes.total) {
        return this.quizzes.total;
      }
      
      // Otherwise count the available quizzes
      return this.quizzesList ? this.quizzesList.length : 0;
    },
    loadingTopics() {
      return this.$store.getters['topic/loading'];
    },
    loadingQuizzes() {
      return this.$store.getters['quiz/loading'];
    },
    totalPages() {
      if (this.quizzes && this.quizzes.last_page) {
        return this.quizzes.last_page;
      }
      return 1;
    },
    completedQuizzes() {
      if (!this.quizzesList) return 0;
      return this.quizzesList.filter(quiz => quiz.completed).length;
    },
    inProgressQuizzes() {
      if (!this.quizzesList) return 0;
      return this.quizzesList.filter(quiz => !quiz.completed).length;
    }
  },
  created() {
    this.fetchTopics();
    this.fetchQuizzes();
  },
  methods: {
    getUserInitials() {
      if (!this.user || !this.user.name) return 'U';
      const names = this.user.name.split(' ');
      if (names.length >= 2) {
        return (names[0][0] + names[1][0]).toUpperCase();
      }
      return names[0].substr(0, 2).toUpperCase();
    },
    
    async fetchTopics() {
      try {
        this.topicsError = null;
        await this.$store.dispatch('topic/fetchTopics');
      } catch (error) {
        console.error('Error fetching topics:', error);
        this.topicsError = 'Failed to load topics';
      }
    },
    
    async fetchQuizzes(page = 1) {
      try {
        this.quizzesError = null;
        this.currentPage = page;
        await this.$store.dispatch('quiz/fetchQuizzes', { page });
        // Reset filtered quizzes when new quizzes are fetched
        this.searchQuizzes();
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        this.quizzesError = 'Failed to load quizzes';
      }
    },
    
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.fetchQuizzes(page);
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
        
        return quiz.title.toLowerCase().includes(query) || 
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
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* User greeting section */
.user-greeting {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #6753db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin-right: 20px;
}

.greeting-text h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #333;
}

.greeting-text p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

/* Stats cards */
.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  flex: 1;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  margin-right: 15px;
  background-position: center;
  background-repeat: no-repeat;
  background-size: 20px;
  background-color: #e9ecef;
}

.total-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%236753db' viewBox='0 0 16 16'%3E%3Cpath d='M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z'/%3E%3Cpath d='M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z'/%3E%3C/svg%3E");
}

.completed-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%236753db' viewBox='0 0 16 16'%3E%3Cpath d='M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z'/%3E%3C/svg%3E");
}

.progress-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%236753db' viewBox='0 0 16 16'%3E%3Cpath d='M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/%3E%3Cpath d='M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z'/%3E%3C/svg%3E");
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* Main content container */
.content-container {
  display: flex;
  gap: 30px;
}

.start-quiz-container {
  width: 35%;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.your-quizzes-container {
  width: 65%;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
}

/* Form elements */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #495057;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  color: #495057;
  background-color: #fff;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23495057' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
}

.form-select:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.btn-start-quiz {
  display: block;
  width: 100%;
  padding: 12px 0;
  background-color: #6753db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-start-quiz:hover {
  background-color: #5a46c7;
}

.btn-start-quiz:disabled {
  background-color: #b3b3b3;
  cursor: not-allowed;
}

/* Quizzes list */
.quizzes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  width: 250px;
}

.search-input:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.quizzes-list {
  max-height: 500px;
  overflow-y: auto;
}

.quiz-item {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
}

.quiz-item:last-child {
  border-bottom: none;
}

.quiz-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.quiz-item p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #6c757d;
}

.quiz-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-continue {
  padding: 8px 16px;
  background-color: #6753db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-continue:hover {
  background-color: #5a46c7;
}

/* Loading, error and empty states */
.loading, .error {
  padding: 20px;
  text-align: center;
  color: #6c757d;
}

.error {
  color: #dc3545;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #f8f9fa;
  margin-bottom: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%236c757d' viewBox='0 0 16 16'%3E%3Cpath d='M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/%3E%3Cpath d='M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z'/%3E%3C/svg%3E");
  background-position: center;
  background-repeat: no-repeat;
  background-size: 40px;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.empty-state p {
  margin: 0;
  color: #6c757d;
  max-width: 300px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.pagination-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  background-color: #fff;
  color: #6753db;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}

.pagination-btn:disabled {
  color: #6c757d;
  cursor: not-allowed;
}

.page-info {
  margin: 0 15px;
  font-size: 14px;
  color: #6c757d;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-container {
    flex-direction: column;
  }
  
  .content-container {
    flex-direction: column;
  }
  
  .start-quiz-container,
  .your-quizzes-container {
    width: 100%;
  }
  
  .quizzes-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-container {
    width: 100%;
    margin-top: 15px;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>
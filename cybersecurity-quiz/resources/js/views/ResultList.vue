<template>
    <div class="result-list container">
      <h1>Quiz Results</h1>
      
      <div v-if="loading" class="loader">
        Loading results...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="results.length === 0" class="empty-state">
        <p>You haven't completed any quizzes yet.</p>
        <router-link to="/dashboard" class="btn btn-primary">Start a Quiz</router-link>
      </div>
      
      <div v-else>
        <div class="performance-summary card">
          <h2>Performance Summary</h2>
          <div class="summary-stats">
            <div class="stat-card">
              <div class="stat-value">{{ results.length }}</div>
              <div class="stat-label">Quizzes Completed</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-value">{{ averageScore }}%</div>
              <div class="stat-label">Average Score</div>
            </div>
            
            <div class="stat-card">
              <div class="stat-value">{{ topSubject }}</div>
              <div class="stat-label">Strongest Topic</div>
            </div>
          </div>
        </div>
        
        <div class="results-table card">
          <h2>Your Results</h2>
          <table>
            <thead>
              <tr>
                <th>Quiz</th>
                <th>Topic</th>
                <th>Date</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in results" :key="result.id">
                <td>{{ result.quiz_title }}</td>
                <td>{{ result.topic_name }}</td>
                <td>{{ formatDate(result.completed_at) }}</td>
                <td>
                  <span :class="['score-pill', getScoreClass(result.percentage_score)]">
                    {{ Math.round(result.percentage_score) }}%
                  </span>
                </td>
                <td>
                  <router-link :to="`/results/${result.id}`" class="btn btn-sm btn-primary">
                    View Details
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="score-chart card" v-if="results.length > 1">
          <h2>Progress Over Time</h2>
          <div class="chart-container">
            <!-- Placeholder for chart - in a real implementation you'd use a charting library -->
            <div class="chart-placeholder">
              <div class="chart-bars">
                <div 
                  v-for="(result, index) in recentResults" 
                  :key="index"
                  class="chart-bar"
                  :style="{ height: `${result.percentage_score}%` }"
                  :class="getScoreClass(result.percentage_score)"
                >
                  <span class="bar-tooltip">{{ Math.round(result.percentage_score) }}%</span>
                </div>
              </div>
              <div class="chart-labels">
                <div 
                  v-for="(result, index) in recentResults" 
                  :key="index"
                  class="chart-label"
                >
                  {{ formatShortDate(result.completed_at) }}
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
    name: 'ResultList',
    data() {
      return {
        loading: true,
        error: '',
        results: []
      }
    },
    computed: {
      averageScore() {
        if (this.results.length === 0) return 0;
        
        const sum = this.results.reduce((total, result) => {
          return total + result.percentage_score;
        }, 0);
        
        return Math.round(sum / this.results.length);
      },
      
      topSubject() {
        if (this.results.length === 0) return 'N/A';
        
        // Group by topic name
        const topicScores = {};
        
        for (const result of this.results) {
          if (!topicScores[result.topic_name]) {
            topicScores[result.topic_name] = {
              count: 0,
              totalScore: 0
            };
          }
          
          topicScores[result.topic_name].count++;
          topicScores[result.topic_name].totalScore += result.percentage_score;
        }
        
        // Find topic with highest average score
        let topTopic = '';
        let highestAvg = 0;
        
        for (const topic in topicScores) {
          const avg = topicScores[topic].totalScore / topicScores[topic].count;
          
          if (avg > highestAvg) {
            highestAvg = avg;
            topTopic = topic;
          }
        }
        
        return topTopic || 'N/A';
      },
      
      recentResults() {
        // Get the most recent 5 results for the chart
        return [...this.results]
          .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
          .slice(0, 5)
          .reverse();
      }
    },
    created() {
      this.fetchResults();
    },
    methods: {
      async fetchResults() {
        this.loading = true;
        this.error = '';
        
        try {
          const response = await this.$store.dispatch('result/fetchResults');
          this.results = response.data;
        } catch (error) {
          console.error('Error fetching results:', error);
          this.error = 'Failed to load results. Please try again.';
        } finally {
          this.loading = false;
        }
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
      
      formatShortDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
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
  .result-list {
    padding: 2rem 0;
  }
  
  .loader, .error, .empty-state {
    text-align: center;
    padding: 2rem;
  }
  
  .error {
    color: #ef4444;
  }
  
  .card {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
  
  .summary-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-top: 1rem;
  }
  
  .stat-card {
    flex: 1;
    min-width: 140px;
    padding: 1rem;
    border-radius: 0.375rem;
    background-color: #f9fafb;
    text-align: center;
  }
  
  .stat-value {
    font-size: 1.875rem;
    font-weight: 700;
    color: #3b82f6;
    margin-bottom: 0.25rem;
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: #4b5563;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
  }
  
  th {
    font-weight: 600;
    color: #111827;
    background-color: #f9fafb;
  }
  
  .score-pill {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.875rem;
    color: white;
  }
  
  .score-pill.excellent {
    background-color: #10b981;
  }
  
  .score-pill.good {
    background-color: #3b82f6;
  }
  
  .score-pill.average {
    background-color: #f59e0b;
  }
  
  .score-pill.fair {
    background-color: #f97316;
  }
  
  .score-pill.poor {
    background-color: #ef4444;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }
  
  .chart-container {
    margin-top: 1.5rem;
    height: 250px;
  }
  
  .chart-placeholder {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .chart-bars {
    flex: 1;
    display: flex;
    justify-content: space-around;
    align-items: flex-end;
    padding: 0 1rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .chart-bar {
    width: 3rem;
    position: relative;
    border-radius: 0.25rem 0.25rem 0 0;
    transition: height 0.3s ease;
  }
  
  .chart-bar.excellent {
    background-color: #10b981;
  }
  
  .chart-bar.good {
    background-color: #3b82f6;
  }
  
  .chart-bar.average {
    background-color: #f59e0b;
  }
  
  .chart-bar.fair {
    background-color: #f97316;
  }
  
  .chart-bar.poor {
    background-color: #ef4444;
  }
  
  .bar-tooltip {
    position: absolute;
    top: -1.5rem;
    left: 50%;
    transform: translateX(-50%);
    background-color: #111827;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  
  .chart-bar:hover .bar-tooltip {
    opacity: 1;
  }
  
  .chart-labels {
    display: flex;
    justify-content: space-around;
    padding: 0.5rem 1rem 0;
  }
  
  .chart-label {
    width: 3rem;
    text-align: center;
    font-size: 0.75rem;
    color: #6b7280;
  }
  </style>
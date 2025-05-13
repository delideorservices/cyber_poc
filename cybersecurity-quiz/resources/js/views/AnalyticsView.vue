<template>
  <div class="analytics-page">
    <h1 class="page-title">Skills Analytics</h1>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <span>Loading your analytics...</span>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!hasAnalytics" class="empty-card">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      </div>
      <h2>No Analytics Available</h2>
      <p>Take some quizzes to generate skills analytics and track your progress</p>
      <button class="btn-primary" @click="$router.push('/')">Take a Quiz</button>
    </div>
    
    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Overview Section -->
      <div class="overview-section">
        <div class="overview-card">
          <div class="overview-header">
            <h3>Skills Overview</h3>
            <button class="btn-outline btn-sm" @click="downloadAnalytics">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Export
            </button>
          </div>
          <div class="overview-stats">
            <div class="stat-card">
              <div class="stat-value">{{ analytics.total_quizzes || 0 }}</div>
              <div class="stat-label">Quizzes Completed</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ analytics.avg_score || 0 }}%</div>
              <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ analytics.strengths ? analytics.strengths.length : 0 }}</div>
              <div class="stat-label">Strengths</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ analytics.weaknesses ? analytics.weaknesses.length : 0 }}</div>
              <div class="stat-label">Areas for Improvement</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Skill Proficiency Chart -->
      <div class="chart-section">
        <div class="chart-card">
          <h3>Skill Proficiency</h3>
          <div class="radar-chart-container">
            <canvas ref="radarChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Strengths and Improvement Areas -->
      <div class="skills-section">
        <div class="skills-card strengths">
          <h3>Your Strengths</h3>
          <div v-if="!strengths || strengths.length === 0" class="empty-skills">
            <p>No strengths identified yet. Keep taking quizzes!</p>
          </div>
          <div v-else class="skills-list">
            <div v-for="skill in strengths" :key="skill.id" class="skill-item">
              <div class="skill-info">
                <h4>{{ skill.name }}</h4>
                <div class="skill-score">
                  <div class="progress-bar">
                    <div class="progress-filled" :style="{ width: `${skill.score}%` }"></div>
                  </div>
                  <span class="score-value">{{ skill.score }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="skills-card improvements">
          <h3>Areas for Improvement</h3>
          <div v-if="!weaknesses || weaknesses.length === 0" class="empty-skills">
            <p>No improvement areas identified yet. Take more quizzes!</p>
          </div>
          <div v-else class="skills-list">
            <div v-for="skill in weaknesses" :key="skill.id" class="skill-item">
              <div class="skill-info">
                <h4>{{ skill.name }}</h4>
                <div class="skill-score">
                  <div class="progress-bar">
                    <div class="progress-filled" :style="{ width: `${skill.score}%` }"></div>
                  </div>
                  <span class="score-value">{{ skill.score }}%</span>
                </div>
              </div>
              <div class="skill-actions">
                <button class="btn-primary btn-sm" @click="practiceSkill(skill.id)">Practice</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Peer Comparison -->
      <div class="comparison-section">
        <div class="comparison-card">
          <h3>Peer Comparison</h3>
          <div v-if="!peerComparison" class="empty-comparison">
            <p>Not enough data for peer comparison yet.</p>
          </div>
          <div v-else>
            <div class="compare-header">
              <div class="percentile-display">
                <div class="percentile-value">{{ peerComparison.percentile }}th</div>
                <div class="percentile-label">Percentile</div>
              </div>
              <p class="compare-description">
                You're performing better than {{ peerComparison.percentile }}% of peers in your sector.
              </p>
            </div>
            <div class="comparison-chart-container">
              <canvas ref="comparisonChart"></canvas>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="activity-section">
        <div class="activity-card">
          <h3>Recent Quiz Activity</h3>
          <div v-if="!recentActivity || recentActivity.length === 0" class="empty-activity">
            <p>No recent quiz activity.</p>
          </div>
          <div v-else class="activity-list">
            <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
              <div class="activity-info">
                <div class="activity-title">{{ activity.quiz_title || 'Quiz' }}</div>
                <div class="activity-date">{{ formatDate(activity.created_at) }}</div>
              </div>
              <div class="activity-score">
                <span class="score-badge" :class="getScoreClass(activity.score)">
                  {{ activity.score }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
import Chart from 'chart.js/auto'

export default {
  name: 'AnalyticsView',
  data() {
    return {
      charts: {
        radar: null,
        comparison: null
      }
    }
  },
  computed: {
    ...mapGetters({
      analytics: 'analytics/analytics',
      strengths: 'analytics/strengths',
      weaknesses: 'analytics/weaknesses',
      peerComparison: 'analytics/peerComparison',
      recentActivity: 'analytics/recentActivity',
      loading: 'analytics/loading',
      error: 'analytics/error'
    }),
    hasAnalytics() {
      return this.analytics && Object.keys(this.analytics).length > 0
    }
  },
  mounted() {
    this.fetchAnalytics()
      .then(() => {
        if (this.hasAnalytics) {
          this.$nextTick(() => {
            this.initCharts()
          })
        }
      })
  },
  methods: {
    ...mapActions({
      fetchAnalytics: 'analytics/fetchAnalytics',
      exportAnalytics: 'analytics/exportAnalytics'
    }),
    initCharts() {
      this.initRadarChart()
      this.initComparisonChart()
    },
    initRadarChart() {
      if (!this.analytics || !this.analytics.skill_domains) return
      
      const ctx = this.$refs.radarChart.getContext('2d')
      
      // Extract data for radar chart
      const labels = this.analytics.skill_domains.map(domain => domain.name)
      const data = this.analytics.skill_domains.map(domain => domain.score)
      
      // Destroy existing chart if it exists
      if (this.charts.radar) {
        this.charts.radar.destroy()
      }
      
      // Create new radar chart
      this.charts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Your Proficiency',
            data: data,
            backgroundColor: 'rgba(26, 115, 232, 0.2)',
            borderColor: 'rgba(26, 115, 232, 1)',
            pointBackgroundColor: 'rgba(26, 115, 232, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(26, 115, 232, 1)',
            borderWidth: 2
          }]
        },
        options: {
          scales: {
            r: {
              angleLines: {
                display: true,
                color: 'rgba(0, 0, 0, 0.1)'
              },
              suggestedMin: 0,
              suggestedMax: 100,
              ticks: {
                stepSize: 20,
                backdropColor: 'transparent'
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          }
        }
      })
    },
    initComparisonChart() {
      if (!this.peerComparison || !this.peerComparison.domain_comparison) return
      
      const ctx = this.$refs.comparisonChart.getContext('2d')
      
      // Extract data for comparison chart
      const domains = this.peerComparison.domain_comparison
      const labels = domains.map(domain => domain.name)
      const userScores = domains.map(domain => domain.user_score)
      const peerScores = domains.map(domain => domain.peer_avg)
      
      // Destroy existing chart if it exists
      if (this.charts.comparison) {
        this.charts.comparison.destroy()
      }
      
      // Create new bar chart
      this.charts.comparison = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Your Score',
              data: userScores,
              backgroundColor: 'rgba(26, 115, 232, 0.7)',
              borderColor: 'rgba(26, 115, 232, 1)',
              borderWidth: 1
            },
            {
              label: 'Peer Average',
              data: peerScores,
              backgroundColor: 'rgba(95, 99, 104, 0.5)',
              borderColor: 'rgba(95, 99, 104, 1)',
              borderWidth: 1
            }
          ]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Score (%)'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Skill Domains'
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          }
        }
      })
    },
    practiceSkill(skillId) {
      this.$router.push(`/skill-improvement/practice/${skillId}`)
    },
    downloadAnalytics() {
      this.exportAnalytics()
        .then(response => {
          // Create a blob link to download the CSV
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', 'analytics_export.csv')
          document.body.appendChild(link)
          link.click()
          link.remove()
        })
        .catch(error => {
          console.error('Error exporting analytics:', error)
        })
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },
    getScoreClass(score) {
      if (score >= 80) return 'excellent'
      if (score >= 60) return 'good'
      if (score >= 40) return 'average'
      return 'needs-improvement'
    }
  }
}
</script>
<style scoped>
.analytics-page {
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

/* Loading and Empty States */
.loading-card, .empty-card {
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

/* Overview Section */
.analytics-content > div {
  margin-bottom: 30px;
}

.overview-card, .chart-card, .skills-card, .comparison-card, .activity-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header h3, .chart-card h3, .skills-card h3, .comparison-card h3, .activity-card h3 {
  font-size: 18px;
  margin: 0;
  font-weight: 500;
  color: #333;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-card {
  padding: 16px;
  border-radius: 8px;
  background-color: #f8f9fa;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 500;
  color: #1a73e8;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #5f6368;
}

/* Chart Sections */
.radar-chart-container, .comparison-chart-container {
  height: 300px;
  position: relative;
}

/* Skills Section */
.skills-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.skills-card h3 {
  margin-bottom: 20px;
}

.empty-skills {
  padding: 20px;
  text-align: center;
  color: #5f6368;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #f1f3f4;
}

.skill-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.skill-info {
  flex: 1;
}

.skill-info h4 {
  font-size: 14px;
  margin: 0 0 8px;
  font-weight: 500;
  color: #333;
}

.skill-score {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #f1f3f4;
  border-radius: 4px;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.strengths .progress-filled {
  background-color: #34a853;
}

.improvements .progress-filled {
  background-color: #fbbc04;
}

.score-value {
  font-size: 14px;
  font-weight: 500;
  color: #5f6368;
  min-width: 40px;
  text-align: right;
}

.skill-actions {
  margin-left: 10px;
}

/* Peer Comparison */
.compare-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.percentile-display {
  background-color: #e8f0fe;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  margin-right: 20px;
}

.percentile-value {
  font-size: 24px;
  font-weight: 500;
  color: #1a73e8;
}

.percentile-label {
  font-size: 12px;
  color: #5f6368;
}

.compare-description {
  margin: 0;
  color: #5f6368;
}

.empty-comparison {
  padding: 30px;
  text-align: center;
  color: #5f6368;
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Activity Section */
.activity-list {
  display: flex;
  flex-direction: column;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f1f3f4;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.activity-date {
  font-size: 12px;
  color: #5f6368;
}

.score-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.score-badge.excellent {
  background-color: #e6f4ea;
  color: #34a853;
}

.score-badge.good {
  background-color: #e8f0fe;
  color: #1a73e8;
}

.score-badge.average {
  background-color: #fef7e0;
  color: #f9ab00;
}

.score-badge.needs-improvement {
  background-color: #fce8e6;
  color: #ea4335;
}

.empty-activity {
  padding: 20px;
  text-align: center;
  color: #5f6368;
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Buttons */
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

.btn-outline {
  background-color: transparent;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  border-radius: 4px;
  padding: 9px 15px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-outline:hover {
  background-color: rgba(26, 115, 232, 0.04);
}

.btn-outline svg {
  color: #1a73e8;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .skills-section {
    grid-template-columns: 1fr;
  }
  
  .compare-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .percentile-display {
    margin-bottom: 15px;
    margin-right: 0;
  }
}
</style>
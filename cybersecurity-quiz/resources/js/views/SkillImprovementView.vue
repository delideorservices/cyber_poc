<template>
  <div class="skill-improvement-page">
    <h1 class="page-title">Skill Improvement</h1>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <span>Loading skill improvement data...</span>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!hasSkills" class="empty-card">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20v-6M6 20V10M18 20V4"></path>
        </svg>
      </div>
      <h2>No Skills to Improve</h2>
      <p>Take quizzes to identify skill gaps and access personalized improvement activities</p>
      <button class="btn-primary" @click="$router.push('/')">Take a Quiz</button>
    </div>
    
    <!-- Skills Content -->
    <div v-else class="skills-content">
      <!-- Improvement Needed Skills -->
      <div class="skills-section">
        <h2 class="section-title">Skills to Improve</h2>
        <div class="skills-grid">
          <div v-for="skill in improvementSkills" :key="skill.id" class="skill-card">
            <div class="skill-header">
              <h3>{{ skill.name }}</h3>
              <div class="proficiency-badge" :class="getProficiencyClass(skill.proficiency)">
                {{ getProficiencyLabel(skill.proficiency) }}
              </div>
            </div>
            <div class="skill-progress">
              <div class="progress-bar">
                <div class="progress-filled" :style="{ width: `${skill.proficiency}%` }"></div>
              </div>
              <span class="progress-percentage">{{ skill.proficiency }}%</span>
            </div>
            <p class="skill-description">{{ skill.description || 'Improve your knowledge in this skill area.' }}</p>
            <div class="gap-info">
              <div class="gap-label">Identified Gaps:</div>
              <ul class="gap-list">
                <li v-for="(gap, index) in skill.gaps" :key="index">{{ gap }}</li>
              </ul>
            </div>
            <div class="skill-actions">
              <button class="btn-primary" @click="startPractice(skill.id)">
                Practice Skill
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Spaced Repetition Section -->
      <div class="repetition-section">
        <h2 class="section-title">Due for Review</h2>
        
        <div v-if="dueReviews.length === 0" class="empty-reviews">
          <p>No reviews due at this time. Check back later!</p>
        </div>
        
        <div v-else class="reviews-list">
          <div v-for="review in dueReviews" :key="review.id" class="review-card">
            <div class="review-info">
              <div class="review-skill">{{ review.skill.name }}</div>
              <div class="review-meta">
                <span>Last reviewed: {{ formatDate(review.last_review_date) }}</span>
                <span class="review-count">Repetition: {{ review.repetition_number }}</span>
              </div>
            </div>
            <div class="review-actions">
              <button class="btn-primary" @click="startReview(review.id)">
                Start Review
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Practice History -->
      <div class="history-section">
        <h2 class="section-title">Practice History</h2>
        
        <div v-if="practiceHistory.length === 0" class="empty-history">
          <p>No practice sessions found. Start practicing to build your history!</p>
        </div>
        
        <div v-else class="history-list">
          <div v-for="session in practiceHistory" :key="session.id" class="history-card">
            <div class="history-info">
              <div class="history-skill">{{ session.skill.name }}</div>
              <div class="history-meta">
                <div class="meta-date">{{ formatDate(session.created_at) }}</div>
                <div class="meta-score" :class="getScoreClass(session.score)">
                  {{ session.score }}%
                </div>
              </div>
              <div class="history-detail">
                <div>Questions: {{ session.total_questions }}</div>
                <div>Correct: {{ session.correct_answers }}</div>
              </div>
            </div>
            <div class="history-actions">
              <button class="btn-secondary" @click="viewSessionDetails(session.id)">
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'SkillImprovementView',
  computed: {
    ...mapGetters({
      skills: 'skillImprovement/skills',
      dueReviews: 'skillImprovement/dueReviews',
      practiceHistory: 'skillImprovement/practiceHistory',
      loading: 'skillImprovement/loading',
      error: 'skillImprovement/error'
    }),
    hasSkills() {
      return this.skills && this.skills.length > 0
    },
    improvementSkills() {
      if (!this.skills) return []
      return this.skills.filter(skill => skill.needs_improvement)
    }
  },
  created() {
    this.fetchSkillData()
    this.fetchDueReviews()
    this.fetchPracticeHistory()
  },
  methods: {
    ...mapActions({
      fetchSkillData: 'skillImprovement/fetchSkillData',
      fetchDueReviews: 'skillImprovement/fetchDueReviews',
      fetchPracticeHistory: 'skillImprovement/fetchPracticeHistory'
    }),
    startPractice(skillId) {
      this.$router.push(`/skill-improvement/practice/${skillId}`)
    },
    startReview(reviewId) {
      this.$router.push(`/skill-improvement/review/${reviewId}`)
    },
    viewSessionDetails(sessionId) {
      this.$router.push(`/skill-improvement/session/${sessionId}`)
    },
    getProficiencyClass(score) {
      if (score >= 80) return 'expert'
      if (score >= 60) return 'proficient'
      if (score >= 40) return 'developing'
      return 'beginner'
    },
    getProficiencyLabel(score) {
      if (score >= 80) return 'Expert'
      if (score >= 60) return 'Proficient'
      if (score >= 40) return 'Developing'
      return 'Beginner'
    },
    getScoreClass(score) {
      if (score >= 80) return 'excellent'
      if (score >= 60) return 'good'
      if (score >= 40) return 'average'
      return 'needs-improvement'
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    }
  }
}
</script>
<style scoped>
.skill-improvement-page {
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

/* Section Headers */
.section-title {
  font-size: 20px;
  font-weight: 500;
  margin: 30px 0 20px;
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

.empty-reviews, .empty-history {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #5f6368;
}

/* Skills Grid */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.skill-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.skill-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.skill-header h3 {
  font-size: 18px;
  margin: 0;
  font-weight: 500;
  color: #333;
}

.proficiency-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.proficiency-badge.expert {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.proficiency-badge.proficient {
  background-color: #e3f2fd;
  color: #1565c0;
}

.proficiency-badge.developing {
  background-color: #fff3e0;
  color: #e65100;
}

.proficiency-badge.beginner {
  background-color: #ffebee;
  color: #c62828;
}

.skill-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
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
  background-color: #1a73e8;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-percentage {
  font-size: 14px;
  font-weight: 500;
  color: #5f6368;
}

.skill-description {
  margin-bottom: 15px;
  color: #5f6368;
  font-size: 14px;
}

.gap-info {
  margin-bottom: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.gap-label {
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.gap-list {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  color: #5f6368;
}

.gap-list li {
  margin-bottom: 4px;
}

.skill-actions {
  display: flex;
  justify-content: center;
}

/* Spaced Repetition Section */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 15px 20px;
}

.review-skill {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
  color: #5f6368;
}

.review-count {
  display: inline-block;
  padding: 2px 8px;
  background-color: #f1f3f4;
  border-radius: 12px;
  font-size: 12px;
}

/* Practice History Section */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 15px 20px;
}

.history-skill {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.meta-date {
  font-size: 14px;
  color: #5f6368;
}

.meta-score {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 14px;
}

.meta-score.excellent {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.meta-score.good {
  background-color: #e3f2fd;
  color: #1565c0;
}

.meta-score.average {
  background-color: #fff3e0;
  color: #e65100;
}

.meta-score.needs-improvement {
  background-color: #ffebee;
  color: #c62828;
}

.history-detail {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #5f6368;
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

.btn-secondary {
  background-color: #f1f3f4;
  color: #5f6368;
  border: none;
  border-radius: 4px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #e8eaed;
}

@media (max-width: 768px) {
  .skills-grid {
    grid-template-columns: 1fr;
  }
  
  .review-card, .history-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .review-actions, .history-actions {
    margin-top: 15px;
    align-self: flex-end;
  }
  
  .history-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>
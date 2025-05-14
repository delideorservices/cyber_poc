<template>
  <div class="recommendations-page">
    <h1 class="page-title">Learning Recommendations</h1>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <span>Finding personalized recommendations for you...</span>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!hasRecommendations" class="empty-card">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19.39 6.57A10 10 0 1 0 12 22a10 10 0 0 0 8.9-5.5"></path>
          <circle cx="12" cy="8" r="1"></circle>
          <path d="M8.5 14h7"></path>
        </svg>
      </div>
      <h2>No Recommendations Yet</h2>
      <p>Generate personalized learning recommendations based on your quiz results and skills</p>
      <button class="btn-primary" @click="generateRecommendations" :disabled="generating">
        {{ generating ? 'Generating...' : 'Generate Recommendations' }}
      </button>
    </div>
    
    <!-- Recommendations Content -->
    <div v-else class="recommendations-content">
      <div class="filter-section">
        <div class="filter-header">
          <h3>Filter Recommendations</h3>
          <button class="btn-outline btn-sm" @click="generateRecommendations" :disabled="generating">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            {{ generating ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
        
        <div class="filter-controls">
          <div class="filter-group">
            <label for="resourceType">Resource Type</label>
            <select id="resourceType" v-model="selectedType" @change="filterRecommendations">
              <option value="">All Types</option>
              <option v-for="type in resourceTypes" :key="type" :value="type">
                {{ formatResourceType(type) }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="difficultyLevel">Difficulty Level</label>
            <select id="difficultyLevel" v-model="selectedDifficulty" @change="filterRecommendations">
              <option value="">All Levels</option>
              <option value="1">Beginner (1)</option>
              <option value="2">Easy (2)</option>
              <option value="3">Intermediate (3)</option>
              <option value="4">Advanced (4)</option>
              <option value="5">Expert (5)</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="recommendations-list">
        <div v-for="recommendation in filteredRecommendations" 
             :key="recommendation.id" 
             class="recommendation-card"
             :class="recommendation.resource_type">
          
          <div class="card-header">
            <div class="card-type" :class="recommendation.resource_type">
              <svg v-if="recommendation.resource_type === 'video'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <svg v-else-if="recommendation.resource_type === 'article'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              <svg v-else-if="recommendation.resource_type === 'course'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <svg v-else-if="recommendation.resource_type === 'interactive'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 3 21 3 21 9"></polyline>
                <polyline points="9 21 3 21 3 15"></polyline>
                <line x1="21" y1="3" x2="14" y2="10"></line>
                <line x1="3" y1="21" x2="10" y2="14"></line>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              {{ formatResourceType(recommendation.resource_type) }}
            </div>
            
            <div class="difficulty-badge" :class="getDifficultyClass(recommendation.difficulty_level)">
              {{ formatDifficulty(recommendation.difficulty_level) }}
            </div>
          </div>
          
          <h3 class="card-title">{{ recommendation.title }}</h3>
          <p class="card-description">{{ recommendation.description }}</p>
          
          <div class="card-meta">
            <div class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>{{ recommendation.estimated_minutes }} minutes</span>
            </div>
            
            <div class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>{{ recommendation.primary_skill || 'General' }}</span>
            </div>
            
            <div class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              <span>{{ recommendation.relevance_score || 5 }} / 10</span>
            </div>
          </div>
          
          <div class="learning-match" v-if="recommendation.learning_style_match">
            <div class="match-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <span>{{ recommendation.learning_style_match }}</span>
          </div>
          
          <div class="card-actions">
            <a :href="recommendation.url" target="_blank" rel="noopener noreferrer" 
               class="btn-primary" @click="viewRecommendation(recommendation)">
              View Resource
            </a>
            
            <button v-if="recommendation.status !== 'saved'" 
                    class="btn-outline" 
                    @click="saveRecommendation(recommendation)">
              Save For Later
            </button>
            
            <button v-else
                    class="btn-outline btn-saved" 
                    @click="removeSavedRecommendation(recommendation)">
              Remove from Saved
            </button>
          </div>
          
          <div v-if="recommendation.status === 'viewed' || recommendation.status === 'completed'" 
               class="feedback-section">
            <h4>How was this resource?</h4>
            <div class="rating">
              <span class="star" 
                    v-for="i in 5" 
                    :key="i" 
                    :class="{ 'active': recommendation.feedback && recommendation.feedback.rating >= i }"
                    @click="rateRecommendation(recommendation, i)">
                ★
              </span>
            </div>
            
            <button class="btn-sm btn-outline" 
                    @click="completeRecommendation(recommendation)" 
                    :disabled="!recommendation.feedback || !recommendation.feedback.rating">
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
      
      <div class="saved-recommendations" v-if="savedRecommendations.length > 0">
        <h2 class="section-title">Saved for Later</h2>
        
        <div class="saved-list">
          <div v-for="recommendation in savedRecommendations" 
               :key="recommendation.id" 
               class="saved-card">
            <div class="card-type" :class="recommendation.resource_type">
              {{ formatResourceType(recommendation.resource_type) }}
            </div>
            
            <h3 class="card-title">{{ recommendation.title }}</h3>
            
            <div class="card-actions">
              <a :href="recommendation.url" target="_blank" rel="noopener noreferrer" 
                 class="btn-sm btn-primary" @click="viewRecommendation(recommendation)">
                View
              </a>
              
              <button class="btn-sm btn-outline" 
                      @click="removeSavedRecommendation(recommendation)">
                Remove
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
  name: 'RecommendationsView',
  data() {
    return {
      selectedType: '',
      selectedDifficulty: '',
      generating: false
    }
  },
  computed: {
    ...mapGetters({
      recommendations: 'recommendations/recommendations',
      savedRecommendations: 'recommendations/savedRecommendations',
      resourceTypes: 'recommendations/resourceTypes',
      loading: 'recommendations/loading',
      error: 'recommendations/error'
    }),
    hasRecommendations() {
      return this.recommendations && this.recommendations.length > 0
    },
    filteredRecommendations() {
      if (!this.recommendations) return []
      
      return this.recommendations.filter(rec => {
        // Filter by resource type
        if (this.selectedType && rec.resource_type !== this.selectedType) {
          return false
        }
        
        // Filter by difficulty level
        if (this.selectedDifficulty && rec.difficulty_level != this.selectedDifficulty) {
          return false
        }
        
        return true
      })
    }
  },
  created() {
    this.fetchRecommendations()
    this.fetchSavedRecommendations()
  },
  methods: {
    ...mapActions({
      fetchRecommendationsAction: 'recommendations/fetchRecommendations',
      fetchSavedRecommendationsAction: 'recommendations/fetchSavedRecommendations',
      generateRecommendationsAction: 'recommendations/generateRecommendations',
      viewRecommendationAction: 'recommendations/viewRecommendation',
      saveRecommendationAction: 'recommendations/saveRecommendation',
      removeSavedRecommendationAction: 'recommendations/removeSavedRecommendation',
      completeRecommendationAction: 'recommendations/completeRecommendation',
      provideFeedbackAction: 'recommendations/provideFeedback'
    }),
    async fetchRecommendations() {
      try {
        await this.fetchRecommendationsAction()
      } catch (error) {
        console.error('Error fetching recommendations:', error)
      }
    },
    async fetchSavedRecommendations() {
      try {
        await this.fetchSavedRecommendationsAction()
      } catch (error) {
        console.error('Error fetching saved recommendations:', error)
      }
    },
    async generateRecommendations() {
      this.generating = true
      try {
        await this.generateRecommendationsAction({
          type: this.selectedType,
          difficulty: this.selectedDifficulty
        })
      } catch (error) {
        console.error('Error generating recommendations:', error)
      } finally {
        this.generating = false
      }
    },
    filterRecommendations() {
      // The filtering is done via computed properties
      // This method is here for any future needs
    },
    async viewRecommendation(recommendation) {
      try {
        await this.viewRecommendationAction(recommendation.id)
      } catch (error) {
        console.error('Error marking recommendation as viewed:', error)
      }
    },
    async saveRecommendation(recommendation) {
      try {
        await this.saveRecommendationAction(recommendation.id)
        
        // Refresh recommendations and saved lists
        this.fetchRecommendations()
        this.fetchSavedRecommendations()
      } catch (error) {
        console.error('Error saving recommendation:', error)
      }
    },
    async removeSavedRecommendation(recommendation) {
      try {
        await this.removeSavedRecommendationAction(recommendation.id)
        
        // Refresh saved recommendations list
        this.fetchSavedRecommendations()
        
        // Also refresh main recommendations if removing from saved view
        if (recommendation.status === 'saved') {
          this.fetchRecommendations()
        }
      } catch (error) {
        console.error('Error removing saved recommendation:', error)
      }
    },
    async rateRecommendation(recommendation, rating) {
      try {
        if (!recommendation.feedback) {
          recommendation.feedback = {}
        }
        recommendation.feedback.rating = rating
        
        await this.provideFeedbackAction({
          id: recommendation.id,
          rating: rating
        })
      } catch (error) {
        console.error('Error rating recommendation:', error)
      }
    },
    async completeRecommendation(recommendation) {
      try {
        if (!recommendation.feedback || !recommendation.feedback.rating) {
          // Require rating before completion
          return
        }
        
        await this.completeRecommendationAction({
          id: recommendation.id,
          rating: recommendation.feedback.rating,
          feedback: recommendation.feedback.text || ''
        })
        
        // Refresh recommendations
        this.fetchRecommendations()
      } catch (error) {
        console.error('Error completing recommendation:', error)
      }
    },
    formatResourceType(type) {
      if (!type) return 'Unknown'
      
      const types = {
        'article': 'Article',
        'video': 'Video',
        'course': 'Course',
        'interactive': 'Interactive',
        'book': 'Book',
        'tool': 'Tool'
      }
      
      return types[type] || type.charAt(0).toUpperCase() + type.slice(1)
    },
    formatDifficulty(level) {
      const levels = {
        1: 'Beginner',
        2: 'Easy',
        3: 'Intermediate',
        4: 'Advanced',
        5: 'Expert'
      }
      
      return levels[level] || `Level ${level}`
    },
    getDifficultyClass(level) {
      if (level <= 2) return 'beginner'
      if (level === 3) return 'intermediate'
      return 'advanced'
    }
  }
}
</script>

<style scoped>
.recommendations-page {
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

/* Filter Section */
.filter-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-header h3 {
  font-size: 18px;
  margin: 0;
  font-weight: 500;
  color: #333;
}

.filter-controls {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 200px;
}

.filter-group label {
  font-size: 14px;
  margin-bottom: 6px;
  color: #5f6368;
}

.filter-group select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dadce0;
  font-size: 14px;
  color: #333;
  background-color: white;
}

/* Recommendations List */
.recommendations-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.recommendation-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, a0, 0, 0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  border-top: 4px solid #dadce0;
  position: relative;
  overflow: hidden;
}

.recommendation-card.article {
  border-top-color: #4285f4;
}

.recommendation-card.video {
  border-top-color: #ea4335;
}

.recommendation-card.course {
  border-top-color: #fbbc05;
}

.recommendation-card.interactive {
  border-top-color: #34a853;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-type {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  background-color: #f1f3f4;
  color: #5f6368;
}

.card-type.article {
  background-color: #e8f0fe;
  color: #4285f4;
}

.card-type.video {
  background-color: #fce8e6;
  color: #ea4335;
}

.card-type.course {
  background-color: #fef7e0;
  color: #fbbc05;
}

.card-type.interactive {
  background-color: #e6f4ea;
  color: #34a853;
}

.card-type svg {
  color: currentColor;
}

.difficulty-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
}

.difficulty-badge.beginner {
  background-color: #e6f4ea;
  color: #34a853;
}

.difficulty-badge.intermediate {
  background-color: #fef7e0;
  color: #f9ab00;
}

.difficulty-badge.advanced {
  background-color: #fce8e6;
  color: #ea4335;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
  margin: 0 0 10px;
  color: #333;
}

.card-description {
  font-size: 14px;
  color: #5f6368;
  margin: 0 0 16px;
  flex-grow: 1;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5f6368;
}

.meta-item svg {
  color: #5f6368;
}

.learning-match {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #188038;
}

.match-icon {
  display: flex;
  align-items: center;
  color: #188038;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.feedback-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #f1f3f4;
}

.feedback-section h4 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 10px;
  color: #333;
}

.rating {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
}

.star {
  font-size: 24px;
  color: #dadce0;
  cursor: pointer;
  user-select: none;
}

.star:hover, .star.active {
  color: #fbbc05;
}

/* Saved Recommendations */
.saved-recommendations {
  margin-top: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #333;
}

.saved-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.saved-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  padding: 15px;
  border-left: 3px solid #dadce0;
}

.saved-card .card-title {
  font-size: 16px;
  margin-bottom: 15px;
}

.saved-card .card-actions {
  margin-top: 10px;
}

/* Buttons */
.btn-primary {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary:hover {
  background-color: #1765cc;
}

.btn-primary:disabled {
  background-color: #dadce0;
  color: #5f6368;
  cursor: not-allowed;
}

.btn-outline {
  background-color: transparent;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-outline:hover {
  background-color: rgba(26, 115, 232, 0.04);
}

.btn-outline:disabled {
  border-color: #dadce0;
  color: #5f6368;
  cursor: not-allowed;
}

.btn-outline.btn-saved {
  color: #188038;
  border-color: #188038;
}

.btn-outline.btn-saved:hover {
  background-color: rgba(24, 128, 56, 0.04);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .recommendations-list, .saved-list {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .btn-primary, .btn-outline {
    width: 100%;
    text-align: center;
    justify-content: center;
  }
}
</style>

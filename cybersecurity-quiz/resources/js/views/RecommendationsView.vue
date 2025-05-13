<template>
  <div class="recommendations-page">
    <div class="page-header">
      <h1 class="page-title">Personalized Recommendations</h1>
      <p class="page-description">
        Based on your skill analysis and learning progress, we've curated these resources to help you improve.
      </p>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Loading your personalized recommendations...</span>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <h3>We encountered an error</h3>
      <p>{{ error }}</p>
      <button class="btn-primary" @click="fetchRecommendations">Try Again</button>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!hasRecommendations" class="empty-container">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
      </div>
      <h2>No Recommendations Yet</h2>
      <p>Complete more quizzes and activities to receive personalized resource recommendations</p>
      <button class="btn-primary" @click="generateRecommendations" :disabled="generating">
        {{ generating ? 'Generating...' : 'Generate Recommendations' }}
        <div v-if="generating" class="btn-spinner"></div>
      </button>
    </div>
    
    <!-- Content State -->
    <div v-else class="recommendations-content">
      <!-- Filter Controls -->
      <div class="filter-controls">
        <div class="filter-section">
          <h3>Filter by Type</h3>
          <div class="filter-buttons">
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'all' }"
              @click="setFilter('all')">
              All Types
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'article' }"
              @click="setFilter('article')">
              Articles
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'video' }"
              @click="setFilter('video')">
              Videos
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'course' }"
              @click="setFilter('course')">
              Courses
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'tool' }"
              @click="setFilter('tool')">
              Tools
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: activeFilter === 'reference' }"
              @click="setFilter('reference')">
              References
            </button>
          </div>
        </div>
        
        <div class="filter-section">
          <h3>Filter by Skill</h3>
          <div class="skill-filter">
            <select v-model="selectedSkill" class="skill-select">
              <option value="">All Skills</option>
              <option v-for="skill in skillsList" :key="skill.id" :value="skill.id">
                {{ skill.name }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="filter-section">
          <h3>Filter by Status</h3>
          <div class="filter-buttons">
            <button 
              class="filter-btn" 
              :class="{ active: statusFilter === 'all' }"
              @click="setStatusFilter('all')">
              All
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: statusFilter === 'new' }"
              @click="setStatusFilter('new')">
              New
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: statusFilter === 'viewed' }"
              @click="setStatusFilter('viewed')">
              Viewed
            </button>
            <button 
              class="filter-btn" 
              :class="{ active: statusFilter === 'completed' }"
              @click="setStatusFilter('completed')">
              Completed
            </button>
          </div>
        </div>
        
        <div class="search-section">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search recommendations..."
            class="search-input" 
            @input="debounceSearch"
          />
        </div>
      </div>
      
      <!-- Recommendations Count -->
      <div class="results-info">
        <p>Showing {{ filteredRecommendations.length }} recommendation{{ filteredRecommendations.length !== 1 ? 's' : '' }}</p>
        <button v-if="hasFilters" class="clear-filters-btn" @click="clearFilters">
          Clear Filters
        </button>
      </div>
      
      <!-- Filtered Empty State -->
      <div v-if="recommendationsLoaded && filteredRecommendations.length === 0" class="filtered-empty">
        <h3>No recommendations match your filters</h3>
        <p>Try adjusting your filter criteria to see more recommendations</p>
        <button class="btn-primary" @click="clearFilters">Clear All Filters</button>
      </div>
      
      <!-- Recommendations List -->
      <div v-else class="recommendations-list">
        <div 
          v-for="recommendation in filteredRecommendations" 
          :key="recommendation.id" 
          class="recommendation-card"
          :class="[recommendation.resource_type, recommendation.status]"
        >
          <div class="recommendation-header">
            <div class="recommendation-type">
              <span class="type-icon" :class="recommendation.resource_type">
                <!-- Article Icon -->
                <svg v-if="recommendation.resource_type === 'article'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                
                <!-- Video Icon -->
                <svg v-else-if="recommendation.resource_type === 'video'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                  <line x1="7" y1="2" x2="7" y2="22"></line>
                  <line x1="17" y1="2" x2="17" y2="22"></line>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <line x1="2" y1="7" x2="7" y2="7"></line>
                  <line x1="2" y1="17" x2="7" y2="17"></line>
                  <line x1="17" y1="17" x2="22" y2="17"></line>
                  <line x1="17" y1="7" x2="22" y2="7"></line>
                </svg>
                
                <!-- Course Icon -->
                <svg v-else-if="recommendation.resource_type === 'course'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                
                <!-- Tool Icon -->
                <svg v-else-if="recommendation.resource_type === 'tool'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
                
                <!-- Reference Icon -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
              </span>
              <span class="type-label">{{ formatResourceType(recommendation.resource_type) }}</span>
            </div>
            
            <div class="status-badge" :class="recommendation.status">
              {{ formatStatus(recommendation.status) }}
            </div>
          </div>
          
          <div class="recommendation-body">
            <h2 class="resource-title">{{ recommendation.resource.title }}</h2>
            
            <div class="resource-meta">
              <div class="meta-item" v-if="recommendation.resource.author">
                <span class="meta-label">Author:</span>
                <span class="meta-value">{{ recommendation.resource.author }}</span>
              </div>
              
              <div class="meta-item" v-if="recommendation.resource.estimated_time_minutes">
                <span class="meta-label">Estimated Time:</span>
                <span class="meta-value">{{ formatTime(recommendation.resource.estimated_time_minutes) }}</span>
              </div>
              
              <div class="meta-item">
                <span class="meta-label">Difficulty:</span>
                <span class="meta-value">{{ formatDifficulty(recommendation.resource.difficulty_level) }}</span>
              </div>
            </div>
            
            <p class="resource-description">{{ recommendation.resource.description }}</p>
            
            <div class="related-skills">
              <span class="skills-label">Related Skills:</span>
              <div class="skills-tags">
                <span v-for="(skill, index) in parseRelatedSkills(recommendation.resource.related_skills)" 
                      :key="index" class="skill-tag">
                  {{ skill }}
                </span>
              </div>
            </div>
            
            <div class="recommendation-reason">
              <h4>Why we recommend this:</h4>
              <p>{{ recommendation.recommendation_reason }}</p>
            </div>
            
            <div class="relevance-meter">
              <span class="relevance-label">Relevance to your needs:</span>
              <div class="relevance-score">
                <div class="relevance-dots">
                  <span v-for="n in 5" :key="n" class="relevance-dot"
                       :class="{ filled: n <= Math.round(recommendation.relevance_score / 20) }">
                  </span>
                </div>
                <span class="relevance-percentage">{{ recommendation.relevance_score }}%</span>
              </div>
            </div>
          </div>
          
          <div class="recommendation-actions">
            <button class="btn-primary" @click="viewResource(recommendation)">
              View Resource
            </button>
            
            <button v-if="recommendation.status !== 'saved' && recommendation.status !== 'completed'"
                   class="btn-outline" @click="saveRecommendation(recommendation.id)">
              Save for Later
            </button>
            
            <button v-if="recommendation.status !== 'completed'"
                   class="btn-outline" @click="markCompleted(recommendation.id)">
              Mark as Completed
            </button>
            
            <button v-if="recommendation.status === 'saved'"
                   class="btn-outline" @click="removeFromSaved(recommendation.id)">
              Remove from Saved
            </button>
          </div>
        </div>
      </div>
      
      <!-- Saved Resources Section -->
      <div class="saved-section" v-if="activeFilter === 'all' && statusFilter === 'all' && !searchQuery">
        <h3 class="section-title">Saved Resources</h3>
        
        <div v-if="savedRecommendations.length === 0" class="empty-saved">
          <p>You haven't saved any resources yet. Use the "Save for Later" button on any recommendation to add it here.</p>
        </div>
        
        <div v-else class="saved-list">
          <div v-for="saved in savedRecommendations" :key="saved.id" class="saved-item">
            <div class="saved-info">
              <div class="saved-type-badge" :class="saved.resource_type">
                {{ formatResourceType(saved.resource_type) }}
              </div>
              <h4 class="saved-title">{{ saved.resource.title }}</h4>
            </div>
            
            <div class="saved-actions">
              <button class="btn-small" @click="viewResource(saved)">
                View
              </button>
              <button class="btn-small outline" @click="removeFromSaved(saved.id)">
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
import debounce from 'lodash/debounce'

export default {
  name: 'RecommendationsView',
  
  data() {
    return {
      activeFilter: 'all',
      statusFilter: 'all',
      selectedSkill: '',
      searchQuery: '',
      generating: false,
      recommendationsLoaded: false,
      debouncedSearch: null
    }
  },
  
  computed: {
    ...mapGetters({
      recommendations: 'recommendations/recommendations',
      savedRecommendations: 'recommendations/savedRecommendations',
      skillsList: 'recommendations/skillsList',
      loading: 'recommendations/loading',
      error: 'recommendations/error'
    }),
    
    hasRecommendations() {
      return this.recommendations && this.recommendations.length > 0
    },
    
    filteredRecommendations() {
      if (!this.recommendations) return []
      
      let filtered = [...this.recommendations]
      
      // Filter by type
      if (this.activeFilter !== 'all') {
        filtered = filtered.filter(rec => rec.resource_type === this.activeFilter)
      }
      
      // Filter by status
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(rec => rec.status === this.statusFilter)
      }
      
      // Filter by skill
      if (this.selectedSkill) {
        filtered = filtered.filter(rec => {
          const relatedSkills = this.parseRelatedSkills(rec.resource.related_skills)
          return relatedSkills.some(skill => 
            skill.id === this.selectedSkill || 
            skill.toLowerCase().includes(this.getSkillNameById(this.selectedSkill).toLowerCase())
          )
        })
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(rec => 
          rec.resource.title.toLowerCase().includes(query) ||
          rec.resource.description.toLowerCase().includes(query) ||
          (rec.resource.author && rec.resource.author.toLowerCase().includes(query)) ||
          this.parseRelatedSkills(rec.resource.related_skills).some(skill => 
            typeof skill === 'string' && skill.toLowerCase().includes(query)
          )
        )
      }
      
      return filtered
    },
    
    hasFilters() {
      return this.activeFilter !== 'all' || 
             this.statusFilter !== 'all' || 
             this.selectedSkill !== '' || 
             this.searchQuery !== ''
    }
  },
  
  created() {
    this.debouncedSearch = debounce(() => {
      // This will re-compute filteredRecommendations
    }, 300)
    
    this.fetchRecommendations()
      .then(() => {
        this.recommendationsLoaded = true
      })
    this.fetchSavedRecommendations()
    this.fetchSkillsList()
  },
  
  methods: {
    ...mapActions({
      fetchRecommendations: 'recommendations/fetchRecommendations',
      fetchSavedRecommendations: 'recommendations/fetchSavedRecommendations',
      fetchSkillsList: 'recommendations/fetchSkillsList',
      saveRecommendationAction: 'recommendations/saveRecommendation',
      completeRecommendationAction: 'recommendations/completeRecommendation',
      removeSavedAction: 'recommendations/removeSaved',
      generateRecommendationsAction: 'recommendations/generateRecommendations',
      viewRecommendationAction: 'recommendations/viewRecommendation'
    }),
    
    setFilter(filter) {
      this.activeFilter = filter
    },
    
    setStatusFilter(status) {
      this.statusFilter = status
    },
    
    clearFilters() {
      this.activeFilter = 'all'
      this.statusFilter = 'all'
      this.selectedSkill = ''
      this.searchQuery = ''
    },
    
    async viewResource(recommendation) {
      try {
        // Mark as viewed in the backend
        await this.viewRecommendationAction(recommendation.id)
        
        // Open resource in new tab if URL exists
        if (recommendation.resource.url) {
          window.open(recommendation.resource.url, '_blank')
        } else {
          // Navigate to resource view if no direct URL
          this.$router.push(`/resources/${recommendation.resource.id}`)
        }
      } catch (error) {
        console.error('Error viewing recommendation:', error)
      }
    },
    
    async saveRecommendation(id) {
      try {
        await this.saveRecommendationAction(id)
      } catch (error) {
        console.error('Error saving recommendation:', error)
      }
    },
    
    async markCompleted(id) {
      try {
        await this.completeRecommendationAction(id)
      } catch (error) {
        console.error('Error marking recommendation as completed:', error)
      }
    },
    
    async removeFromSaved(id) {
      try {
        await this.removeSavedAction(id)
      } catch (error) {
        console.error('Error removing saved recommendation:', error)
      }
    },
    
    async generateRecommendations() {
      this.generating = true
      try {
        await this.generateRecommendationsAction()
        this.recommendationsLoaded = true
      } catch (error) {
        console.error('Error generating recommendations:', error)
      } finally {
        this.generating = false
      }
    },
    
    formatResourceType(type) {
      const types = {
        article: 'Article',
        video: 'Video',
        course: 'Course',
        tool: 'Tool',
        reference: 'Reference'
      }
      return types[type] || 'Resource'
    },
    
    formatStatus(status) {
      const statuses = {
        new: 'New',
        viewed: 'Viewed',
        saved: 'Saved',
        completed: 'Completed',
        dismissed: 'Dismissed'
      }
      return statuses[status] || status
    },
    
    formatTime(minutes) {
      if (minutes < 60) {
        return `${minutes} min${minutes !== 1 ? 's' : ''}`
      } else {
        const hours = Math.floor(minutes / 60)
        const remainingMinutes = minutes % 60
        if (remainingMinutes === 0) {
          return `${hours} hour${hours !== 1 ? 's' : ''}`
        } else {
          return `${hours} hour${hours !== 1 ? 's' : ''} ${remainingMinutes} min${remainingMinutes !== 1 ? 's' : ''}`
        }
      }
    },
    
    formatDifficulty(level) {
      if (!level) return 'Not specified'
      
      const difficulties = {
        1: 'Beginner',
        2: 'Easy',
        3: 'Intermediate',
        4: 'Advanced',
        5: 'Expert'
      }
      
      return difficulties[level] || `Level ${level}`
    },
    
    parseRelatedSkills(skills) {
      if (!skills) return []
      
      // Handle JSON string
      if (typeof skills === 'string') {
        try {
          return JSON.parse(skills)
        } catch (e) {
          // If not valid JSON, split by commas
          return skills.split(',').map(s => s.trim())
        }
      }
      
      // Handle array
      if (Array.isArray(skills)) {
        return skills
      }
      
      // Handle object
      if (typeof skills === 'object') {
        return Object.values(skills)
      }
      
      return []
    },
    
    getSkillNameById(id) {
      if (!this.skillsList || !id) return ''
      
      const skill = this.skillsList.find(s => s.id === id || s.id === parseInt(id))
      return skill ? skill.name : ''
    }
  }
}
</script>

<style scoped>
.recommendations-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Roboto', Arial, sans-serif;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 500;
  color: #2a2f45;
  margin: 0 0 8px 0;
}

.page-description {
  color: #5a617b;
  font-size: 16px;
  line-height: 1.5;
  margin: 0;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 60px 20px;
  text-align: center;
  margin-top: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(25, 118, 210, 0.1);
  border-radius: 50%;
  border-top-color: #1976d2;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px 20px;
  text-align: center;
  margin-top: 20px;
  color: #d32f2f;
}

.error-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(211, 47, 47, 0.1);
  border-radius: 50%;
  margin-bottom: 16px;
}

.error-container h3 {
  font-size: 20px;
  margin: 0 0 8px 0;
}

.error-container p {
  margin: 0 0 20px 0;
  color: #5a617b;
}

/* Empty State */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 60px 20px;
  text-align: center;
  margin-top: 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4fa;
  border-radius: 50%;
  margin-bottom: 24px;
  color: #5a617b;
}

.empty-container h2 {
  font-size: 24px;
  margin: 0 0 12px 0;
  color: #2a2f45;
}

.empty-container p {
  margin: 0 0 24px 0;
  color: #5a617b;
  max-width: 400px;
}

/* Buttons */
.btn-primary {
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-primary:disabled {
  background-color: #b0bec5;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-left: 8px;
}

.btn-outline {
  background-color: transparent;
  color: #1976d2;
  border: 1px solid #1976d2;
  border-radius: 4px;
  padding: 11px 19px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-outline:hover {
  background-color: rgba(25, 118, 210, 0.05);
}

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-small.outline {
  padding: 5px 11px;
  color: #5a617b;
  border-color: #c8ccd8;
}

.btn-small.outline:hover {
  background-color: rgba(90, 97, 123, 0.05);
}

/* Content Styles */
.recommendations-content {
  margin-top: 24px;
}

/* Filter Controls */
.filter-controls {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.filter-section h3 {
  font-size: 14px;
  font-weight: 500;
  color: #5a617b;
  margin: 0 0 12px 0;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  background: #f0f4fa;
  border: 1px solid transparent;
  border-radius: 30px;
  padding: 6px 12px;
  font-size: 13px;
  color: #5a617b;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #e3e9f2;
}

.filter-btn.active {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
  font-weight: 500;
}

.skill-select {
  width: 100%;
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid #c8ccd8;
  font-size: 14px;
  background-color: white;
  color: #2a2f45;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%235a617b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

.search-section {
  grid-column: 1 / -1;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #c8ccd8;
  font-size: 14px;
  background-color: white;
  color: #2a2f45;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: #a0a8bd;
}

/* Results Info */
.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-info p {
  color: #5a617b;
  font-size: 14px;
  margin: 0;
}

.clear-filters-btn {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.clear-filters-btn:hover {
  text-decoration: underline;
}

/* Filtered Empty State */
.filtered-empty {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  margin-bottom: 24px;
}

.filtered-empty h3 {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #2a2f45;
}

.filtered-empty p {
  margin: 0 0 20px 0;
  color: #5a617b;
}

/* Recommendations List */
.recommendations-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.recommendation-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid transparent;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* Card type colors */
.recommendation-card.article {
  border-left-color: #2196f3;
}

.recommendation-card.video {
  border-left-color: #f44336;
}

.recommendation-card.course {
  border-left-color: #4caf50;
}

.recommendation-card.tool {
  border-left-color: #ff9800;
}

.recommendation-card.reference {
  border-left-color: #9c27b0;
}

/* Status indicators */
.recommendation-card.new::after {
  content: '';
  position: absolute;
  top: 12px;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #2196f3;
}

.recommendation-card.completed {
  opacity: 0.85;
  border-left-color: #66bb6a;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f4fa;
}

.recommendation-type {
  display: flex;
  align-items: center;
}

.type-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 8px;
}

.type-icon.article {
  color: #2196f3;
  background-color: rgba(33, 150, 243, 0.1);
}

.type-icon.video {
  color: #f44336;
  background-color: rgba(244, 67, 54, 0.1);
}

.type-icon.course {
  color: #4caf50;
  background-color: rgba(76, 175, 80, 0.1);
}

.type-icon.tool {
  color: #ff9800;
  background-color: rgba(255, 152, 0, 0.1);
}

.type-icon.reference {
  color: #9c27b0;
  background-color: rgba(156, 39, 176, 0.1);
}

.type-label {
  font-size: 13px;
  font-weight: 500;
}

.status-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  text-transform: uppercase;
}

.status-badge.new {
  background-color: rgba(33, 150, 243, 0.1);
  color: #1976d2;
}

.status-badge.viewed {
  background-color: rgba(96, 125, 139, 0.1);
  color: #546e7a;
}

.status-badge.saved {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ff8f00;
}

.status-badge.completed {
  background-color: rgba(76, 175, 80, 0.1);
  color: #388e3c;
}

.recommendation-body {
  padding: 20px;
}

.resource-title {
  font-size: 18px;
  font-weight: 500;
  color: #2a2f45;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.meta-label {
  color: #5a617b;
  margin-right: 4px;
}

.meta-value {
  color: #2a2f45;
  font-weight: 500;
}

.resource-description {
  color: #5a617b;
  margin: 0 0 20px 0;
  line-height: 1.6;
  font-size: 14px;
}

.related-skills {
  margin-bottom: 20px;
}

.skills-label {
  display: block;
  font-size: 13px;
  color: #5a617b;
  margin-bottom: 8px;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  background-color: #f0f4fa;
  color: #5a617b;
  padding: 4px 10px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 500;
}

.recommendation-reason {
  background-color: #f8fafd;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.recommendation-reason h4 {
  font-size: 14px;
  color: #2a2f45;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.recommendation-reason p {
  font-size: 14px;
  color: #5a617b;
  margin: 0;
  line-height: 1.5;
}

.relevance-meter {
  margin-bottom: 8px;
}

.relevance-label {
  display: block;
  font-size: 13px;
  color: #5a617b;
  margin-bottom: 8px;
}

.relevance-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.relevance-dots {
  display: flex;
  gap: 3px;
}

.relevance-dot {
  width: 16px;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.relevance-dot.filled {
  background-color: #1976d2;
}

.relevance-percentage {
  font-size: 14px;
  font-weight: 500;
  color: #1976d2;
}

.recommendation-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 0 20px 20px;
}

/* Saved Resources Section */
.saved-section {
  margin-top: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 500;
  color: #2a2f45;
  margin: 0 0 20px 0;
}

.empty-saved {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: center;
}

.empty-saved p {
  color: #5a617b;
  margin: 0;
  font-size: 14px;
}

.saved-list {
  display: grid;
  gap: 12px;
}

.saved-item {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.saved-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.saved-type-badge {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.saved-type-badge.article {
  background-color: rgba(33, 150, 243, 0.1);
  color: #1976d2;
}

.saved-type-badge.video {
  background-color: rgba(244, 67, 54, 0.1);
  color: #d32f2f;
}

.saved-type-badge.course {
  background-color: rgba(76, 175, 80, 0.1);
  color: #388e3c;
}

.saved-type-badge.tool {
  background-color: rgba(255, 152, 0, 0.1);
  color: #f57c00;
}

.saved-type-badge.reference {
  background-color: rgba(156, 39, 176, 0.1);
  color: #7b1fa2;
}

.saved-title {
  margin: 0;
  font-size: 14px;
  color: #2a2f45;
  font-weight: 500;
}

.saved-actions {
  display: flex;
  gap: 8px;
}

/* Responsive Adjustments */
@media (min-width: 768px) {
  .recommendations-list {
    grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  }
  
  .saved-list {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 767px) {
  .recommendation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .status-badge {
    align-self: flex-start;
  }
  
  .recommendation-actions {
    flex-direction: column;
  }
  
  .saved-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .saved-actions {
    align-self: flex-end;
  }
}
</style>
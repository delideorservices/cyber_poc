import axios from 'axios'

// Initial state
const state = {
  recommendations: [],
  savedRecommendations: [],
  completedRecommendations: [],
  currentResource: null,
  loading: false,
  generating: false,
  error: null
}

// Getters
const getters = {
  // Get all recommendations
  recommendations: state => state.recommendations,
  
  // Get saved recommendations
  savedRecommendations: state => state.savedRecommendations,
  
  // Get completed recommendations
  completedRecommendations: state => state.completedRecommendations,
  
  // Get current resource
  currentResource: state => state.currentResource,
  
  // Get recommendations by type
  recommendationsByType: state => type => {
    return state.recommendations.filter(rec => rec.resource_type === type)
  },
  
  // Get recommendations by skill
  recommendationsBySkill: state => skillId => {
    return state.recommendations.filter(rec => {
      return rec.related_skills && rec.related_skills.includes(skillId)
    })
  },
  
  // Get loading state
  loading: state => state.loading,
  
  // Get generating state
  generating: state => state.generating,
  
  // Get error state
  error: state => state.error,
  
  // Check if there are any recommendations
  hasRecommendations: state => state.recommendations.length > 0,
  
  // Group recommendations by category
  groupedRecommendations: state => {
    const grouped = {
      articles: [],
      videos: [],
      courses: [],
      tools: [],
      other: []
    }
    
    state.recommendations.forEach(rec => {
      if (grouped[rec.resource_type]) {
        grouped[rec.resource_type].push(rec)
      } else {
        grouped.other.push(rec)
      }
    })
    
    return grouped
  }
}

// Mutations
const mutations = {
  // Set recommendations
  SET_RECOMMENDATIONS(state, recommendations) {
    state.recommendations = recommendations
  },
  
  // Set saved recommendations
  SET_SAVED_RECOMMENDATIONS(state, recommendations) {
    state.savedRecommendations = recommendations
  },
  
  // Set completed recommendations
  SET_COMPLETED_RECOMMENDATIONS(state, recommendations) {
    state.completedRecommendations = recommendations
  },
  
  // Set current resource
  SET_CURRENT_RESOURCE(state, resource) {
    state.currentResource = resource
  },
  
  // Update recommendation status
  UPDATE_RECOMMENDATION_STATUS(state, { id, status }) {
    // Update in main recommendations array
    const index = state.recommendations.findIndex(rec => rec.id === id)
    if (index !== -1) {
      state.recommendations[index].status = status
    }
    
    // Update saved recommendations if status is 'saved'
    if (status === 'saved') {
      if (!state.savedRecommendations.some(rec => rec.id === id)) {
        const recommendation = state.recommendations.find(rec => rec.id === id)
        if (recommendation) {
          state.savedRecommendations.push({ ...recommendation, status: 'saved' })
        }
      }
    } else if (status === 'completed') {
      // Remove from saved if it was there
      state.savedRecommendations = state.savedRecommendations.filter(rec => rec.id !== id)
      
      // Add to completed
      if (!state.completedRecommendations.some(rec => rec.id === id)) {
        const recommendation = state.recommendations.find(rec => rec.id === id)
        if (recommendation) {
          state.completedRecommendations.push({ ...recommendation, status: 'completed' })
        }
      }
    }
  },
  
  // Remove recommendation from saved
  REMOVE_SAVED_RECOMMENDATION(state, id) {
    state.savedRecommendations = state.savedRecommendations.filter(rec => rec.id !== id)
    
    // Update main recommendations array
    const index = state.recommendations.findIndex(rec => rec.id === id)
    if (index !== -1 && state.recommendations[index].status === 'saved') {
      state.recommendations[index].status = 'new'
    }
  },
  
  // Set loading state
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  // Set generating state
  SET_GENERATING(state, generating) {
    state.generating = generating
  },
  
  // Set error state
  SET_ERROR(state, error) {
    state.error = error
  },
  
  // Clear error state
  CLEAR_ERROR(state) {
    state.error = null
  }
}

// Actions
const actions = {
  // Fetch recommendations
  async fetchRecommendations({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/recommendations')
      
      if (response.data.status === 'success') {
        commit('SET_RECOMMENDATIONS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load recommendations')
        return null
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      commit('SET_ERROR', 'Failed to load recommendations')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch saved recommendations
  async fetchSavedRecommendations({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/recommendations/saved')
      
      if (response.data.status === 'success') {
        commit('SET_SAVED_RECOMMENDATIONS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load saved recommendations')
        return null
      }
    } catch (error) {
      console.error('Error fetching saved recommendations:', error)
      commit('SET_ERROR', 'Failed to load saved recommendations')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch completed recommendations
  async fetchCompletedRecommendations({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/recommendations/completed')
      
      if (response.data.status === 'success') {
        commit('SET_COMPLETED_RECOMMENDATIONS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load completed recommendations')
        return null
      }
    } catch (error) {
      console.error('Error fetching completed recommendations:', error)
      commit('SET_ERROR', 'Failed to load completed recommendations')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // View a recommendation
  async viewRecommendation({ commit }, id) {
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(`/api/recommendations/${id}/view`)
      
      if (response.data.status === 'success') {
        // Update status if it has changed
        if (response.data.data && response.data.data.status) {
          commit('UPDATE_RECOMMENDATION_STATUS', { 
            id, 
            status: response.data.data.status 
          })
        }
        
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to track recommendation view')
        return null
      }
    } catch (error) {
      console.error('Error viewing recommendation:', error)
      commit('SET_ERROR', 'Failed to track recommendation view')
      return null
    }
  },
  
  // Save a recommendation
  async saveRecommendation({ commit }, id) {
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(`/api/recommendations/${id}/save`)
      
      if (response.data.status === 'success') {
        commit('UPDATE_RECOMMENDATION_STATUS', { id, status: 'saved' })
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to save recommendation')
        return null
      }
    } catch (error) {
      console.error('Error saving recommendation:', error)
      commit('SET_ERROR', 'Failed to save recommendation')
      return null
    }
  },
  
  // Complete a recommendation
  async completeRecommendation({ commit }, id) {
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(`/api/recommendations/${id}/complete`)
      
      if (response.data.status === 'success') {
        commit('UPDATE_RECOMMENDATION_STATUS', { id, status: 'completed' })
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to mark recommendation as completed')
        return null
      }
    } catch (error) {
      console.error('Error completing recommendation:', error)
      commit('SET_ERROR', 'Failed to mark recommendation as completed')
      return null
    }
  },
  
  // Remove saved recommendation
  async removeSaved({ commit }, id) {
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(`/api/recommendations/${id}/unsave`)
      
      if (response.data.status === 'success') {
        commit('REMOVE_SAVED_RECOMMENDATION', id)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to remove saved recommendation')
        return null
      }
    } catch (error) {
      console.error('Error removing saved recommendation:', error)
      commit('SET_ERROR', 'Failed to remove saved recommendation')
      return null
    }
  },
  
  // Generate new recommendations
  async generateRecommendations({ commit, dispatch }) {
    commit('SET_GENERATING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post('/api/recommendations/generate')
      
      if (response.data.status === 'success') {
        // Refresh recommendations list
        await dispatch('fetchRecommendations')
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to generate recommendations')
        return null
      }
    } catch (error) {
      console.error('Error generating recommendations:', error)
      commit('SET_ERROR', 'Failed to generate recommendations')
      return null
    } finally {
      commit('SET_GENERATING', false)
    }
  },
  
  // Get resource details
  async getResourceDetails({ commit }, resourceId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(`/api/resources/${resourceId}`)
      
      if (response.data.status === 'success') {
        commit('SET_CURRENT_RESOURCE', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load resource details')
        return null
      }
    } catch (error) {
      console.error('Error fetching resource details:', error)
      commit('SET_ERROR', 'Failed to load resource details')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
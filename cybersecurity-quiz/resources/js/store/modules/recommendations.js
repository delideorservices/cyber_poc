import axios from 'axios'

// Initial state
const state = {
  recommendations: [],
  savedRecommendations: [],
  resourceTypes: [],
  loading: false,
  generating: false,
  error: null
}

// Getters
const getters = {
  recommendations: state => state.recommendations,
  savedRecommendations: state => state.savedRecommendations,
  resourceTypes: state => state.resourceTypes,
  loading: state => state.loading,
  generating: state => state.generating,
  error: state => state.error
}

// Mutations
const mutations = {
  SET_RECOMMENDATIONS(state, recommendations) {
    state.recommendations = recommendations
  },
  
  SET_SAVED_RECOMMENDATIONS(state, recommendations) {
    state.savedRecommendations = recommendations
  },
  
  SET_RESOURCE_TYPES(state, types) {
    state.resourceTypes = types
  },
  
  UPDATE_RECOMMENDATION(state, { id, changes }) {
    const index = state.recommendations.findIndex(r => r.id === id)
    if (index !== -1) {
      state.recommendations[index] = { ...state.recommendations[index], ...changes }
    }
  },
  
  REMOVE_RECOMMENDATION(state, id) {
    state.recommendations = state.recommendations.filter(r => r.id !== id)
  },
  
  REMOVE_SAVED_RECOMMENDATION(state, id) {
    state.savedRecommendations = state.savedRecommendations.filter(r => r.id !== id)
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_GENERATING(state, generating) {
    state.generating = generating
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  }
}

// Actions
const actions = {
  // Fetch all recommendations
  async fetchRecommendations({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/recommendations')
      
      if (response.data && response.data.recommendations) {
        commit('SET_RECOMMENDATIONS', response.data.recommendations)
      }
      
      if (response.data && response.data.resource_types) {
        commit('SET_RESOURCE_TYPES', response.data.resource_types)
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      commit('SET_ERROR', 'Failed to load recommendations')
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
      
      if (response.data) {
        commit('SET_SAVED_RECOMMENDATIONS', response.data)
      }
    } catch (error) {
      console.error('Error fetching saved recommendations:', error)
      commit('SET_ERROR', 'Failed to load saved recommendations')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Generate new recommendations
  async generateRecommendations({ commit }, filters = {}) {
    commit('SET_GENERATING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post('/api/recommendations/generate', filters)
      
      if (response.data && response.data.recommendations) {
        commit('SET_RECOMMENDATIONS', response.data.recommendations)
      }
      
      if (response.data && response.data.resource_types) {
        commit('SET_RESOURCE_TYPES', response.data.resource_types)
      }
      
      return response.data
    } catch (error) {
      console.error('Error generating recommendations:', error)
      commit('SET_ERROR', 'Failed to generate recommendations')
      throw error
    } finally {
      commit('SET_GENERATING', false)
    }
  },
  
  // Mark recommendation as viewed
  async viewRecommendation({ commit }, id) {
    try {
      const response = await axios.post(`/api/recommendations/${id}/viewed`)
      
      if (response.data) {
        commit('UPDATE_RECOMMENDATION', { 
          id, 
          changes: { 
            status: 'viewed',
            viewed_at: new Date()
          }
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Error viewing recommendation:', error)
      throw error
    }
  },
  
  // Save recommendation for later
  async saveRecommendation({ commit }, id) {
    try {
      const response = await axios.post(`/api/recommendations/${id}/save`)
      
      if (response.data) {
        commit('UPDATE_RECOMMENDATION', { 
          id, 
          changes: { status: 'saved' }
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Error saving recommendation:', error)
      throw error
    }
  },
  
  // Remove recommendation from saved list
  async removeSavedRecommendation({ commit }, id) {
    try {
      const response = await axios.delete(`/api/recommendations/${id}/save`)
      
      if (response.data) {
        commit('REMOVE_SAVED_RECOMMENDATION', id)
      }
      
      return response.data
    } catch (error) {
      console.error('Error removing saved recommendation:', error)
      throw error
    }
  },
  
  // Provide feedback on a recommendation
  async provideFeedback({ commit }, { id, rating, feedback }) {
    try {
      const data = { rating }
      if (feedback) {
        data.feedback = feedback
      }
      
      const response = await axios.post(`/api/recommendations/${id}/feedback`, data)
      
      if (response.data) {
        commit('UPDATE_RECOMMENDATION', { 
          id, 
          changes: { 
            user_rating: rating,
            user_feedback: feedback,
            feedback: { rating, text: feedback }
          }
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Error providing feedback:', error)
      throw error
    }
  },
  
  // Mark recommendation as completed
  async completeRecommendation({ commit }, { id, rating, feedback }) {
    try {
      const data = {}
      if (rating) {
        data.rating = rating
      }
      if (feedback) {
        data.feedback = feedback
      }
      
      const response = await axios.post(`/api/recommendations/${id}/completed`, data)
      
      if (response.data) {
        commit('UPDATE_RECOMMENDATION', { 
          id, 
          changes: { 
            status: 'completed',
            completed_at: new Date(),
            user_rating: rating,
            user_feedback: feedback
          }
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Error completing recommendation:', error)
      throw error
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
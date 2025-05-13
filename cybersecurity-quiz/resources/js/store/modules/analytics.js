import axios from 'axios'

// Initial state
const state = {
  analytics: null,
  skillAnalytics: {},
  domains: [],
  strengths: [],
  weaknesses: [],
  peerComparison: null,
  performanceTrends: [],
  loading: false,
  error: null
}

// Getters
const getters = {
  // Get overall analytics data
  analytics: state => state.analytics,
  
  // Get analytics for a specific skill
  skillAnalytics: state => skillId => {
    return state.skillAnalytics[skillId] || null
  },
  
  // Get all skill analytics
  allSkillAnalytics: state => state.skillAnalytics,
  
  // Get domain proficiency data
  domains: state => state.domains,
  
  // Get user strengths
  strengths: state => state.strengths,
  
  // Get user weaknesses
  weaknesses: state => state.weaknesses,
  
  // Get peer comparison data
  peerComparison: state => state.peerComparison,
  
  // Get performance trends over time
  performanceTrends: state => state.performanceTrends,
  
  // Get loading state
  loading: state => state.loading,
  
  // Get error state
  error: state => state.error,
  
  // Calculate overall proficiency score (average of all skills)
  overallProficiency: state => {
    if (!state.strengths.length && !state.weaknesses.length) return 0
    
    const allSkills = [...state.strengths, ...state.weaknesses]
    if (!allSkills.length) return 0
    
    const sum = allSkills.reduce((total, skill) => total + skill.proficiency_score, 0)
    return Math.round(sum / allSkills.length)
  }
}

// Mutations
const mutations = {
  // Set overall analytics data
  SET_ANALYTICS(state, analytics) {
    state.analytics = analytics
  },
  
  // Set analytics for a specific skill
  SET_SKILL_ANALYTICS(state, { skillId, data }) {
    state.skillAnalytics = {
      ...state.skillAnalytics,
      [skillId]: data
    }
  },
  
  // Set domain proficiency data
  SET_DOMAINS(state, domains) {
    state.domains = domains
  },
  
  // Set user strengths
  SET_STRENGTHS(state, strengths) {
    state.strengths = strengths
  },
  
  // Set user weaknesses
  SET_WEAKNESSES(state, weaknesses) {
    state.weaknesses = weaknesses
  },
  
  // Set peer comparison data
  SET_PEER_COMPARISON(state, data) {
    state.peerComparison = data
  },
  
  // Set performance trends
  SET_PERFORMANCE_TRENDS(state, trends) {
    state.performanceTrends = trends
  },
  
  // Set loading state
  SET_LOADING(state, loading) {
    state.loading = loading
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
  // Fetch user analytics
  async fetchAnalytics({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/analytics/user')
      
      if (response.data.status === 'success') {
        const analyticsData = response.data.data
        
        commit('SET_ANALYTICS', analyticsData)
        
        // Extract domains if available
        if (analyticsData.domains) {
          commit('SET_DOMAINS', analyticsData.domains)
        }
        
        // Extract strengths if available
        if (analyticsData.strengths) {
          commit('SET_STRENGTHS', analyticsData.strengths)
        }
        
        // Extract weaknesses if available
        if (analyticsData.weaknesses) {
          commit('SET_WEAKNESSES', analyticsData.weaknesses)
        }
        
        // Extract performance trends if available
        if (analyticsData.performance_trends) {
          commit('SET_PERFORMANCE_TRENDS', analyticsData.performance_trends)
        }
        
        return analyticsData
      } else {
        commit('SET_ERROR', 'Failed to load analytics data')
        return null
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
      commit('SET_ERROR', 'Failed to load analytics data')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch analytics for a specific skill
  async fetchSkillAnalytics({ commit }, skillId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(`/api/analytics/skill/${skillId}`)
      
      if (response.data.status === 'success') {
        commit('SET_SKILL_ANALYTICS', { 
          skillId, 
          data: response.data.data 
        })
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load skill analytics')
        return null
      }
    } catch (error) {
      console.error('Error fetching skill analytics:', error)
      commit('SET_ERROR', 'Failed to load skill analytics')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch peer comparison data
  async fetchPeerComparison({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/analytics/peer-comparison')
      
      if (response.data.status === 'success') {
        commit('SET_PEER_COMPARISON', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load peer comparison data')
        return null
      }
    } catch (error) {
      console.error('Error fetching peer comparison:', error)
      commit('SET_ERROR', 'Failed to load peer comparison data')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Generate analytics report (PDF or data export)
  async generateAnalyticsReport({ state, commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/analytics/report', {
        responseType: 'blob'
      })
      
      // Create a blob URL for the PDF
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      
      // Open the PDF in a new tab
      window.open(url, '_blank')
      
      return { status: 'success' }
    } catch (error) {
      console.error('Error generating analytics report:', error)
      commit('SET_ERROR', 'Failed to generate analytics report')
      return { status: 'error', message: 'Failed to generate analytics report' }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Generate enhanced analytics using the Analytics Agent
  async generateEnhancedAnalytics({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post('/api/analytics/generate')
      
      if (response.data.status === 'success') {
        // Refresh analytics data with the newly generated data
        await dispatch('fetchAnalytics')
        return { status: 'success' }
      } else {
        commit('SET_ERROR', 'Failed to generate enhanced analytics')
        return { status: 'error', message: 'Failed to generate enhanced analytics' }
      }
    } catch (error) {
      console.error('Error generating enhanced analytics:', error)
      commit('SET_ERROR', 'Failed to generate enhanced analytics')
      return { status: 'error', message: error.message || 'Failed to generate enhanced analytics' }
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
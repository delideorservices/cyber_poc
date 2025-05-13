import axios from 'axios'

// Initial state
const state = {
  plan: null,
  modules: [],
  progress: [],
  loading: false,
  generating: false,
  error: null
}

// Getters
const getters = {
  // Get the user's learning plan
  learningPlan: state => state.plan,
  
  // Get the user's learning plan modules
  modules: state => state.modules,
  
  // Get module by ID
  getModuleById: state => id => {
    return state.modules.find(module => module.id === id)
  },
  
  // Calculate overall progress percentage
  overallProgress: state => {
    if (!state.modules.length) return 0
    
    const completedModules = state.modules.filter(
      module => module.status === 'completed'
    ).length
    
    return Math.round((completedModules / state.modules.length) * 100)
  },
  
  // Get modules grouped by status
  modulesByStatus: state => {
    return {
      notStarted: state.modules.filter(m => m.status === 'not_started'),
      inProgress: state.modules.filter(m => m.status === 'in_progress'),
      completed: state.modules.filter(m => m.status === 'completed')
    }
  },
  
  // Loading state
  loading: state => state.loading,
  
  // Generating state
  generating: state => state.generating,
  
  // Error state
  error: state => state.error
}

// Mutations
const mutations = {
  // Set the learning plan
  SET_PLAN(state, plan) {
    state.plan = plan
  },
  
  // Set the learning plan modules
  SET_MODULES(state, modules) {
    state.modules = modules
  },
  
  // Set the learning plan progress
  SET_PROGRESS(state, progress) {
    state.progress = progress
  },
  
  // Update a single module's status
  UPDATE_MODULE_STATUS(state, { moduleId, status }) {
    const moduleIndex = state.modules.findIndex(m => m.id === moduleId)
    if (moduleIndex !== -1) {
      state.modules[moduleIndex].status = status
      
      // Also update progress percentage if completed
      if (status === 'completed') {
        state.modules[moduleIndex].progress_percentage = 100
      } else if (status === 'in_progress' && state.modules[moduleIndex].progress_percentage === 0) {
        state.modules[moduleIndex].progress_percentage = 5
      }
    }
  },
  
  // Update a single module's progress
  UPDATE_MODULE_PROGRESS(state, { moduleId, progress }) {
    const moduleIndex = state.modules.findIndex(m => m.id === moduleId)
    if (moduleIndex !== -1) {
      state.modules[moduleIndex].progress_percentage = progress
      
      // Update status based on progress
      if (progress >= 100) {
        state.modules[moduleIndex].status = 'completed'
      } else if (progress > 0) {
        state.modules[moduleIndex].status = 'in_progress'
      }
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
  // Fetch the user's learning plan
  async fetchLearningPlan({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/learning-plan')
      
      if (response.data.status === 'success') {
        commit('SET_PLAN', response.data.data)
        
        // If modules are included in the response
        if (response.data.data && response.data.data.modules) {
          commit('SET_MODULES', response.data.data.modules)
        }
        
        // If progress is included in the response
        if (response.data.data && response.data.data.progress) {
          commit('SET_PROGRESS', response.data.data.progress)
        }
      } else {
        commit('SET_ERROR', 'Failed to load learning plan')
      }
    } catch (error) {
      console.error('Error fetching learning plan:', error)
      commit('SET_ERROR', 'Failed to load learning plan')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Generate a new learning plan
  async generateLearningPlan({ commit }) {
    commit('SET_GENERATING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post('/api/learning-plan/generate')
      
      if (response.data.status === 'success') {
        commit('SET_PLAN', response.data.data)
        
        // If modules are included in the response
        if (response.data.data && response.data.data.modules) {
          commit('SET_MODULES', response.data.data.modules)
        }
        
        return response.data
      } else {
        commit('SET_ERROR', 'Failed to generate learning plan')
        return { status: 'error', message: 'Failed to generate learning plan' }
      }
    } catch (error) {
      console.error('Error generating learning plan:', error)
      commit('SET_ERROR', 'Failed to generate learning plan')
      return { status: 'error', message: error.message || 'Failed to generate learning plan' }
    } finally {
      commit('SET_GENERATING', false)
    }
  },
  
  // Fetch modules for the current learning plan
  async fetchModules({ commit, state }) {
    if (!state.plan || !state.plan.id) {
      return
    }
    
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(`/api/learning-plan/${state.plan.id}/modules`)
      
      if (response.data.status === 'success') {
        commit('SET_MODULES', response.data.data)
      } else {
        commit('SET_ERROR', 'Failed to load learning plan modules')
      }
    } catch (error) {
      console.error('Error fetching learning plan modules:', error)
      commit('SET_ERROR', 'Failed to load learning plan modules')
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Start a learning plan module
  async startModule({ commit }, moduleId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(`/api/learning-plan/module/${moduleId}/start`)
      
      if (response.data.status === 'success') {
        commit('UPDATE_MODULE_STATUS', { 
          moduleId, 
          status: 'in_progress' 
        })
        return response.data
      } else {
        commit('SET_ERROR', 'Failed to start module')
        return { status: 'error', message: 'Failed to start module' }
      }
    } catch (error) {
      console.error('Error starting module:', error)
      commit('SET_ERROR', 'Failed to start module')
      return { status: 'error', message: error.message || 'Failed to start module' }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Update module progress
  async updateModuleProgress({ commit }, { moduleId, status, progress }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const data = { status }
      if (progress !== undefined) {
        data.progress_percentage = progress
      }
      
      const response = await axios.post(
        `/api/learning-plan/module/${moduleId}/progress`,
        data
      )
      
      if (response.data.status === 'success') {
        // Update both status and progress if provided
        if (status) {
          commit('UPDATE_MODULE_STATUS', { moduleId, status })
        }
        
        if (progress !== undefined) {
          commit('UPDATE_MODULE_PROGRESS', { moduleId, progress })
        }
        
        return response.data
      } else {
        commit('SET_ERROR', 'Failed to update module progress')
        return { status: 'error', message: 'Failed to update module progress' }
      }
    } catch (error) {
      console.error('Error updating module progress:', error)
      commit('SET_ERROR', 'Failed to update module progress')
      return { status: 'error', message: error.message || 'Failed to update module progress' }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Complete a module
  async completeModule({ commit, dispatch }, moduleId) {
    return dispatch('updateModuleProgress', {
      moduleId,
      status: 'completed',
      progress: 100
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
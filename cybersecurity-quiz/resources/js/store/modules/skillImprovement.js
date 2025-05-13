import axios from 'axios'

// Initial state
const state = {
  skills: [],
  practiceSession: null,
  currentQuestion: null,
  practiceHistory: [],
  dueReviews: [],
  upcomingReviews: [],
  completedReviews: [],
  loading: false,
  practiceLoading: false,
  submitting: false,
  error: null
}

// Getters
const getters = {
  // Get all skills that need improvement
  skills: state => state.skills,
  
  // Get current practice session
  practiceSession: state => state.practiceSession,
  
  // Get current question in the practice session
  currentQuestion: state => state.currentQuestion,
  
  // Get practice history
  practiceHistory: state => state.practiceHistory,
  
  // Get due reviews for spaced repetition
  dueReviews: state => state.dueReviews,
  
  // Get upcoming reviews
  upcomingReviews: state => state.upcomingReviews,
  
  // Get completed reviews
  completedReviews: state => state.completedReviews,
  
  // Get loading state
  loading: state => state.loading,
  
  // Get practice loading state
  practiceLoading: state => state.practiceLoading,
  
  // Get submitting state
  submitting: state => state.submitting,
  
  // Get error state
  error: state => state.error,
  
  // Get skills that need improvement
  improvementSkills: state => {
    return state.skills.filter(skill => skill.needs_improvement)
  },
  
  // Check if there is an active practice session
  hasActivePracticeSession: state => {
    return state.practiceSession !== null
  },
  
  // Get practice session progress
  practiceProgress: state => {
    if (!state.practiceSession) return 0
    
    const total = state.practiceSession.total_questions
    const answered = state.practiceSession.answered_questions.length
    
    if (total === 0) return 0
    return Math.round((answered / total) * 100)
  }
}

// Mutations
const mutations = {
  // Set skills data
  SET_SKILLS(state, skills) {
    state.skills = skills
  },
  
  // Set practice session
  SET_PRACTICE_SESSION(state, session) {
    state.practiceSession = session
  },
  
  // Set current question
  SET_CURRENT_QUESTION(state, question) {
    state.currentQuestion = question
  },
  
  // Set practice history
  SET_PRACTICE_HISTORY(state, history) {
    state.practiceHistory = history
  },
  
  // Set due reviews
  SET_DUE_REVIEWS(state, reviews) {
    state.dueReviews = reviews
  },
  
  // Set upcoming reviews
  SET_UPCOMING_REVIEWS(state, reviews) {
    state.upcomingReviews = reviews
  },
  
  // Set completed reviews
  SET_COMPLETED_REVIEWS(state, reviews) {
    state.completedReviews = reviews
  },
  
  // Add an answered question to the session
  ADD_ANSWERED_QUESTION(state, { questionId, answer, isCorrect }) {
    if (!state.practiceSession) return
    
    state.practiceSession.answered_questions.push({
      question_id: questionId,
      answer,
      is_correct: isCorrect
    })
  },
  
  // Update practice session score
  UPDATE_SESSION_SCORE(state, score) {
    if (!state.practiceSession) return
    state.practiceSession.score = score
  },
  
  // Set loading state
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  // Set practice loading state
  SET_PRACTICE_LOADING(state, loading) {
    state.practiceLoading = loading
  },
  
  // Set submitting state
  SET_SUBMITTING(state, submitting) {
    state.submitting = submitting
  },
  
  // Set error state
  SET_ERROR(state, error) {
    state.error = error
  },
  
  // Clear error state
  CLEAR_ERROR(state) {
    state.error = null
  },
  
  // Reset practice session
  RESET_PRACTICE_SESSION(state) {
    state.practiceSession = null
    state.currentQuestion = null
  }
}

// Actions
const actions = {
  // Fetch skill data
  async fetchSkillData({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/skill-improvement')
      
      if (response.data.status === 'success') {
        commit('SET_SKILLS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load skill data')
        return null
      }
    } catch (error) {
      console.error('Error fetching skill data:', error)
      commit('SET_ERROR', 'Failed to load skill data')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Start a new practice session for a skill
  async startPracticeSession({ commit }, skillId) {
    commit('SET_PRACTICE_LOADING', true)
    commit('CLEAR_ERROR')
    commit('RESET_PRACTICE_SESSION')
    
    try {
      const response = await axios.post(`/api/skill-improvement/${skillId}/practice/start`)
      
      if (response.data.status === 'success') {
        commit('SET_PRACTICE_SESSION', response.data.data.session)
        
        // If first question is included in the response
        if (response.data.data.first_question) {
          commit('SET_CURRENT_QUESTION', response.data.data.first_question)
        }
        
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to start practice session')
        return null
      }
    } catch (error) {
      console.error('Error starting practice session:', error)
      commit('SET_ERROR', 'Failed to start practice session')
      return null
    } finally {
      commit('SET_PRACTICE_LOADING', false)
    }
  },
  
  // Load next question in the practice session
  async loadNextQuestion({ commit, state }) {
    if (!state.practiceSession) {
      commit('SET_ERROR', 'No active practice session')
      return null
    }
    
    commit('SET_PRACTICE_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(
        `/api/skill-improvement/practice/${state.practiceSession.id}/next-question`
      )
      
      if (response.data.status === 'success') {
        if (response.data.data) {
          commit('SET_CURRENT_QUESTION', response.data.data)
        } else {
          // No more questions, set to null
          commit('SET_CURRENT_QUESTION', null)
        }
        
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load next question')
        return null
      }
    } catch (error) {
      console.error('Error loading next question:', error)
      commit('SET_ERROR', 'Failed to load next question')
      return null
    } finally {
      commit('SET_PRACTICE_LOADING', false)
    }
  },
  
  // Submit an answer for the current question
  async submitAnswer({ commit, state, dispatch }, { questionId, answer }) {
    if (!state.practiceSession) {
      commit('SET_ERROR', 'No active practice session')
      return null
    }
    
    commit('SET_SUBMITTING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(
        `/api/skill-improvement/practice/${state.practiceSession.id}/answer`,
        { question_id: questionId, answer }
      )
      
      if (response.data.status === 'success') {
        const result = response.data.data
        
        // Record the answered question
        commit('ADD_ANSWERED_QUESTION', {
          questionId,
          answer,
          isCorrect: result.is_correct
        })
        
        // Update session score if provided
        if (result.session_score !== undefined) {
          commit('UPDATE_SESSION_SCORE', result.session_score)
        }
        
        // Load the next question if there are more
        if (result.has_more_questions) {
          await dispatch('loadNextQuestion')
        } else {
          // Set current question to null if no more questions
          commit('SET_CURRENT_QUESTION', null)
        }
        
        return result
      } else {
        commit('SET_ERROR', 'Failed to submit answer')
        return null
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
      commit('SET_ERROR', 'Failed to submit answer')
      return null
    } finally {
      commit('SET_SUBMITTING', false)
    }
  },
  
  // Complete the current practice session
  async completePracticeSession({ commit, state }) {
    if (!state.practiceSession) {
      commit('SET_ERROR', 'No active practice session')
      return null
    }
    
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(
        `/api/skill-improvement/practice/${state.practiceSession.id}/complete`
      )
      
      if (response.data.status === 'success') {
        // Reset the practice session after completion
        commit('RESET_PRACTICE_SESSION')
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to complete practice session')
        return null
      }
    } catch (error) {
      console.error('Error completing practice session:', error)
      commit('SET_ERROR', 'Failed to complete practice session')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch practice history
  async fetchPracticeHistory({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/skill-improvement/history')
      
      if (response.data.status === 'success') {
        commit('SET_PRACTICE_HISTORY', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load practice history')
        return null
      }
    } catch (error) {
      console.error('Error fetching practice history:', error)
      commit('SET_ERROR', 'Failed to load practice history')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch due spaced repetition reviews
  async fetchDueReviews({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/skill-improvement/spaced-repetition/due')
      
      if (response.data.status === 'success') {
        commit('SET_DUE_REVIEWS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load due reviews')
        return null
      }
    } catch (error) {
      console.error('Error fetching due reviews:', error)
      commit('SET_ERROR', 'Failed to load due reviews')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch upcoming spaced repetition reviews
  async fetchUpcomingReviews({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/skill-improvement/spaced-repetition/upcoming')
      
      if (response.data.status === 'success') {
        commit('SET_UPCOMING_REVIEWS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load upcoming reviews')
        return null
      }
    } catch (error) {
      console.error('Error fetching upcoming reviews:', error)
      commit('SET_ERROR', 'Failed to load upcoming reviews')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Fetch completed spaced repetition reviews
  async fetchCompletedReviews({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get('/api/skill-improvement/spaced-repetition/completed')
      
      if (response.data.status === 'success') {
        commit('SET_COMPLETED_REVIEWS', response.data.data)
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to load completed reviews')
        return null
      }
    } catch (error) {
      console.error('Error fetching completed reviews:', error)
      commit('SET_ERROR', 'Failed to load completed reviews')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Start a spaced repetition review session
  async startReviewSession({ commit }, reviewId) {
    commit('SET_PRACTICE_LOADING', true)
    commit('CLEAR_ERROR')
    commit('RESET_PRACTICE_SESSION')
    
    try {
      const response = await axios.post(
        `/api/skill-improvement/spaced-repetition/${reviewId}/start`
      )
      
      if (response.data.status === 'success') {
        commit('SET_PRACTICE_SESSION', response.data.data.session)
        
        // If first question is included in the response
        if (response.data.data.first_question) {
          commit('SET_CURRENT_QUESTION', response.data.data.first_question)
        }
        
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to start review session')
        return null
      }
    } catch (error) {
      console.error('Error starting review session:', error)
      commit('SET_ERROR', 'Failed to start review session')
      return null
    } finally {
      commit('SET_PRACTICE_LOADING', false)
    }
  },
  
  // Complete a spaced repetition review
  async completeReview({ commit }, { reviewId, performanceRating }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.post(
        `/api/skill-improvement/spaced-repetition/${reviewId}/complete`,
        { performance_rating: performanceRating }
      )
      
      if (response.data.status === 'success') {
        // Refresh due reviews after completion
        dispatch('fetchDueReviews')
        return response.data.data
      } else {
        commit('SET_ERROR', 'Failed to complete review')
        return null
      }
    } catch (error) {
      console.error('Error completing review:', error)
      commit('SET_ERROR', 'Failed to complete review')
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
import axios from 'axios';

const state = {
  quizzes: [],
  currentQuiz: null,
  loading: false,
  error: null
};

const getters = {
  quizzes: state => state.quizzes,
  currentQuiz: state => state.currentQuiz,
  loading: state => state.loading,
  error: state => state.error
};

const actions = {
  async fetchQuizzes({ commit, rootState }) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.get('/api/quizzes', {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      
      commit('SET_QUIZZES', response.data.data);
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch quizzes');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchQuiz({ commit, rootState }, quizId) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.get(`/api/quizzes/${quizId}`, {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      
      commit('SET_CURRENT_QUIZ', response.data);
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch quiz');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async generateQuiz({ commit, rootState }, topicId) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.post('/api/quizzes/generate', { topic_id: topicId }, {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      console.log('✅ Quiz generation response:', response.data);
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to generate quiz');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async submitQuiz({ commit, rootState }, { quizId, responses }) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.post(`/api/quizzes/${quizId}/submit`, { responses }, {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to submit quiz');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  
  SET_ERROR(state, error) {
    state.error = error;
  },
  
  SET_QUIZZES(state, quizzes) {
    state.quizzes = quizzes;
  },
  
  SET_CURRENT_QUIZ(state, quiz) {
    state.currentQuiz = quiz;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
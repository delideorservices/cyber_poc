import axios from 'axios';

const state = {
  results: [],
  currentResult: null,
  loading: false,
  error: null
};

const getters = {
  results: state => state.results,
  currentResult: state => state.currentResult,
  loading: state => state.loading,
  error: state => state.error
};

const actions = {
  async fetchResults({ commit, rootState }) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.get('/api/results', {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      
      commit('SET_RESULTS', response.data.data);
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch results');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchResult({ commit, rootState }, resultId) {
    try {
      commit('SET_LOADING', true);
      
      const response = await axios.get(`/api/results/${resultId}`, {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`
        }
      });
      
      commit('SET_CURRENT_RESULT', response.data);
      return response;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch result');
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
  
  SET_RESULTS(state, results) {
    state.results = results;
  },
  
  SET_CURRENT_RESULT(state, result) {
    state.currentResult = result;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
import axios from 'axios';

const state = {
  user: null,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null
};

const getters = {
  isAuthenticated: state => !!state.token,
  user: state => state.user,
  loading: state => state.loading,
  error: state => state.error
};

const actions = {
  async login({ commit }, credentials) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/api/login', credentials);
      
      const token = response.data.token;
      localStorage.setItem('token', token);
      
      // Set the default Authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      commit('SET_TOKEN', token);
      commit('SET_USER', response.data.user);
      
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Login failed';
      commit('SET_ERROR', errorMessage);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async register({ commit }, userData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await axios.post('/api/register', userData);
      
      const token = response.data.token;
      localStorage.setItem('token', token);
      
      // Set the default Authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      commit('SET_TOKEN', token);
      commit('SET_USER', response.data.user);
      
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Registration failed';
      commit('SET_ERROR', errorMessage);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchUser({ commit, state }) {
    if (!state.token) return;
    
    commit('SET_LOADING', true);
    
    try {
      // Set the header for this specific request
      const response = await axios.get('/api/user', {
        headers: {
          'Authorization': `Bearer ${state.token}`
        }
      });
      
      commit('SET_USER', response.data);
      return response;
    } catch (error) {
      console.error('Fetch user error:', error);
      // If unauthorized, log out
      if (error.response?.status === 401) {
        commit('CLEAR_AUTH');
        localStorage.removeItem('token');
      }
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async updateProfile({ commit, state }, profileData) {
    if (!state.token) return;
    
    commit('SET_LOADING', true);
    
    try {
      const response = await axios.put('/api/profile', profileData, {
        headers: {
          'Authorization': `Bearer ${state.token}`
        }
      });
      
      commit('SET_USER', response.data);
      return response;
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  logout({ commit }) {
    // Clear auth data
    commit('CLEAR_AUTH');
    localStorage.removeItem('token');
    
    // Remove the Authorization header
    delete axios.defaults.headers.common['Authorization'];
  }
};

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  
  SET_ERROR(state, error) {
    state.error = error;
  },
  
  CLEAR_ERROR(state) {
    state.error = null;
  },
  
  SET_TOKEN(state, token) {
    state.token = token;
  },
  
  SET_USER(state, user) {
    state.user = user;
  },
  
  CLEAR_AUTH(state) {
    state.token = null;
    state.user = null;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};

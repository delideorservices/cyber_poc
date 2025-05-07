import axios from 'axios';

const state = {
    topics: [],
    loading: false,
    error: null
};

const getters = {
    topics: state => state.topics,
    loading: state => state.loading,
    error: state => state.error
};

const actions = {
    async fetchTopics({ commit, rootState }, sectorId = null) {
        commit('SET_LOADING', true);
        
        try {
            let url = '/api/topics';
            if (sectorId) {
                url += `?sector_id=${sectorId}`;
            }
            
            const response = await axios.get(url, {
                headers: {
                    'Authorization': `Bearer ${rootState.auth.token}`
                }
            });
            
            commit('SET_TOPICS', response.data);
            return response;
        } catch (error) {
            console.error('Error fetching topics:', error);
            commit('SET_ERROR', error.message || 'Failed to fetch topics');
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
    
    SET_TOPICS(state, topics) {
        state.topics = topics;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

import { createStore } from 'vuex';
import auth from './modules/auth';
import quiz from './modules/quiz';
import result from './modules/result';
import topic from './modules/topic'; 
export default createStore({
  modules: {
    auth,
    quiz,
    result,
    topic
  }
});
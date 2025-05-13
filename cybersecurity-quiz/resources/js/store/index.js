import { createStore } from 'vuex';
import auth from './modules/auth';
import quiz from './modules/quiz';
import result from './modules/result';
import topic from './modules/topic'; 
import learningPlan from './modules/learningPlan'
import analytics from './modules/analytics'
import skillImprovement from './modules/skillImprovement'
import recommendations from './modules/recommendations'
export default createStore({
  modules: {
    auth,
    quiz,
    result,
    topic,
    learningPlan,
    analytics,
    skillImprovement,
    recommendations
  }
});
import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

// Import components
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Dashboard from '../views/Dashboard.vue';
import Profile from '../views/Profile.vue';
import QuizList from '../views/QuizList.vue';
import QuizDetails from '../views/QuizDetails.vue';
import QuizStart from '../views/QuizStart.vue';
import ResultList from '../views/ResultList.vue';
import ResultDetails from '../views/ResultDetails.vue';
import LearningPlanView from '@/views/LearningPlanView.vue'
import AnalyticsView from '@/views/AnalyticsView.vue'
import SkillImprovementView from '@/views/SkillImprovementView.vue'
import SkillPracticeView from '@/views/SkillPracticeView.vue'
import RecommendationsView from '@/views/RecommendationsView.vue'
// import ResourceView from '@/views/ResourceView.vue'
// Create route configuration
const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/quizzes',
    name: 'quizzes',
    component: QuizList,
    meta: { requiresAuth: true }
  },
  {
    path: '/quizzes/:id',
    name: 'quiz-details',
    component: QuizDetails,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/quizzes/:id/start',
    name: 'quiz-start',
    component: QuizStart,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/results',
    name: 'results',
    component: ResultList,
    meta: { requiresAuth: true }
  },
  {
    path: '/results/:id',
    name: 'result-details',
    component: ResultDetails,
    meta: { requiresAuth: true },
    props: true
  },
   {
    path: '/learning-plan',
    name: 'LearningPlan',
    component: LearningPlanView,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: AnalyticsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/skill-improvement',
    name: 'SkillImprovement',
    component: SkillImprovementView,
    meta: { requiresAuth: true }
  },
  {
    path: '/skill-improvement/practice/:id',
    name: 'SkillPractice',
    component: SkillPracticeView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/recommendations',
    name: 'Recommendations',
    component: RecommendationsView,
    meta: { requiresAuth: true }
  }
  // {
  //   path: '/resources/:id',
  //   name: 'Resource',
  //   component: ResourceView,
  //   props: true,
  //   meta: { requiresAuth: true }
  // }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  // Redirect to login if route requires auth and user is not authenticated
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'login' });
  } 
  // Redirect to dashboard if route is for guests only and user is authenticated
  else if (to.matched.some(record => record.meta.guest) && isAuthenticated) {
    next({ name: 'dashboard' });
  } 
  else {
    next();
  }
});

export default router;
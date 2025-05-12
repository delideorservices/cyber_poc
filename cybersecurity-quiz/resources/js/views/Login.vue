<template>
  <div class="login-page">
    <div class="auth-card">
      <div class="card-header">
        <h1>Login</h1>
        <p class="subtitle">Log in to access your cybersecurity quizzes</p>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
      
      <form @submit.prevent="login" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-container">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            <input 
              id="email"
              v-model="email"
              type="email" 
              required
              placeholder="Enter your email"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-container">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input 
              id="password"
              v-model="password"
              type="password" 
              required
              placeholder="Enter your password"
            >
          </div>
          <div class="forgot-password">
            <a href="#">Forgot password?</a>
          </div>
        </div>
        
        <div class="form-group">
          <button type="submit" class="btn-primary" :disabled="loading">
            <span>{{ loading ? 'Logging in...' : 'Login' }}</span>
            <div v-if="loading" class="btn-spinner"></div>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
              <polyline points="10 17 15 12 10 7"></polyline>
              <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
          </button>
        </div>
      </form>
      
      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Register</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      errorMessage: ''
    }
  },
  methods: {
    async login() {
      this.loading = true;
      this.errorMessage = '';
      
      try {
        await this.$store.dispatch('auth/login', {
          email: this.email,
          password: this.password
        });
        
        this.$router.push('/dashboard');
      } catch (error) {
        this.errorMessage = error.response?.data?.message || 'Login failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
/* Professional dark-themed design matching the dashboard */
:root {
  --primary-bg: #f8f9fa;
  --card-bg: #ffffff;
  --text-color: #333333;
  --text-secondary: #6c757d;
  --primary-color: #1a73e8;
  --primary-hover: #1765cc;
  --secondary-color: #5f6368;
  --border-color: #e0e0e0;
  --shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  --border-radius: 8px;
  --input-bg: #f1f3f4;
}

.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--primary-bg);
  font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.card-header {
  padding: 30px 30px 20px;
  text-align: center;
}

.card-header h1 {
  margin: 0 0 10px;
  font-size: 28px;
  font-weight: 500;
  color: var(--text-color);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 15px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 30px 15px;
  padding: 15px;
  background-color: #fce8e6;
  color: #d93025;
  border-radius: var(--border-radius);
  font-size: 14px;
}

.auth-form {
  padding: 0 30px 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-container svg {
  position: absolute;
  left: 12px;
  color: var(--secondary-color);
}

.input-container input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 15px;
  background-color: var(--input-bg);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-container input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
  background-color: white;
}

.forgot-password {
  text-align: right;
  margin-top: 8px;
}

.forgot-password a {
  font-size: 13px;
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}

.btn-primary {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 14px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:active {
  transform: translateY(1px);
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  background-color: var(--secondary-color);
}

.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  padding: 20px 30px;
  text-align: center;
  background-color: #f8f9fa;
  border-top: 1px solid var(--border-color);
}

.auth-footer p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-footer a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .auth-card {
    box-shadow: none;
    border: none;
  }
  
  .card-header,
  .auth-form,
  .auth-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style>
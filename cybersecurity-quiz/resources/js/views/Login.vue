<template>
    <div class="login-page container">
      <div class="card">
        <h1 class="text-center">Login</h1>
        <div v-if="errorMessage" class="alert alert-danger">
          {{ errorMessage }}
        </div>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <input 
              id="email"
              v-model="email"
              type="email" 
              class="form-control" 
              required
              placeholder="Enter your email"
            >
          </div>
          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input 
              id="password"
              v-model="password"
              type="password" 
              class="form-control" 
              required
              placeholder="Enter your password"
            >
          </div>
          <div class="form-group">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </form>
        <div class="text-center mt-4">
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
  .login-page {
    max-width: 500px;
    margin: 2rem auto;
  }
  
  .text-center {
    text-align: center;
  }
  
  .mt-4 {
    margin-top: 1rem;
  }
  
  .alert {
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid transparent;
    border-radius: 0.25rem;
  }
  
  .alert-danger {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
  }
  </style>
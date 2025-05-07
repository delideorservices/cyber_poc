<template>
    <div class="app">
      <nav v-if="isAuthenticated" class="main-nav">
        <div class="container nav-container">
          <div class="nav-logo">
            <router-link to="/" class="logo-link">
              Cybersecurity Quiz
            </router-link>
          </div>
          <div class="nav-links">
            <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/quizzes" class="nav-link">Quizzes</router-link>
            <router-link to="/results" class="nav-link">Results</router-link>
            <router-link to="/profile" class="nav-link">Profile</router-link>
          </div>
          <div class="nav-actions">
            <button @click="logout" class="logout-btn">Logout</button>
          </div>
        </div>
      </nav>
      
      <main>
        <router-view />
      </main>
      
      <footer class="main-footer">
        <div class="container">
          <p>&copy; {{ currentYear }} Cybersecurity Quiz Platform</p>
        </div>
      </footer>
    </div>
  </template>
  
  <script>
  export default {
    name: 'App',
    computed: {
      isAuthenticated() {
        return this.$store.getters['auth/isAuthenticated'];
      },
      currentYear() {
        return new Date().getFullYear();
      }
    },
    methods: {
      async logout() {
        try {
          await this.$store.dispatch('auth/logout');
          this.$router.push('/login');
        } catch (error) {
          console.error('Logout error:', error);
        }
      }
    },
    created() {
      // Check if user is already authenticated
      if (localStorage.getItem('token')) {
        this.$store.dispatch('auth/fetchUser');
      }
    }
  }
  </script>
  
  <style>
  /* Global styles */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: 'Nunito', sans-serif;
    font-size: 16px;
    line-height: 1.5;
    color: #111827;
    background-color: #f3f4f6;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  /* Navigation */
  .main-nav {
    background-color: white;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    padding: 1rem 0;
  }
  
  .nav-container {
    display: flex;
    align-items: center;
  }
  
  .nav-logo {
    margin-right: 2rem;
  }
  
  .logo-link {
    color: #3b82f6;
    font-size: 1.25rem;
    font-weight: 700;
    text-decoration: none;
  }
  
  .nav-links {
    display: flex;
    flex: 1;
    gap: 1.5rem;
  }
  
  .nav-link {
    color: #4b5563;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
  }
  
  .nav-link:hover {
    color: #111827;
  }
  
  .nav-link.router-link-active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
  }
  
  .logout-btn {
    background-color: transparent;
    border: none;
    color: #4b5563;
    font-weight: 500;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
  }
  
  .logout-btn:hover {
    background-color: #f3f4f6;
    color: #111827;
  }
  
  /* Footer */
  .main-footer {
    background-color: white;
    border-top: 1px solid #e5e7eb;
    padding: 1.5rem 0;
    text-align: center;
    margin-top: 4rem;
    color: #6b7280;
    font-size: 0.875rem;
  }
  
  /* Button styles */
  .btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    font-weight: 500;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    transition: all 0.2s ease;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
    border: 1px solid #3b82f6;
  }
  
  .btn-primary:hover {
    background-color: #2563eb;
  }
  
  .btn-secondary {
    background-color: white;
    color: #4b5563;
    border: 1px solid #d1d5db;
  }
  
  .btn-secondary:hover {
    background-color: #f9fafb;
  }
  
  /* Other common styles */
  h1, h2, h3, h4, h5, h6 {
    color: #111827;
    margin-bottom: 1rem;
    line-height: 1.2;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  h3 {
    font-size: 1.25rem;
  }
  
  a {
    color: #3b82f6;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  main {
    min-height: calc(100vh - 140px);
  }
  </style>
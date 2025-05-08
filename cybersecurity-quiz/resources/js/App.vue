<template>
  <div class="app" :class="{ 'dark-mode': darkMode }">
    <nav v-if="isAuthenticated" class="main-nav">
      <div class="container nav-container">
        <div class="nav-logo">
          <router-link to="/" class="logo-link">
            <span class="logo-icon">⚡</span> CyX 3.0
          </router-link>
        </div>
        
        <div class="nav-links" :class="{ 'nav-active': mobileMenuOpen }">
          <router-link to="/dashboard" class="nav-link">
            <i class="nav-icon">📊</i> Dashboard
          </router-link>
          <router-link to="/quizzes" class="nav-link">
            <i class="nav-icon">📝</i> Quizzes
          </router-link>
          <router-link to="/results" class="nav-link">
            <i class="nav-icon">📈</i> Results
          </router-link>
          
          <div class="dropdown">
            <router-link to="/profile" class="nav-link profile-link">
              <div class="avatar">
                <span class="avatar-text">{{ userInitials }}</span>
              </div>
              Profile
            </router-link>
            <div class="dropdown-content">
              <router-link to="/settings" class="dropdown-item">
                <i class="dropdown-icon">⚙️</i> Settings
              </router-link>
              <router-link to="/help" class="dropdown-item">
                <i class="dropdown-icon">❓</i> Help
              </router-link>
              <button @click="logout" class="dropdown-item logout-item">
                <i class="dropdown-icon">🚪</i> Logout
              </button>
            </div>
          </div>
        </div>
        
        <div class="nav-actions">
          <button @click="toggleDarkMode" class="theme-toggle" aria-label="Toggle dark mode">
            <span v-if="darkMode">☀️</span>
            <span v-else>🌙</span>
          </button>
          <button @click="toggleMobileMenu" class="mobile-menu-btn">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </button>
        </div>
      </div>
    </nav>
    
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="main-footer">
      
    </footer>
  </div>
</template>
  <script>
  export default {
    name: 'App',
    data() {
      return {
        darkMode: false,
        mobileMenuOpen: false
      }
    },
    computed: {
      isAuthenticated() {
        return this.$store.getters['auth/isAuthenticated'];
      },
      currentYear() {
        return new Date().getFullYear();
      },
      userInitials() {
        const user = this.$store.state.auth.user || {};
        if (user.firstName && user.lastName) {
          return `${user.firstName[0]}${user.lastName[0]}`;
        }
        return user.email ? user.email[0].toUpperCase() : 'U';
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
      },
      toggleDarkMode() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
      },
      toggleMobileMenu() {
        this.mobileMenuOpen = !this.mobileMenuOpen;
      }
    },
    created() {
      // Check if user is already authenticated
      if (localStorage.getItem('token')) {
        this.$store.dispatch('auth/fetchUser');
      }
      
      // Check dark mode preference
      const savedDarkMode = localStorage.getItem('darkMode');
      if (savedDarkMode !== null) {
        this.darkMode = savedDarkMode === 'true';
      } else {
        // Check system preference
        this.darkMode = window.matchMedia && 
                       window.matchMedia('(prefers-color-scheme: dark)').matches;
      }
    }
  }
  </script>
  
  <style>
:root {
  --primary: #4361ee;
  --primary-light: #4895ef;
  --primary-dark: #3f37c9;
  --secondary: #560bad;
  --success: #06d6a0;
  --warning: #ffd166;
  --danger: #ef476f;
  --light: #f8f9fa;
  --dark: #212529;
  --gray: #6c757d;
  --gray-light: #ced4da;
  --gray-dark: #343a40;
  --background: #ffffff;
  --text-primary: #212529;
  --text-secondary: #6c757d;
  --shadow: rgba(0, 0, 0, 0.1);
  --border: #e9ecef;
  --transition: all 0.3s ease;
  --radius: 0.5rem;
}

.dark-mode {
  --primary: #4cc9f0;
  --primary-light: #4895ef;
  --primary-dark: #3f37c9;
  --background: #121212;
  --text-primary: #f8f9fa;
  --text-secondary: #adb5bd;
  --shadow: rgba(0, 0, 0, 0.3);
  --border: #343a40;
  --gray-light: #495057;
}

/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', 'Nunito', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--background);
  transition: var(--transition);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Navigation */
.main-nav {
  background-color: var(--background);
  box-shadow: 0 4px 12px var(--shadow);
  padding: 0.75rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: var(--transition);
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  color: var(--primary);
  font-size: 1.5rem;
  font-weight: 700;
  text-decoration: none;
  transition: var(--transition);
}

.logo-icon {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.logo-link:hover {
  transform: scale(1.05);
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  transition: var(--transition);
  position: relative;
}

.nav-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.nav-link:hover {
  color: var(--primary);
  background-color: rgba(67, 97, 238, 0.05);
  text-decoration: none;
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  color: var(--primary);
  font-weight: 700;
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  height: 3px;
  width: 20px;
  background: linear-gradient(90deg, var(--primary-light), var(--primary-dark));
  border-radius: 3px;
}

/* Profile and Dropdown */
.profile-link {
  display: flex;
  align-items: center;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-light), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.dropdown {
  position: relative;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--background);
  min-width: 200px;
  box-shadow: 0 8px 16px var(--shadow);
  border-radius: var(--radius);
  padding: 0.75rem 0;
  z-index: 1;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: var(--transition);
}

.dropdown:hover .dropdown-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(5px);
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  color: var(--text-primary);
  text-decoration: none;
  transition: var(--transition);
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 1rem;
  font-family: inherit;
}

.dropdown-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.dropdown-item:hover {
  background-color: rgba(67, 97, 238, 0.05);
  color: var(--primary);
}

.logout-item {
  color: var(--danger);
}

.logout-item:hover {
  background-color: rgba(239, 71, 111, 0.05);
  color: var(--danger);
}

/* Theme Toggle */
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  margin-right: 1rem;
  padding: 0.25rem;
  border-radius: var(--radius);
  transition: var(--transition);
}

.theme-toggle:hover {
  transform: rotate(15deg);
}

/* Mobile Menu */
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 30px;
  height: 30px;
  position: relative;
  z-index: 200;
}

.bar {
  display: block;
  width: 100%;
  height: 3px;
  background-color: var(--text-primary);
  margin: 5px 0;
  transition: var(--transition);
  border-radius: 3px;
}

/* Footer */
.main-footer {
  background-color: var(--background);
  border-top: 1px solid var(--border);
  padding: 2rem 0;
  margin-top: 4rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.footer-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.footer-logo {
  display: flex;
  align-items: center;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--primary);
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition);
}

.footer-link:hover {
  color: var(--primary);
  text-decoration: none;
}

.copyright {
  color: var(--text-secondary);
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Button styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: var(--transition);
  border: none;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  color: white;
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.2);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(67, 97, 238, 0.3);
}

.btn-secondary {
  background-color: var(--background);
  color: var(--text-primary);
  border: 1px solid var(--border);
  box-shadow: 0 2px 6px var(--shadow);
}

.btn-secondary:hover {
  background-color: var(--light);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow);
}

.btn-icon {
  margin-right: 0.5rem;
}

/* Responsive styles */
@media (max-width: 768px) {
  .nav-links {
    position: fixed;
    top: 0;
    right: -280px;
    width: 280px;
    height: 100vh;
    background-color: var(--background);
    box-shadow: -5px 0 15px var(--shadow);
    flex-direction: column;
    align-items: flex-start;
    padding: 6rem 2rem 2rem;
    transition: right 0.3s ease;
    z-index: 100;
  }
  
  .nav-links.nav-active {
    right: 0;
  }
  
  .nav-link {
    width: 100%;
    padding: 1rem 0;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .nav-active .bar:nth-child(1) {
    transform: rotate(-45deg) translate(-5px, 6px);
  }
  
  .nav-active .bar:nth-child(2) {
    opacity: 0;
  }
  
  .nav-active .bar:nth-child(3) {
    transform: rotate(45deg) translate(-5px, -6px);
  }
  
  .dropdown-content {
    position: static;
    box-shadow: none;
    opacity: 1;
    visibility: visible;
    transform: none;
    padding: 0;
    width: 100%;
  }
  
  .dropdown-item {
    padding: 0.75rem 1rem;
  }
  
  .footer-container {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
}
</style>

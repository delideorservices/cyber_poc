<template>
  <div class="skill-practice-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <span>Loading practice session...</span>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="error-card">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <h2>Something went wrong</h2>
      <p>{{ error }}</p>
      <button class="btn-primary" @click="$router.push('/skill-improvement')">
        Back to Skill Improvement
      </button>
    </div>
    
    <!-- Introduction Screen -->
    <div v-else-if="!sessionStarted" class="intro-card">
      <h1>Practice: {{ skillName }}</h1>
      <div class="practice-info">
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="info-content">
            <div class="info-label">Duration</div>
            <div class="info-value">Approximately {{ practiceInfo.estimated_minutes }} minutes</div>
          </div>
        </div>
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h13l4-3.5L18 6z"></path>
              <path d="M12 13v9"></path>
              <path d="M12 2v4"></path>
            </svg>
          </div>
          <div class="info-content">
            <div class="info-label">Difficulty</div>
            <div class="info-value">{{ formatDifficulty(practiceInfo.difficulty_level) }}</div>
          </div>
        </div>
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
          </div>
          <div class="info-content">
            <div class="info-label">Questions</div>
            <div class="info-value">{{ practiceInfo.total_questions }} questions</div>
          </div>
        </div>
      </div>
      
      <div class="intro-description">
        <p>This practice session is designed to help you improve your skills in {{ skillName }}. 
           The questions are tailored to your current proficiency level.</p>
        <p>As you progress, the difficulty will adjust based on your performance. 
           Remember, this is practice - take your time and learn from each question.</p>
      </div>
      
      <div class="intro-actions">
        <button class="btn-primary" @click="startSession">Start Practice</button>
        <button class="btn-secondary" @click="$router.push('/skill-improvement')">
          Back to Skill Improvement
        </button>
      </div>
    </div>
    
    <!-- Practice Session -->
    <div v-else-if="sessionStarted && !sessionCompleted" class="practice-container">
      <div class="practice-header">
        <div>
          <h1>Practice: {{ skillName }}</h1>
          <div class="practice-progress">
            Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
          </div>
        </div>
        <div class="session-timer">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span>{{ formatTime(sessionTime) }}</span>
        </div>
      </div>
      
      <div class="progress-bar-container">
        <div class="progress-dots">
          <div v-for="(question, index) in questions" :key="index" 
               class="progress-dot" 
               :class="getProgressDotClass(index)">
          </div>
        </div>
      </div>
      
      <div class="question-card">
        <div class="question-content">
          <div class="question-text">{{ currentQuestion.text }}</div>
          
          <!-- Multiple Choice Question -->
          <div v-if="currentQuestion.type === 'multiple_choice'" class="question-options">
            <div v-for="(option, index) in currentQuestion.options" :key="index" 
                 class="option-item" 
                 :class="{ 'selected': userResponses[currentQuestionIndex] === option.value }"
                 @click="selectOption(option.value)">
              <div class="option-marker">{{ ['A', 'B', 'C', 'D', 'E'][index] }}</div>
              <div class="option-text">{{ option.text }}</div>
            </div>
          </div>
          
          <!-- True/False Question -->
          <div v-else-if="currentQuestion.type === 'true_false'" class="question-options true-false">
            <div class="option-item" 
                 :class="{ 'selected': userResponses[currentQuestionIndex] === true }"
                 @click="selectOption(true)">
              <div class="option-marker">A</div>
              <div class="option-text">True</div>
            </div>
            <div class="option-item" 
                 :class="{ 'selected': userResponses[currentQuestionIndex] === false }"
                 @click="selectOption(false)">
              <div class="option-marker">B</div>
              <div class="option-text">False</div>
            </div>
          </div>
          
          <!-- Fill in the Blank Question -->
          <div v-else-if="currentQuestion.type === 'fill_blank'" class="question-fill-blank">
            <input type="text" class="fill-blank-input" 
                   v-model="userResponses[currentQuestionIndex]" 
                   placeholder="Type your answer here...">
          </div>
          
          <!-- Default Question View -->
          <div v-else class="question-default">
            <p>Unsupported question type.</p>
          </div>
        </div>
        
        <div v-if="showHint" class="question-hint">
          <div class="hint-header">
            <div class="hint-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 16v.01"></path>
                <path d="M12 8a2.5 2.5 0 0 1 0 5"></path>
              </svg>
            </div>
            <span>Hint</span>
          </div>
          <div class="hint-text">{{ currentQuestion.hint }}</div>
        </div>
        
        <div class="question-actions">
          <button v-if="currentQuestion.hint && !showHint" 
                class="btn-text" 
                @click="showHint = true">
            Show Hint
          </button>
          
          <div class="navigation-buttons">
            <button v-if="currentQuestionIndex > 0" 
                  class="btn-secondary" 
                  @click="previousQuestion">
              Previous
            </button>
            
            <button v-if="currentQuestionIndex < questions.length - 1" 
                  class="btn-primary" 
                  @click="nextQuestion" 
                  :disabled="!hasCurrentResponse">
              Next
            </button>
            
            <button v-else 
                  class="btn-primary" 
                  @click="submitSession" 
                  :disabled="!hasCurrentResponse || submitting">
              {{ submitting ? 'Submitting...' : 'Submit' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Results Screen -->
    <div v-else-if="sessionCompleted" class="results-container">
      <div class="results-header">
        <h1>Practice Completed</h1>
      </div>
      
      <div class="results-card">
        <div class="score-display">
          <div class="score-circle" :class="getScoreClass(sessionResults.score)">
            <div class="score-value">{{ sessionResults.score }}%</div>
          </div>
          <div class="score-label">Your Score</div>
        </div>
        
        <div class="results-stats">
          <div class="stats-item">
            <div class="stats-value">{{ sessionResults.correct_answers }}/{{ sessionResults.total_questions }}</div>
            <div class="stats-label">Correct Answers</div>
          </div>
          <div class="stats-item">
            <div class="stats-value">{{ formatTime(sessionResults.time_taken) }}</div>
            <div class="stats-label">Time Taken</div>
          </div>
          <div class="stats-item">
            <div class="stats-value">{{ formatDifficulty(sessionResults.difficulty_level) }}</div>
            <div class="stats-label">Difficulty</div>
          </div>
        </div>
        
        <div class="results-feedback">
          <h3>Feedback</h3>
          <p>{{ sessionResults.feedback }}</p>
        </div>
        
        <div class="next-steps">
          <h3>Next Steps</h3>
          <div class="next-steps-options">
            <button class="btn-primary" @click="startNewSession">
              Practice Again
            </button>
            <button class="btn-secondary" @click="$router.push('/skill-improvement')">
              Back to Skill Improvement
            </button>
            <button class="btn-outline" @click="$router.push('/analytics')">
              View Analytics
            </button>
          </div>
        </div>
      </div>
      
      <div class="questions-review">
        <h2>Question Review</h2>
        <div class="review-list">
          <div v-for="(question, index) in questions" :key="index" class="review-item">
            <div class="review-header">
              <div class="review-number">Question {{ index + 1 }}</div>
              <div class="review-status" :class="questionReviewClass(index)">
                {{ questionReviewStatus(index) }}
              </div>
            </div>
            <div class="review-question">{{ question.text }}</div>
            <div class="review-answer">
              <div class="answer-label">Your Answer:</div>
              <div class="user-answer" :class="{ 'incorrect': !isCorrect(index) }">
                {{ formatAnswer(userResponses[index], question) }}
              </div>
            </div>
            <div v-if="!isCorrect(index)" class="review-correct">
              <div class="answer-label">Correct Answer:</div>
              <div class="correct-answer">{{ formatAnswer(question.correct_answer, question) }}</div>
            </div>
            <div class="review-explanation" v-if="question.explanation">
              <div class="explanation-label">Explanation:</div>
              <div class="explanation-text">{{ question.explanation }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'SkillPracticeView',
  data() {
    return {
      skillId: null,
      sessionStarted: false,
      sessionCompleted: false,
      loading: true,
      error: null,
      practiceInfo: {},
      questions: [],
      userResponses: [],
      currentQuestionIndex: 0,
      showHint: false,
      sessionTime: 0,
      timer: null,
      sessionResults: null,
      submitting: false
    }
  },
  computed: {
    ...mapGetters({
      skillsData: 'skillImprovement/skills'
    }),
    skillName() {
      if (this.practiceInfo && this.practiceInfo.skill_name) {
        return this.practiceInfo.skill_name
      }
      
      if (this.skillId && this.skillsData) {
        const skill = this.skillsData.find(s => s.id === this.skillId)
        return skill ? skill.name : 'Skill'
      }
      
      return 'Skill'
    },
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {}
    },
    hasCurrentResponse() {
      const response = this.userResponses[this.currentQuestionIndex]
      return response !== undefined && response !== null && response !== ''
    }
  },
  created() {
    // Get skill ID from route
    this.skillId = parseInt(this.$route.params.skillId)
    
    if (!this.skillId) {
      this.error = 'Invalid skill ID. Please select a valid skill to practice.'
      this.loading = false
      return
    }
    
    this.initializePractice()
  },
  beforeDestroy() {
    // Clear timer when component is destroyed
    this.stopTimer()
  },
  methods: {
    ...mapActions({
      fetchPracticeSession: 'skillImprovement/fetchPracticeSession',
      submitPracticeSession: 'skillImprovement/submitPracticeSession'
    }),
    async initializePractice() {
      this.loading = true
      this.error = null
      
      try {
        const response = await this.fetchPracticeSession(this.skillId)
        
        this.practiceInfo = {
          skill_name: response.skill_name,
          skill_id: response.skill_id,
          session_id: response.session_id,
          difficulty_level: response.difficulty_level,
          total_questions: response.questions.length,
          estimated_minutes: Math.ceil(response.questions.length * 1.5) // Estimate 1.5 minutes per question
        }
        
        this.questions = response.questions
        
        // Initialize responses array
        this.userResponses = new Array(this.questions.length).fill(null)
        
        this.loading = false
      } catch (error) {
        console.error('Error fetching practice session:', error)
        this.error = 'Failed to load practice session. Please try again later.'
        this.loading = false
      }
    },
    startSession() {
      this.sessionStarted = true
      this.currentQuestionIndex = 0
      this.startTimer()
    },
    startTimer() {
      this.sessionTime = 0
      this.timer = setInterval(() => {
        this.sessionTime++
      }, 1000)
    },
    stopTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    selectOption(value) {
      this.userResponses[this.currentQuestionIndex] = value
    },
    nextQuestion() {
      // Save answer and move to next question
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
        this.showHint = false
      }
    },
    previousQuestion() {
      // Move to previous question
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        this.showHint = false
      }
    },
    async submitSession() {
      // Make sure all questions have responses
      const unanswered = this.userResponses.findIndex(r => r === null || r === undefined || r === '')
      
      if (unanswered >= 0) {
        const confirmation = confirm(`Question ${unanswered + 1} is unanswered. Submit anyway?`)
        if (!confirmation) return
      }
      
      this.submitting = true
      this.stopTimer()
      
      try {
        const results = await this.submitPracticeSession({
          session_id: this.practiceInfo.session_id,
          skill_id: this.skillId,
          responses: this.userResponses,
          time_taken: this.sessionTime
        })
        
        // Set results and show results screen
        this.sessionResults = {
          score: results.score,
          correct_answers: results.correct_answers,
          total_questions: results.total_questions,
          time_taken: this.sessionTime,
          difficulty_level: results.difficulty_level,
          feedback: results.feedback || this.generateFeedback(results.score)
        }
        
        this.sessionCompleted = true
        this.submitting = false
      } catch (error) {
        console.error('Error submitting practice session:', error)
        alert('Failed to submit practice session. Please try again.')
        this.submitting = false
        
        // Restart timer if submission failed
        this.startTimer()
      }
    },
    startNewSession() {
      // Reset data and start a new session
      this.sessionStarted = false
      this.sessionCompleted = false
      this.loading = true
      this.userResponses = []
      this.currentQuestionIndex = 0
      this.sessionTime = 0
      this.sessionResults = null
      this.showHint = false
      
      this.initializePractice()
    },
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`
    },
    formatDifficulty(level) {
      const levels = {
        1: 'Beginner',
        2: 'Easy',
        3: 'Intermediate',
        4: 'Advanced',
        5: 'Expert'
      }
      return levels[level] || level
    },
    getProgressDotClass(index) {
      if (index === this.currentQuestionIndex) return 'current'
      if (this.userResponses[index] !== null && this.userResponses[index] !== undefined && this.userResponses[index] !== '') return 'answered'
      return ''
    },
    getScoreClass(score) {
      if (score >= 80) return 'excellent'
      if (score >= 60) return 'good'
      if (score >= 40) return 'average'
      return 'needs-improvement'
    },
    generateFeedback(score) {
      if (score >= 90) return 'Excellent work! You demonstrate a strong understanding of this skill.'
      if (score >= 80) return 'Great job! You have a good grasp of this skill with minor areas for improvement.'
      if (score >= 70) return 'Good progress! Continue practicing to strengthen your understanding in certain areas.'
      if (score >= 60) return 'You\'re on the right track. Regular practice will help reinforce these concepts.'
      if (score >= 50) return 'You have a basic understanding but need more practice with these concepts.'
      return 'This topic needs more focused study. Consider reviewing the fundamentals before trying again.'
    },
    isCorrect(index) {
      const question = this.questions[index]
      if (!question) return false
      
      const userAnswer = this.userResponses[index]
      const correctAnswer = question.correct_answer
      
      // Handle different question types
      if (question.type === 'true_false') {
        return userAnswer === correctAnswer
      }
      
      if (question.type === 'fill_blank' && typeof userAnswer === 'string' && typeof correctAnswer === 'string') {
        return userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim()
      }
      
      return userAnswer === correctAnswer
    },
    questionReviewClass(index) {
      return this.isCorrect(index) ? 'correct' : 'incorrect'
    },
    questionReviewStatus(index) {
      return this.isCorrect(index) ? 'Correct' : 'Incorrect'
    },
    formatAnswer(answer, question) {
      if (answer === null || answer === undefined) return 'Not answered'
      
      if (question.type === 'multiple_choice') {
        const option = question.options.find(opt => opt.value === answer)
        return option ? option.text : answer
      }
      
      if (question.type === 'true_false') {
        return answer === true ? 'True' : 'False'
      }
      
      return answer
    }
  }
}
</script>
<style scoped>
.skill-practice-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

/* Loading State */
.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(26, 115, 232, 0.1);
  border-radius: 50%;
  border-top-color: #1a73e8;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error State */
.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.error-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #fce8e6;
  margin-bottom: 24px;
  color: #ea4335;
}

.error-card h2 {
  font-size: 20px;
  margin: 0 0 10px;
  font-weight: 500;
  color: #ea4335;
}

.error-card p {
  margin: 0 0 24px;
  color: #5f6368;
  max-width: 400px;
}

/* Introduction Screen */
.intro-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 30px;
}

.intro-card h1 {
  font-size: 24px;
  margin: 0 0 20px;
  color: #333;
  font-weight: 500;
}

.practice-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  flex: 1;
  min-width: 200px;
}

.info-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e8f0fe;
  margin-right: 12px;
  color: #1a73e8;
}

.info-label {
  font-size: 14px;
  color: #5f6368;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 500;
  color: #333;
}

.intro-description {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.intro-description p {
  margin: 0 0 10px;
  color: #5f6368;
  line-height: 1.5;
}

.intro-description p:last-child {
  margin-bottom: 0;
}

.intro-actions {
  display: flex;
  gap: 15px;
}

/* Practice Session */
.practice-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.practice-header h1 {
  font-size: 24px;
  margin: 0 0 5px;
  color: #333;
  font-weight: 500;
}

.practice-progress {
  font-size: 14px;
  color: #5f6368;
}

.session-timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #5f6368;
  background-color: #f1f3f4;
  padding: 8px 12px;
  border-radius: 20px;
}

.progress-bar-container {
  margin-bottom: 10px;
}

.progress-dots {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 0;
}

.progress-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #e0e0e0;
  flex-shrink: 0;
}

.progress-dot.answered {
  background-color: #1a73e8;
}

.progress-dot.current {
  background-color: #fbbc04;
  transform: scale(1.2);
}

.question-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 25px;
}

.question-content {
  margin-bottom: 30px;
}

.question-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.5;
}

/* Multiple Choice & True/False Questions */
.question-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-item:hover {
  background-color: #f8f9fa;
}

.option-item.selected {
  background-color: #e8f0fe;
  border-color: #1a73e8;
}

.option-marker {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
  background-color: #f1f3f4;
  border-radius: 50%;
  margin-right: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.option-item.selected .option-marker {
  background-color: #1a73e8;
  color: white;
}

.option-text {
  flex: 1;
}

/* Fill in the Blank Questions */
.question-fill-blank {
  padding: 10px 0;
}

.fill-blank-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s ease;
}

.fill-blank-input:focus {
  border-color: #1a73e8;
}

/* Hint */
.question-hint {
  background-color: #f0f4f8;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.hint-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 500;
  color: #1a73e8;
}

.hint-icon {
  color: #1a73e8;
}

.hint-text {
  color: #5f6368;
  line-height: 1.5;
}

.question-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-text {
  background: none;
  border: none;
  color: #1a73e8;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 0;
}

.btn-text:hover {
  text-decoration: underline;
}

.navigation-buttons {
  display: flex;
  gap: 10px;
}

/* Results Screen */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.results-header h1 {
  font-size: 24px;
  margin: 0;
  color: #333;
  font-weight: 500;
}

.results-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 30px;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.score-circle {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-bottom: 10px;
}

.score-circle.excellent {
  background-color: #e6f4ea;
  color: #34a853;
}

.score-circle.good {
  background-color: #e8f0fe;
  color: #1a73e8;
}

.score-circle.average {
  background-color: #fef7e0;
  color: #f9ab00;
}

.score-circle.needs-improvement {
  background-color: #fce8e6;
  color: #ea4335;
}

.score-value {
  font-size: 36px;
  font-weight: 700;
}

.score-label {
  font-size: 16px;
  color: #5f6368;
}

.results-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.stats-item {
  text-align: center;
}

.stats-value {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #5f6368;
}

.results-feedback, .next-steps {
  margin-bottom: 30px;
}

.results-feedback h3, .next-steps h3 {
  font-size: 18px;
  margin: 0 0 10px;
  color: #333;
  font-weight: 500;
}

.results-feedback p {
  color: #5f6368;
  line-height: 1.5;
}

.next-steps-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.questions-review h2 {
  font-size: 20px;
  margin: 0 0 20px;
  color: #333;
  font-weight: 500;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.review-number {
  font-weight: 500;
  color: #333;
}

.review-status {
  font-size: 14px;
  font-weight: 500;
  padding: 4px 12px;
  border-radius: 16px;
}

.review-status.correct {
  background-color: #e6f4ea;
  color: #34a853;
}

.review-status.incorrect {
  background-color: #fce8e6;
  color: #ea4335;
}

.review-question {
  font-size: 16px;
  color: #333;
  margin-bottom: 15px;
  line-height: 1.5;
}

.review-answer, .review-correct {
  display: flex;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 5px;
}

.answer-label, .explanation-label {
  font-weight: 500;
  color: #5f6368;
  margin-right: 10px;
}

.user-answer.incorrect {
  color: #ea4335;
}

.correct-answer {
  color: #34a853;
  font-weight: 500;
}

.review-explanation {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
}

.explanation-text {
  color: #5f6368;
  line-height: 1.5;
}

/* Buttons */
.btn-primary {
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #1765cc;
}

.btn-primary:disabled {
  background-color: #dadce0;
  color: #5f6368;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f1f3f4;
  color: #5f6368;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #e8eaed;
}

.btn-outline {
  background-color: transparent;
  color: #1a73e8;
  border: 1px solid #1a73e8;
  border-radius: 4px;
  padding: 9px 15px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-outline:hover {
  background-color: rgba(26, 115, 232, 0.04);
}

@media (max-width: 768px) {
  .practice-header, .question-actions, .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .session-timer {
    align-self: flex-start;
  }
  
  .navigation-buttons {
    align-self: flex-end;
  }
  
  .info-item {
    min-width: 100%;
  }
  
  .results-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .next-steps-options {
    flex-direction: column;
  }
}
</style>
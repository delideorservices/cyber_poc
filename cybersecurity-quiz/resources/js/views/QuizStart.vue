<template>
  <div class="quiz-container">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading your quiz...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="fetchQuiz" class="btn btn-retry">Try Again</button>
    </div>
    
    <div v-else class="quiz-content">
      <!-- Quiz header -->
      <div class="quiz-header">
        <h1>{{ quiz.title }}</h1>
        <p class="quiz-description">{{ quiz.description }}</p>
        
        <div class="progress-container">
          <div class="progress-stats">
            <span class="progress-score" :class="{ 'score-updated': scoreUpdated }">Score: {{ currentScore }}/{{ totalPoints }}</span>
            <span class="progress-text">Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress" :style="{ width: `${progressPercentage}%` }"></div>
          </div>
        </div>
      </div>
      
      <!-- Current chapter and question -->
      <div v-if="currentChapter && currentQuestion" class="question-panel">
        <div class="chapter-tag">{{ currentChapter.title }}</div>
        
        <div class="question">
          <p>{{ currentQuestion.content }}</p>
          
          <!-- MCQ Questions -->
          <div v-if="currentQuestion.type === 'mcq'" class="options">
            <div 
              v-for="(option, index) in currentQuestion.options" 
              :key="index"
              class="option"
              :class="{
                'selected': selectedOptions[currentQuestion.id] === index,
                'correct': showFeedback && selectedOptions[currentQuestion.id] === index && isCorrectMcq(index),
                'incorrect': showFeedback && selectedOptions[currentQuestion.id] === index && !isCorrectMcq(index),
                'correct-answer': showFeedback && !isCorrectMcq(selectedOptions[currentQuestion.id]) && isCorrectMcq(index)
              }"
              @click="selectMcqOption(index)"
            >
              <div class="option-marker">
                <div class="option-radio"></div>
              </div>
              <span>{{ option }}</span>
              <div v-if="showFeedback && selectedOptions[currentQuestion.id] === index" class="feedback-icon">
                <span v-if="isCorrectMcq(index)">✓</span>
                <span v-else>✗</span>
              </div>
            </div>
          </div>
          
          <!-- True/False Questions -->
          <div v-else-if="currentQuestion.type === 'true_false'" class="options">
            <div 
              v-for="(option, index) in ['True', 'False']" 
              :key="option"
              class="option"
              :class="{
                'selected': selectedOptions[currentQuestion.id] === option,
                'correct': showFeedback && selectedOptions[currentQuestion.id] === option && isCorrectTrueFalse(option),
                'incorrect': showFeedback && selectedOptions[currentQuestion.id] === option && !isCorrectTrueFalse(option),
                'correct-answer': showFeedback && !isCorrectTrueFalse(selectedOptions[currentQuestion.id]) && isCorrectTrueFalse(option)
              }"
              @click="selectTrueFalseOption(option)"
            >
              <div class="option-marker">
                <div class="option-radio"></div>
              </div>
              <span>{{ option }}</span>
              <div v-if="showFeedback && selectedOptions[currentQuestion.id] === option" class="feedback-icon">
                <span v-if="isCorrectTrueFalse(option)">✓</span>
                <span v-else>✗</span>
              </div>
            </div>
          </div>
          
          <!-- Fill in the blank -->
          <div v-else-if="currentQuestion.type === 'fill_blank'" class="fill-blank">
            <input 
              type="text"
              v-model="fillBlankText"
              @input="selectFillBlankOption"
              @keydown.enter="checkFillBlankAnswer"
              placeholder="Your answer..."
              :class="{
                'correct-input': showFeedback && isCorrectFillBlank(),
                'incorrect-input': showFeedback && !isCorrectFillBlank()
              }"
              :disabled="showFeedback"
            >
            <button 
              class="btn btn-check"
              @click="checkFillBlankAnswer"
              v-if="fillBlankText && !showFeedback"
            >
              Check Answer
            </button>
            <div v-if="showFeedback" class="fill-blank-feedback">
              <div v-if="isCorrectFillBlank()" class="feedback correct-feedback">
                <span class="feedback-icon">✓</span> Correct!
              </div>
              <div v-else class="feedback incorrect-feedback">
                <span class="feedback-icon">✗</span> Incorrect! 
                <span class="correct-answer">Correct answer: {{ getCorrectAnswer() }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Navigation buttons -->
        <div class="navigation">
          <button 
            v-if="!isFirstQuestion" 
            @click="prevQuestion" 
            class="btn btn-prev"
          >
            <span class="btn-icon">←</span> Previous
          </button>
          <div v-else></div>
          
          <button 
            v-if="!showFeedback && !isCurrentQuestionAnswered"
            class="btn btn-disabled"
            disabled
          >
            Answer to continue
          </button>
          <button 
            v-else-if="!showFeedback && isCurrentQuestionAnswered"
            @click="showAnswerFeedback"
            class="btn btn-check-answer"
          >
            Check Answer
          </button>
          <button 
            v-else-if="!isLastQuestion" 
            @click="nextQuestion" 
            class="btn btn-next"
          >
            Next <span class="btn-icon">→</span>
          </button>
          <button 
            v-else-if="isLastQuestion" 
            @click="confirmSubmit" 
            class="btn btn-submit"
          >
            {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Result Popup with Flip Card for Analysis -->
    <div v-if="showResultPopup" class="result-popup-overlay" @click.self="closeResultPopup">
      <div class="result-popup" :class="isCurrentAnswerCorrect ? 'correct-popup' : 'incorrect-popup'">
        <div class="flip-card" :class="{ 'flipped': showExplanation }">
          <div class="flip-card-inner">
            <!-- Front side of card (result) -->
            <div class="flip-card-front">
              <div class="result-icon">{{ isCurrentAnswerCorrect ? '✓' : '✗' }}</div>
              <h3>{{ isCurrentAnswerCorrect ? 'Correct!' : 'Incorrect!' }}</h3>
              <p v-if="!isCurrentAnswerCorrect" class="correct-answer-text">
                Correct answer: {{ getCorrectAnswer() }}
              </p>
              <button @click="toggleExplanation" class="btn btn-analysis">Analysis</button>
              <button @click="closeResultPopup" class="btn btn-continue">Continue</button>
            </div>
            
            <!-- Back side of card (explanation) -->
            <div class="flip-card-back">
              <h3>Explanation</h3>
              <div class="explanation-content">
                <p>{{ currentQuestion.explanation || "No explanation available for this question." }}</p>
              </div>
              <button @click="toggleExplanation" class="btn btn-back">Back</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-content">
        <h2>Submit Quiz?</h2>
        <p>You've answered {{ Object.keys(selectedOptions).length }} of {{ totalQuestions }} questions.</p>
        <p>Your current score: {{ currentScore }} / {{ totalPoints }}</p>
        <p>Are you sure you want to submit your quiz?</p>
        <div class="modal-buttons">
          <button @click="showConfirmModal = false" class="btn btn-cancel">Cancel</button>
          <button @click="submitQuiz" class="btn btn-confirm">Submit Quiz</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizStart',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      quiz: null,
      currentChapterIndex: 0,
      currentQuestionIndex: 0,
      selectedOptions: {},
      fillBlankText: '',
      submitting: false,
      showFeedback: false,
      showConfirmModal: false,
      currentScore: 0,
      totalPoints: 0,
      // New properties for result popup
      showResultPopup: false,
      isCurrentAnswerCorrect: false,
      showExplanation: false,
      scoreUpdated: false
    }
  },
  computed: {
    currentChapter() {
      if (!this.quiz || !this.quiz.chapters) return null;
      return this.quiz.chapters[this.currentChapterIndex];
    },
    currentQuestion() {
      if (!this.currentChapter || !this.currentChapter.questions) return null;
      return this.currentChapter.questions[this.currentQuestionIndex];
    },
    totalQuestions() {
      if (!this.quiz || !this.quiz.chapters) return 0;
      
      let count = 0;
      this.quiz.chapters.forEach(chapter => {
        if (chapter.questions) {
          count += chapter.questions.length;
        }
      });
      
      return count;
    },
    progressPercentage() {
      if (this.totalQuestions === 0) return 0;
      return Math.round(((this.getOverallQuestionIndex() + 1) / this.totalQuestions) * 100);
    },
    isFirstQuestion() {
      return this.currentChapterIndex === 0 && this.currentQuestionIndex === 0;
    },
    isLastQuestion() {
      if (!this.quiz || !this.quiz.chapters) return false;
      
      const lastChapterIndex = this.quiz.chapters.length - 1;
      const lastChapter = this.quiz.chapters[lastChapterIndex];
      if (!lastChapter || !lastChapter.questions) return false;
      
      const lastQuestionIndex = lastChapter.questions.length - 1;
      
      return this.currentChapterIndex === lastChapterIndex && 
             this.currentQuestionIndex === lastQuestionIndex;
    },
    isCurrentQuestionAnswered() {
      return this.currentQuestion && 
             this.currentQuestion.id in this.selectedOptions;
    },
    formattedResponses() {
      let responses = [];
      
      for (const questionId in this.selectedOptions) {
        responses.push({
          question_id: parseInt(questionId),
          answer: this.selectedOptions[questionId]
        });
      }
      
      return responses;
    }
  },
  created() {
    this.fetchQuiz();
  },
  methods: {
    async fetchQuiz() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await this.$store.dispatch('quiz/fetchQuiz', this.id);
        this.quiz = response.data;
        console.log("Quiz loaded:", this.quiz);
        
        // Calculate total points
        this.totalPoints = 0;
        if (this.quiz && this.quiz.chapters) {
          this.quiz.chapters.forEach(chapter => {
            if (chapter.questions) {
              chapter.questions.forEach(question => {
                this.totalPoints += question.points || 1;
              });
            }
          });
        }
        
        this.loading = false;
      } catch (error) {
        console.error("Error fetching quiz:", error);
        this.error = "Failed to load quiz. Please try again.";
        this.loading = false;
      }
    },
    
    getOverallQuestionIndex() {
      if (!this.quiz || !this.quiz.chapters) return 0;
      
      let index = 0;
      for (let i = 0; i < this.currentChapterIndex; i++) {
        if (this.quiz.chapters[i] && this.quiz.chapters[i].questions) {
          index += this.quiz.chapters[i].questions.length;
        }
      }
      
      index += this.currentQuestionIndex;
      return index;
    },
    
    selectMcqOption(index) {
      if (this.showFeedback) return;
      
      console.log("MCQ option selected:", index);
      if (this.currentQuestion) {
        this.selectedOptions[this.currentQuestion.id] = index;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    selectTrueFalseOption(value) {
      if (this.showFeedback) return;
      
      console.log("True/False option selected:", value);
      if (this.currentQuestion) {
        this.selectedOptions[this.currentQuestion.id] = value;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    selectFillBlankOption() {
      if (this.showFeedback) return;
      
      console.log("Fill in blank text:", this.fillBlankText);
      if (this.currentQuestion && this.fillBlankText.trim() !== '') {
        this.selectedOptions[this.currentQuestion.id] = this.fillBlankText;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    checkFillBlankAnswer() {
      if (this.currentQuestion && this.fillBlankText.trim() !== '') {
        this.selectedOptions[this.currentQuestion.id] = this.fillBlankText;
        this.showAnswerFeedback();
      }
    },
    
    isCorrectMcq(index) {
      if (!this.currentQuestion || !this.currentQuestion.correct_answer) return false;
      
      // Handle different formats of correct_answer (index as string or actual option value)
      const correctAnswer = this.currentQuestion.correct_answer;
      
      if (typeof correctAnswer === 'number' || !isNaN(parseInt(correctAnswer))) {
        return parseInt(correctAnswer) === index;
      } else if (correctAnswer && this.currentQuestion.options) {
        return this.currentQuestion.options[index] === correctAnswer;
      }
      
      return false;
    },
    
    isCorrectTrueFalse(value) {
      if (!this.currentQuestion || !this.currentQuestion.correct_answer) return false;
      
      const correctAnswer = this.currentQuestion.correct_answer;
      return correctAnswer === value || correctAnswer === value.toLowerCase();
    },
    
    isCorrectFillBlank() {
      if (!this.currentQuestion || !this.currentQuestion.correct_answer || !this.fillBlankText) return false;
      
      const correctAnswer = this.currentQuestion.correct_answer;
      const userAnswer = this.fillBlankText.trim().toLowerCase();
      
      // Allow for some flexibility in answers
      if (typeof correctAnswer === 'string') {
        return userAnswer === correctAnswer.toLowerCase() || 
               correctAnswer.toLowerCase().includes(userAnswer) ||
               userAnswer.includes(correctAnswer.toLowerCase());
      }
      
      return false;
    },
    
    getCorrectAnswer() {
      if (!this.currentQuestion || !this.currentQuestion.correct_answer) return '';
      
      if (this.currentQuestion.type === 'mcq' && this.currentQuestion.options) {
        const correctIdx = parseInt(this.currentQuestion.correct_answer);
        if (!isNaN(correctIdx) && this.currentQuestion.options[correctIdx]) {
          return this.currentQuestion.options[correctIdx];
        }
        // If correct_answer is the actual option, not an index
        return this.currentQuestion.correct_answer;
      }
      
      return this.currentQuestion.correct_answer;
    },
    
    showAnswerFeedback() {
      if (!this.isCurrentQuestionAnswered) return;
      
      // First, check if the answer is correct
      let isCorrect = false;
      const questionId = this.currentQuestion.id;
      const userAnswer = this.selectedOptions[questionId];
      
      if (this.currentQuestion.type === 'mcq') {
        isCorrect = this.isCorrectMcq(userAnswer);
      } else if (this.currentQuestion.type === 'true_false') {
        isCorrect = this.isCorrectTrueFalse(userAnswer);
      } else if (this.currentQuestion.type === 'fill_blank') {
        isCorrect = this.isCorrectFillBlank();
      }
      
      // Show feedback in popup
      this.isCurrentAnswerCorrect = isCorrect;
      this.showResultPopup = true;
      this.showFeedback = true;
      
      // Update score
      if (isCorrect) {
        this.currentScore += this.currentQuestion.points || 1;
        
        // Add animation to score
        this.scoreUpdated = true;
        setTimeout(() => {
          this.scoreUpdated = false;
        }, 1000);
      }
    },
    
    // New methods for popup handling
    closeResultPopup() {
      this.showResultPopup = false;
      this.showExplanation = false;
    },
    
    toggleExplanation() {
      this.showExplanation = !this.showExplanation;
    },
    
    nextQuestion() {
      this.showFeedback = false;
      this.showResultPopup = false;
      this.showExplanation = false;
      
      if (this.currentQuestionIndex < this.currentChapter.questions.length - 1) {
        // Move to next question in current chapter
        this.currentQuestionIndex++;
      } else if (this.currentChapterIndex < this.quiz.chapters.length - 1) {
        // Move to first question in next chapter
        this.currentChapterIndex++;
        this.currentQuestionIndex = 0;
      }
      
      // Update fillBlankText if current question is fill_blank
      this.updateFillBlankText();
    },
    
    prevQuestion() {
      this.showFeedback = false;
      this.showResultPopup = false;
      this.showExplanation = false;
      
      if (this.currentQuestionIndex > 0) {
        // Move to previous question in current chapter
        this.currentQuestionIndex--;
      } else if (this.currentChapterIndex > 0) {
        // Move to last question in previous chapter
        this.currentChapterIndex--;
        const prevChapter = this.quiz.chapters[this.currentChapterIndex];
        this.currentQuestionIndex = prevChapter.questions.length - 1;
      }
      
      // Update fillBlankText if current question is fill_blank
      this.updateFillBlankText();
    },
    
    updateFillBlankText() {
      if (this.currentQuestion && this.currentQuestion.type === 'fill_blank') {
        this.fillBlankText = this.selectedOptions[this.currentQuestion.id] || '';
      } else {
        this.fillBlankText = '';
      }
    },
    
    confirmSubmit() {
      this.showConfirmModal = true;
    },
    
    async submitQuiz() {
      this.submitting = true;
      this.showConfirmModal = false;
      
      try {
        const response = await this.$store.dispatch('quiz/submitQuiz', {
          quizId: this.id,
          responses: this.formattedResponses
        });
        
        if (response.data && response.data.status === 'success') {
          // Show completion animation
          if (window.confetti) {
            window.confetti({
              particleCount: 150,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
          
          // Navigate to results page
          setTimeout(() => {
            this.$router.push(`/results/${response.data.result_id}`);
          }, 1500);
        } else {
          throw new Error("Failed to submit quiz");
        }
      } catch (error) {
        console.error("Error submitting quiz:", error);
        this.error = "Failed to submit quiz. Please try again.";
        this.submitting = false;
      }
    }
  }
}
</script>

<style scoped>
.quiz-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #f8f9fd;
  border-radius: 15px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e0e0e0;
  border-radius: 50%;
  border-top-color: #4a6ee0;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 2rem;
  background-color: #fff5f5;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.quiz-header {
  margin-bottom: 2rem;
  text-align: center;
}

.quiz-header h1 {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 0.5rem;
  background: linear-gradient(45deg, #4a6ee0, #6c5ce7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.quiz-description {
  font-size: 1rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.progress-container {
  margin-bottom: 2rem;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}

.progress-score {
  font-weight: bold;
  color: #4a6ee0;
  transition: all 0.3s ease;
}

.score-updated {
  transform: scale(1.1);
  color: #00b894;
  animation: pulse 0.5s ease;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.progress-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #4a6ee0, #6c5ce7);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.question-panel {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  padding: 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  transition: all 0.3s;
}

.chapter-tag {
  position: absolute;
  top: -12px;
  left: 25px;
  background: linear-gradient(90deg, #4a6ee0, #6c5ce7);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(74, 110, 224, 0.3);
}

.question {
  margin-bottom: 2rem;
}

.question p {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
  line-height: 1.6;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border: 2px solid #eaeaea;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  background-color: #ffffff;
}

.option:hover {
  border-color: #b3c6ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.option.selected {
  border-color: #4a6ee0;
  background-color: #f7f9ff;
}

.option.correct {
  border-color: #2ecc71;
  background-color: #f0fff4;
}

.option.incorrect {
  border-color: #e74c3c;
  background-color: #fff5f5;
}

.option.correct-answer {
  border: 2px dashed #2ecc71;
  animation: pulse 1.5s infinite;
}

.option-marker {
  margin-right: 15px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.option.selected .option-marker {
  border-color: #4a6ee0;
}

.option.correct .option-marker {
  border-color: #2ecc71;
}

.option.incorrect .option-marker {
  border-color: #e74c3c;
}

.option-radio {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: transparent;
  transition: all 0.2s;
}

.option.selected .option-radio {
  background-color: #4a6ee0;
}

.option.correct .option-radio {
  background-color: #2ecc71;
}

.option.incorrect .option-radio {
  background-color: #e74c3c;
}

.feedback-icon {
  position: absolute;
  right: 15px;
  font-size: 1.2rem;
  font-weight: bold;
}

.option.correct .feedback-icon {
  color: #2ecc71;
}

.option.incorrect .feedback-icon {
  color: #e74c3c;
}

.fill-blank {
  width: 100%;
}

.fill-blank input {
  width: 100%;
  padding: 15px;
  border: 2px solid #eaeaea;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.2s;
}

.fill-blank input:focus {
  border-color: #4a6ee0;
  outline: none;
  box-shadow: 0 0 0 3px rgba(74, 110, 224, 0.1);
}

.fill-blank input.correct-input {
  border-color: #2ecc71;
  background-color: #f0fff4;
}

.fill-blank input.incorrect-input {
  border-color: #e74c3c;
  background-color: #fff5f5;
}

.fill-blank-feedback {
  margin-top: 15px;
}

.feedback {
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.correct-feedback {
  background-color: #f0fff4;
  color: #2ecc71;
}

.incorrect-feedback {
  background-color: #fff5f5;
  color: #e74c3c;
}

.feedback-icon {
  margin-right: 8px;
}

.correct-answer {
  font-weight: normal;
  margin-left: 10px;
  color: #333;
}

.navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.btn-icon {
  margin: 0 8px;
}

.btn-prev {
  background-color: #f5f5f5;
  color: #555;
}

.btn-prev:hover {
  background-color: #e5e5e5;
}

.btn-next {
  background: linear-gradient(45deg, #4a6ee0, #6c5ce7);
  color: white;
}

.btn-next:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 110, 224, 0.3);
}

.btn-check-answer {
  background: linear-gradient(45deg, #3498db, #2980b9);
  color: white;
}

.btn-check-answer:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-submit {
  background: linear-gradient(45deg, #2ecc71, #27ae60);
  color: white;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.btn-retry {
  background: linear-gradient(45deg, #e74c3c, #c0392b);
  color: white;
  margin-top: 1rem;
}

.btn-check {
  background: linear-gradient(45deg, #3498db, #2980b9);
  color: white;
  margin-top: 10px;
  padding: 8px 16px;
  border-radius: 6px;
}

.btn-disabled {
  background-color: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Result popup overlay */
.result-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Result popup styles */
.result-popup {
  width: 320px;
  margin: 0 auto;
  text-align: center;
}

.flip-card {
  background-color: transparent;
  perspective: 1000px;
  height: 350px;
  width: 100%;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 15px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
}

.correct-popup .flip-card-front {
  background: linear-gradient(135deg, #43cea2, #185a9d);
  color: white;
}

.incorrect-popup .flip-card-front {
  background: linear-gradient(135deg, #ff416c, #ff4b2b);
  color: white;
}

.flip-card-back {
  background: white;
  color: #333;
  transform: rotateY(180deg);
}

.result-icon {
  font-size: 50px;
  margin-bottom: 15px;
}

.correct-answer-text {
  margin: 10px 0;
  font-size: 0.9rem;
}

.explanation-content {
  max-height: 180px;
  overflow-y: auto;
  text-align: left;
  margin: 10px 0;
  padding: 5px;
  line-height: 1.6;
}

.btn-analysis {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  border: 2px solid white;
  margin-top: 20px;
  margin-bottom: 10px;
  padding: 10px 20px;
}

.btn-analysis:hover {
  background: rgba(255, 255, 255, 0.5);
}

.btn-continue {
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
  padding: 8px 16px;
  font-size: 0.9rem;
}

.btn-continue:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-back {
  background-color: #f5f5f5;
  color: #333;
  margin-top: 15px;
}

.btn-back:hover {
  background-color: #e0e0e0;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 1.5rem;
}

.btn-cancel {
  background-color: #f5f5f5;
  color: #555;
}

.btn-confirm {
  background: linear-gradient(45deg, #2ecc71, #27ae60);
  color: white;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .quiz-container {
    padding: 1rem;
  }
  
  .question-panel {
    padding: 1.5rem;
  }
  
  .quiz-header h1 {
    font-size: 1.8rem;
  }
  
  .option {
    padding: 12px 15px;
  }
  
  .btn {
    padding: 10px 16px;
    font-size: 0.9rem;
  }
  
  .result-popup {
    width: 300px;
  }
  
  .flip-card {
    height: 320px;
  }
}
</style>
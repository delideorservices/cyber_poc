<template>
  <div class="quiz-container">
    <div v-if="loading">Loading quiz...</div>
    
    <div v-else-if="error">{{ error }}</div>
    
    <div v-else>
      <!-- Quiz header -->
      <h1>{{ quiz.title }}</h1>
      <div class="progress-bar">
        <div class="progress" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <div class="progress-text">
        Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }} ({{ progressPercentage }}% Complete)
      </div>
      
      <!-- Current chapter and question -->
      <div v-if="currentChapter && currentQuestion" class="question-panel">
        <h2>{{ currentChapter.title }}</h2>
        
        <div class="question">
          <p>{{ currentQuestion.content }}</p>
          
          <!-- MCQ Questions -->
          <div v-if="currentQuestion.type === 'mcq'" class="options">
            <div 
              v-for="(option, index) in currentQuestion.options" 
              :key="index"
              class="option"
              :class="{ selected: selectedOptions[currentQuestion.id] === index }"
              @click="selectMcqOption(index)"
            >
              <input 
                type="radio"
                :name="'question_' + currentQuestion.id"
                :checked="selectedOptions[currentQuestion.id] === index"
                @change="selectMcqOption(index)"
              >
              <span>{{ option }}</span>
            </div>
          </div>
          
          <!-- True/False Questions -->
          <div v-else-if="currentQuestion.type === 'true_false'" class="options">
            <div 
              class="option"
              :class="{ selected: selectedOptions[currentQuestion.id] === 'True' }"
              @click="selectTrueFalseOption('True')"
            >
              <input 
                type="radio" 
                :name="'question_' + currentQuestion.id"
                :checked="selectedOptions[currentQuestion.id] === 'True'"
                @change="selectTrueFalseOption('True')"
              >
              <span>True</span>
            </div>
            <div 
              class="option"
              :class="{ selected: selectedOptions[currentQuestion.id] === 'False' }"
              @click="selectTrueFalseOption('False')"
            >
              <input 
                type="radio" 
                :name="'question_' + currentQuestion.id"
                :checked="selectedOptions[currentQuestion.id] === 'False'"
                @change="selectTrueFalseOption('False')"
              >
              <span>False</span>
            </div>
          </div>
          
          <!-- Fill in the blank -->
          <div v-else-if="currentQuestion.type === 'fill_blank'" class="fill-blank">
            <input 
              type="text"
              v-model="fillBlankText"
              @input="selectFillBlankOption"
              placeholder="Your answer..."
            >
          </div>
        </div>
        
        <!-- Navigation buttons -->
        <div class="navigation">
          <button 
            v-if="!isFirstQuestion" 
            @click="prevQuestion" 
            class="btn btn-prev"
          >
            Previous
          </button>
          <div v-else></div>
          
          <button 
            v-if="!isLastQuestion" 
            @click="nextQuestion" 
            class="btn btn-next"
            :disabled="!isCurrentQuestionAnswered"
          >
            Next
          </button>
          
          <button 
            v-else 
            @click="submitQuiz" 
            class="btn btn-submit"
            :disabled="!areAllQuestionsAnswered"
          >
            {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
          </button>
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
      submitting: false
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
      return Math.round(((this.currentQuestionIndex + 1) / this.totalQuestions) * 100);
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
    areAllQuestionsAnswered() {
      if (!this.quiz || !this.quiz.chapters) return false;
      
      let allQuestionIds = [];
      this.quiz.chapters.forEach(chapter => {
        if (chapter.questions) {
          chapter.questions.forEach(question => {
            allQuestionIds.push(question.id);
          });
        }
      });
      
      for (const id of allQuestionIds) {
        if (!(id in this.selectedOptions)) {
          return false;
        }
      }
      
      return true;
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
      
      try {
        const response = await this.$store.dispatch('quiz/fetchQuiz', this.id);
        this.quiz = response.data;
        console.log("Quiz loaded:", this.quiz);
        
        this.loading = false;
      } catch (error) {
        console.error("Error fetching quiz:", error);
        this.error = "Failed to load quiz. Please try again.";
        this.loading = false;
      }
    },
    
    selectMcqOption(index) {
      console.log("MCQ option selected:", index);
      if (this.currentQuestion) {
        this.selectedOptions[this.currentQuestion.id] = index;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    selectTrueFalseOption(value) {
      console.log("True/False option selected:", value);
      if (this.currentQuestion) {
        this.selectedOptions[this.currentQuestion.id] = value;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    selectFillBlankOption() {
      console.log("Fill in blank text:", this.fillBlankText);
      if (this.currentQuestion && this.fillBlankText.trim() !== '') {
        this.selectedOptions[this.currentQuestion.id] = this.fillBlankText;
        console.log("Selected options:", this.selectedOptions);
      }
    },
    
    nextQuestion() {
      if (!this.isCurrentQuestionAnswered) return;
      
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
    
    async submitQuiz() {
      if (!this.areAllQuestionsAnswered) return;
      
      this.submitting = true;
      
      try {
        const response = await this.$store.dispatch('quiz/submitQuiz', {
          quizId: this.id,
          responses: this.formattedResponses
        });
        
        if (response.data && response.data.status === 'success') {
          // Navigate to results page
          this.$router.push(`/results/${response.data.result_id}`);
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
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: Arial, sans-serif;
}

.progress-bar {
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin: 1rem 0;
}

.progress {
  height: 100%;
  background-color: #4a6ee0;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #555;
  margin-bottom: 2rem;
}

.question-panel {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.question {
  margin-bottom: 2rem;
}

.question p {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover {
  border-color: #b3c6ff;
  background-color: #f5f8ff;
}

.option.selected {
  border-color: #4a6ee0;
  background-color: #eef2ff;
}

.option input[type="radio"] {
  margin-right: 12px;
  width: 20px;
  height: 20px;
}

.fill-blank input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.fill-blank input:focus {
  border-color: #4a6ee0;
  outline: none;
}

.navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.btn-prev {
  background-color: #e0e0e0;
  color: #333;
}

.btn-next {
  background-color: #4a6ee0;
  color: white;
}

.btn-submit {
  background-color: #2ecc71;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
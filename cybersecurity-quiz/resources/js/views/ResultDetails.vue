<template>
    <div class="result-details container">
      <div v-if="loading" class="loader">
        Loading result...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else>
        <div class="result-header">
          <h1>Quiz Results</h1>
          <div class="quiz-info">
            <h2>{{ result.quiz_title }}</h2>
            <p>Topic: {{ result.topic_name }}</p>
            <p>Completed: {{ formatDate(result.completed_at) }}</p>
          </div>
        </div>
        
        <div class="score-summary card">
          <div class="score-overview">
            <div class="score-circle" :class="scoreClass">
              {{ Math.round(result.percentage_score) }}%
            </div>
            <div class="score-details">
              <p>You scored <strong>{{ result.points_earned }} out of {{ result.total_points }}</strong> points</p>
              <p class="score-label" :class="scoreClass">{{ scoreLabel }}</p>
            </div>
          </div>
          
          <div class="chapter-scores">
            <h3>Chapter Performance</h3>
            <div v-for="(score, chapter) in result.chapter_scores" :key="chapter" class="chapter-score">
              <div class="chapter-name">{{ chapter }}</div>
              <div class="chapter-progress">
                <div 
                  class="progress-bar" 
                  :style="{ width: `${score.percentage}%` }"
                  :class="getScoreColorClass(score.percentage)"
                ></div>
              </div>
              <div class="chapter-percentage">{{ Math.round(score.percentage) }}%</div>
            </div>
          </div>
        </div>
        
        <div class="feedback-section card">
          <h3>Personalized Feedback</h3>
          <div class="feedback-content">
            <p v-for="(paragraph, index) in feedbackParagraphs" :key="index">{{ paragraph }}</p>
          </div>
        </div>
        
        <div class="skill-gaps card" v-if="result.skill_gaps && result.skill_gaps.length > 0">
          <h3>Areas for Improvement</h3>
          <ul class="gap-list">
            <li v-for="(gap, index) in result.skill_gaps" :key="index">{{ gap }}</li>
          </ul>
        </div>
        
        <div class="response-summary card">
          <h3>Question Summary</h3>
          <div class="response-filters">
            <button 
              :class="['filter-btn', { active: currentFilter === 'all' }]"
              @click="setFilter('all')"
            >All Questions</button>
            <button 
              :class="['filter-btn', { active: currentFilter === 'correct' }]"
              @click="setFilter('correct')"
            >Correct</button>
            <button 
              :class="['filter-btn', { active: currentFilter === 'incorrect' }]"
              @click="setFilter('incorrect')"
            >Incorrect</button>
          </div>
          
          <div class="responses-list">
            <div 
              v-for="response in filteredResponses" 
              :key="response.question_id"
              :class="['response-item', { 'correct': response.is_correct, 'incorrect': !response.is_correct }]"
            >
              <div class="question-content">{{ response.question_content }}</div>
              <div class="response-details">
                <div class="response-status">
                  <span v-if="response.is_correct" class="status-icon correct">✓</span>
                  <span v-else class="status-icon incorrect">✗</span>
                  {{ response.is_correct ? 'Correct' : 'Incorrect' }}
                </div>
                
                <div class="response-answer">
                  <div class="your-answer">
                    <strong>Your answer:</strong> {{ formatAnswer(response.response, response.question_type) }}
                  </div>
                  <div v-if="!response.is_correct" class="correct-answer">
                    <strong>Correct answer:</strong> {{ formatAnswer(response.correct_answer, response.question_type) }}
                  </div>
                </div>
                
                <div v-if="response.explanation" class="explanation">
                  <strong>Explanation:</strong> {{ response.explanation }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="actions">
          <router-link to="/results" class="btn btn-secondary">
            Back to Results
          </router-link>
          <router-link to="/dashboard" class="btn btn-primary">
            Dashboard
          </router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ResultDetails',
    props: {
      id: {
        type: [String, Number],
        required: true
      }
    },
    data() {
      return {
        loading: true,
        error: '',
        result: null,
        currentFilter: 'all'
      }
    },
    computed: {
      scoreClass() {
        const score = this.result?.percentage_score || 0;
        
        if (score >= 90) return 'excellent';
        if (score >= 80) return 'good';
        if (score >= 70) return 'average';
        if (score >= 60) return 'fair';
        return 'poor';
      },
      
      scoreLabel() {
        const score = this.result?.percentage_score || 0;
        
        if (score >= 90) return 'Excellent';
        if (score >= 80) return 'Good';
        if (score >= 70) return 'Average';
        if (score >= 60) return 'Fair';
        return 'Needs Improvement';
      },
      
      feedbackParagraphs() {
        if (!this.result?.feedback) return [];
        return this.result.feedback.split('\n\n');
      },
      
      filteredResponses() {
        if (!this.result?.responses) return [];
        
        if (this.currentFilter === 'all') {
          return this.result.responses;
        } else if (this.currentFilter === 'correct') {
          return this.result.responses.filter(r => r.is_correct);
        } else {
          return this.result.responses.filter(r => !r.is_correct);
        }
      }
    },
    created() {
      this.fetchResult();
    },
    methods: {
      async fetchResult() {
        this.loading = true;
        this.error = '';
        
        try {
          const response = await this.$store.dispatch('result/fetchResult', this.id);
          this.result = response.data;
        } catch (error) {
          console.error('Error fetching result:', error);
          this.error = 'Failed to load result. Please try again.';
        } finally {
          this.loading = false;
        }
      },
      
      formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
      
      getScoreColorClass(percentage) {
        if (percentage >= 90) return 'excellent';
        if (percentage >= 80) return 'good';
        if (percentage >= 70) return 'average';
        if (percentage >= 60) return 'fair';
        return 'poor';
      },
      
      setFilter(filter) {
        this.currentFilter = filter;
      },
      
      formatAnswer(answer, type) {
        if (type === 'mcq') {
          // If answer is an index, try to get the text
          if (typeof answer === 'number' || !isNaN(parseInt(answer))) {
            const index = parseInt(answer);
            const question = this.result.responses.find(r => 
              r.question_id === this.currentQuestion?.id
            );
            
            if (question?.options && index < question.options.length) {
              return question.options[index];
            }
          }
        }
        
        // For other question types or if option lookup fails
        return answer;
      }
    }
  }
  </script>
  
  <style scoped>
  .result-details {
    padding: 2rem 0;
  }
  
  .loader, .error {
    text-align: center;
    padding: 2rem;
  }
  
  .error {
    color: #ef4444;
  }
  
  .result-header {
    margin-bottom: 2rem;
  }
  
  .quiz-info {
    margin-top: 1rem;
    color: #4b5563;
  }
  
  .card {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
  
  .score-overview {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .score-circle {
    width: 6rem;
    height: 6rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 700;
    margin-right: 1.5rem;
    color: white;
  }
  
  .score-circle.excellent {
    background-color: #10b981;
  }
  
  .score-circle.good {
    background-color: #3b82f6;
  }
  
  .score-circle.average {
    background-color: #f59e0b;
  }
  
  .score-circle.fair {
    background-color: #f97316;
  }
  
  .score-circle.poor {
    background-color: #ef4444;
  }
  
  .score-details {
    flex: 1;
  }
  
  .score-label {
    font-weight: 600;
    margin-top: 0.5rem;
  }
  
  .score-label.excellent {
    color: #10b981;
  }
  
  .score-label.good {
    color: #3b82f6;
  }
  
  .score-label.average {
    color: #f59e0b;
  }
  
  .score-label.fair {
    color: #f97316;
  }
  
  .score-label.poor {
    color: #ef4444;
  }
  
  .chapter-scores {
    margin-top: 1.5rem;
  }
  
  .chapter-score {
    display: flex;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .chapter-name {
    width: 40%;
    padding-right: 1rem;
  }
  
  .chapter-progress {
    flex: 1;
    height: 0.75rem;
    background-color: #e5e7eb;
    border-radius: 9999px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    border-radius: 9999px;
  }
  
  .progress-bar.excellent {
    background-color: #10b981;
  }
  
  .progress-bar.good {
    background-color: #3b82f6;
  }
  
  .progress-bar.average {
    background-color: #f59e0b;
  }
  
  .progress-bar.fair {
    background-color: #f97316;
  }
  
  .progress-bar.poor {
    background-color: #ef4444;
  }
  
  .chapter-percentage {
    width: 3rem;
    text-align: right;
    font-weight: 600;
  }
  
  .feedback-content {
    white-space: pre-line;
  }
  
  .gap-list {
  padding-left: 1.25rem;
  margin: 0.5rem 0;
}

.gap-list li {
  margin-bottom: 0.5rem;
}

.response-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background-color: #f9fafb;
}

.filter-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.responses-list {
  margin-top: 1rem;
}

.response-item {
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.375rem;
  border-left: 4px solid transparent;
}

.response-item.correct {
  background-color: #f0fdf4;
  border-left-color: #10b981;
}

.response-item.incorrect {
  background-color: #fef2f2;
  border-left-color: #ef4444;
}

.question-content {
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.response-status {
  display: flex;
  align-items: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  margin-right: 0.5rem;
  font-size: 0.875rem;
  color: white;
}

.status-icon.correct {
  background-color: #10b981;
}

.status-icon.incorrect {
  background-color: #ef4444;
}

.response-answer {
  margin-bottom: 0.5rem;
}

.your-answer {
  margin-bottom: 0.25rem;
}

.correct-answer {
  color: #10b981;
}

.explanation {
  font-size: 0.875rem;
  color: #4b5563;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}
</style>
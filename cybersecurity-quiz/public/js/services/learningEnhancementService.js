// public/js/services/learningEnhancementService.js

class LearningEnhancementService {
    constructor() {
        this.baseUrl = '/api';
        this.headers = {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        };
    }

    // Learning Plan Methods
    async getLearningPlan() {
        return this._request('GET', '/learning-plan');
    }

    async updateMilestoneProgress(milestoneId, status) {
        return this._request('POST', `/learning-plan/milestone/${milestoneId}/progress`, { status });
    }

    async startLearningModule(moduleId) {
        return this._request('POST', `/learning-plan/module/${moduleId}/start`);
    }

    // Analytics Methods
    async getUserAnalytics() {
        return this._request('GET', '/analytics/user');
    }

    async getSkillAnalytics(skillId) {
        return this._request('GET', `/analytics/skill/${skillId}`);
    }

    async getPeerComparison() {
        return this._request('GET', '/analytics/peer-comparison');
    }

    // Skill Improvement Methods
    async getSkillImprovement(skillId) {
        return this._request('GET', `/skill-improvement/${skillId}`);
    }

    async startPracticeSession(skillId) {
        return this._request('POST', `/skill-improvement/${skillId}/practice/start`);
    }

    async submitPracticeResponse(practiceId, questionId, answer) {
        return this._request('POST', `/skill-improvement/practice/${practiceId}/response`, {
            questionId,
            answer
        });
    }

    async completePracticeSession(practiceId) {
        return this._request('POST', `/skill-improvement/practice/${practiceId}/complete`);
    }

    // Recommendation Methods
    async getRecommendations() {
        return this._request('GET', '/recommendations');
    }

    async getSavedRecommendations() {
        return this._request('GET', '/recommendations/saved');
    }

    async viewRecommendation(recommendationId) {
        return this._request('POST', `/recommendations/${recommendationId}/view`);
    }

    async completeRecommendation(recommendationId) {
        return this._request('POST', `/recommendations/${recommendationId}/complete`);
    }

    async saveRecommendation(recommendationId) {
        return this._request('POST', `/recommendations/${recommendationId}/save`);
    }

    // Generic request method
    async _request(method, endpoint, data = null) {
        const url = this.baseUrl + endpoint;
        const options = {
            method,
            headers: this.headers,
            credentials: 'same-origin'
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }
}

// Export as global variable for access across files
window.learningEnhancementService = new LearningEnhancementService();

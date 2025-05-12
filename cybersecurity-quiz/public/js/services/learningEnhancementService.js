/**
 * cybersecurity-quiz/public/js/services/learningEnhancementService.js
 * Service for handling all learning enhancement API calls
 */
class LearningEnhancementService {
    constructor() {
        this.baseUrl = '/api';
        this.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    /**
     * Get the user's learning plan
     * @param {number} userId - The user ID
     * @return {Promise} - Promise with learning plan data
     */
    getUserLearningPlan(userId) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/learning-plan`,
            type: 'GET',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Update milestone completion status
     * @param {number} userId - The user ID
     * @param {number} milestoneId - The milestone ID
     * @param {boolean} completed - Completion status
     * @return {Promise} - Promise with updated milestone data
     */
    updateMilestoneStatus(userId, milestoneId, completed) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/learning-plan/milestones/${milestoneId}`,
            type: 'PATCH',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                completed: completed
            })
        });
    }

    /**
     * Get user's skill analytics data
     * @param {number} userId - The user ID
     * @return {Promise} - Promise with analytics data
     */
    getUserAnalytics(userId) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/analytics`,
            type: 'GET',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Get skill improvement activities for a specific skill
     * @param {number} userId - The user ID
     * @param {number} skillId - The skill ID to improve
     * @return {Promise} - Promise with skill improvement activities
     */
    getSkillImprovementActivities(userId, skillId) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/skills/${skillId}/improvement`,
            type: 'GET',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Start a skill practice session
     * @param {number} userId - The user ID
     * @param {number} skillId - The skill ID
     * @param {number} difficultyLevel - Difficulty level (1-5)
     * @return {Promise} - Promise with practice session data
     */
    startSkillPractice(userId, skillId, difficultyLevel) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/skills/${skillId}/practice`,
            type: 'POST',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                difficulty_level: difficultyLevel
            })
        });
    }

    /**
     * Save practice session results
     * @param {number} userId - The user ID
     * @param {number} sessionId - The practice session ID
     * @param {Object} results - Session results data
     * @return {Promise} - Promise with saved session data
     */
    savePracticeResults(userId, sessionId, results) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/practice-sessions/${sessionId}`,
            type: 'POST',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(results)
        });
    }

    /**
     * Get personalized learning resources and recommendations
     * @param {number} userId - The user ID
     * @return {Promise} - Promise with recommendations data
     */
    getUserRecommendations(userId) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/recommendations`,
            type: 'GET',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Record user interaction with a recommendation
     * @param {number} userId - The user ID
     * @param {number} recommendationId - The recommendation ID
     * @param {string} interactionType - Type of interaction (view, click, complete)
     * @return {Promise} - Promise with interaction result
     */
    recordRecommendationInteraction(userId, recommendationId, interactionType) {
        return $.ajax({
            url: `${this.baseUrl}/users/${userId}/recommendations/${recommendationId}/interaction`,
            type: 'POST',
            headers: {
                'X-CSRF-TOKEN': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                interaction_type: interactionType
            })
        });
    }
}
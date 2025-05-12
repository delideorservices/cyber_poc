$(document).ready(function() {
    const learningService = new LearningEnhancementService();
    const userId = $('#user-data').data('userId');

    // Initialize learning plan
    function initLearningPlan() {
        learningService.getUserLearningPlan(userId)
            .done(function(data) {
                renderLearningPlan(data);
                attachEventHandlers();
            })
            .fail(function(error) {
                console.error('Error loading learning plan:', error);
                showErrorMessage('Failed to load your learning plan. Please try again later.');
            });
    }

    // Render learning plan data
    function renderLearningPlan(planData) {
        if (!planData || !planData.milestones || planData.milestones.length === 0) {
            $('#learning-plan-container').html('<p>No learning plan available yet. Complete a quiz to generate your personalized plan.</p>');
            return;
        }

        // Plan data is rendered by the Laravel Blade template
        // This function handles any dynamic post-loading adjustments
        
        // Update progress indicators
        updateProgressIndicators(planData);
    }

    // Update progress indicators based on completion status
    function updateProgressIndicators(planData) {
        const totalMilestones = planData.milestones.length;
        const completedMilestones = planData.milestones.filter(m => m.completed).length;
        const progressPercentage = Math.round((completedMilestones / totalMilestones) * 100);
        
        $('#learning-plan-progress').css('width', progressPercentage + '%');
        $('#learning-plan-progress-text').text(progressPercentage + '% Complete');
    }

    // Attach event handlers to interactive elements
    function attachEventHandlers() {
        // Milestone completion toggle
        $('.milestone-checkbox').on('change', function() {
            const milestoneId = $(this).data('milestoneId');
            const isCompleted = $(this).prop('checked');
            
            learningService.updateMilestoneStatus(userId, milestoneId, isCompleted)
                .done(function(data) {
                    // Update UI to reflect the change
                    if (isCompleted) {
                        $(`#milestone-${milestoneId}`).addClass('milestone-completed');
                    } else {
                        $(`#milestone-${milestoneId}`).removeClass('milestone-completed');
                    }
                    
                    // Refresh progress indicators
                    learningService.getUserLearningPlan(userId)
                        .done(function(planData) {
                            updateProgressIndicators(planData);
                        });
                })
                .fail(function(error) {
                    console.error('Error updating milestone:', error);
                    showErrorMessage('Failed to update milestone status. Please try again.');
                    // Revert checkbox state
                    $(this).prop('checked', !isCompleted);
                });
        });
        
        // Start associated activity button
        $('.start-activity-btn').on('click', function() {
            const activityId = $(this).data('activityId');
            const activityType = $(this).data('activityType');
            const skillId = $(this).data('skillId');
            
            switch (activityType) {
                case 'quiz':
                    window.location.href = `/quizzes/${activityId}`;
                    break;
                case 'practice':
                    startSkillPractice(skillId);
                    break;
                case 'resource':
                    const resourceUrl = $(this).data('resourceUrl');
                    // Record interaction before redirecting
                    learningService.recordRecommendationInteraction(userId, activityId, 'click')
                        .always(function() {
                            window.open(resourceUrl, '_blank');
                        });
                    break;
                default:
                    console.error('Unknown activity type:', activityType);
            }
        });
    }
    
    // Show error message to user
    function showErrorMessage(message) {
        // Use the app's existing notification system
        if (typeof showNotification === 'function') {
            showNotification('error', message);
        } else {
            alert(message);
        }
    }
    
    // Start skill practice session
    function startSkillPractice(skillId) {
        // Default to medium difficulty (can be improved with user preferences)
        const difficultyLevel = 3;
        
        learningService.startSkillPractice(userId, skillId, difficultyLevel)
            .done(function(data) {
                window.location.href = `/practice/${data.session_id}`;
            })
            .fail(function(error) {
                console.error('Error starting practice session:', error);
                showErrorMessage('Failed to start practice session. Please try again later.');
            });
    }
    
    // Initialize on page load
    initLearningPlan();
});
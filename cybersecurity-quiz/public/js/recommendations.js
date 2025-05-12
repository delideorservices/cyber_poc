$(document).ready(function() {
    const learningService = new LearningEnhancementService();
    const userId = $('#user-data').data('userId');
    
    // Initialize recommendations
    function initRecommendations() {
        learningService.getUserRecommendations(userId)
            .done(function(data) {
                renderRecommendations(data);
                attachEventHandlers();
                
                // Record that recommendations were viewed
                recordRecommendationsViewed(data);
            })
            .fail(function(error) {
                console.error('Error loading recommendations:', error);
                showErrorMessage('Failed to load recommendations. Please try again later.');
            });
    }
    
    // Render recommendations data
    function renderRecommendations(recommendationsData) {
        if (!recommendationsData || !recommendationsData.resources || recommendationsData.resources.length === 0) {
            $('#recommendations-container').html('<p>No recommendations available yet. Complete more quizzes to get personalized recommendations.</p>');
            return;
        }

        // Filter recommendations by category
        const skillResources = recommendationsData.resources.filter(r => r.type === 'skill_resource');
        const quizzes = recommendationsData.resources.filter(r => r.type === 'quiz');
        const courses = recommendationsData.resources.filter(r => r.type === 'course');
        const articles = recommendationsData.resources.filter(r => r.type === 'article');
        
        // Render skill-specific resources if available
        if (skillResources.length > 0) {
            let skillResourcesHtml = '';
            
            skillResources.forEach(resource => {
                skillResourcesHtml += `
                    

                        
${resource.title}

                        
${resource.description}

                        

                            ${resource.match_percentage}% match for your needs
                        

                        
                            Access Resource
                        
                    

                `;
            });
            
            $('#skill-resources-container').html(skillResourcesHtml);
        } else {
            $('#skill-resources-container').html('<p>No skill-specific resources available.</p>');
        }
        
        // Render recommended quizzes if available
        if (quizzes.length > 0) {
            let quizzesHtml = '';
            
            quizzes.forEach(quiz => {
                quizzesHtml += `
                    

                        
${quiz.title}

                        
${quiz.description}

                        

                            ${quiz.match_percentage}% match for your needs
                        

                        
                            Start Quiz
                        
                    

                `;
            });
            
            $('#recommended-quizzes-container').html(quizzesHtml);
        } else {
            $('#recommended-quizzes-container').html('<p>No recommended quizzes available.</p>');
        }
        
        // Similar rendering for courses and articles
        // ...
    }
    
    // Record that recommendations were viewed
    function recordRecommendationsViewed(data) {
        // Record view interaction for each recommendation
        if (data && data.resources) {
            data.resources.forEach(resource => {
                learningService.recordRecommendationInteraction(userId, resource.id, 'view');
            });
        }
    }
    
    // Attach event handlers to interactive elements
    function attachEventHandlers() {
        // Access resource button click handler
        $('.access-resource-btn').on('click', function() {
            const recommendationId = $(this).data('recommendationId');
            const resourceUrl = $(this).data('resourceUrl');
            
            // Record interaction before redirecting
            learningService.recordRecommendationInteraction(userId, recommendationId, 'click')
                .always(function() {
                    window.open(resourceUrl, '_blank');
                });
        });
        
        // Start quiz button click handler
        $('.start-quiz-btn').on('click', function() {
            const recommendationId = $(this).data('recommendationId');
            const quizId = $(this).data('quizId');
            
            // Record interaction before redirecting
            learningService.recordRecommendationInteraction(userId, recommendationId, 'click')
                .always(function() {
                    window.location.href = `/quizzes/${quizId}`;
                });
        });
        
        // Filter buttons click handlers
        $('.filter-btn').on('click', function() {
            const filterType = $(this).data('filterType');
            
            // Update active filter button
            $('.filter-btn').removeClass('active');
            $(this).addClass('active');
            
            // Show/hide relevant recommendation sections
            if (filterType === 'all') {
                $('.recommendation-section').show();
            } else {
                $('.recommendation-section').hide();
                $(`.${filterType}-section`).show();
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
    
    // Initialize on page load
    initRecommendations();
});
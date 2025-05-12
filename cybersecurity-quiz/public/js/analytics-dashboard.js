$(document).ready(function() {
    const learningService = new LearningEnhancementService();
    const userId = $('#user-data').data('userId');

    // Initialize analytics dashboard
    function initAnalyticsDashboard() {
        learningService.getUserAnalytics(userId)
            .done(function(data) {
                renderAnalyticsData(data);
                attachEventHandlers();
            })
            .fail(function(error) {
                console.error('Error loading analytics data:', error);
                showErrorMessage('Failed to load your analytics data. Please try again later.');
            });
    }

    // Render analytics data
    function renderAnalyticsData(analyticsData) {
        if (!analyticsData) {
            $('#analytics-container').html('<p>No analytics data available yet. Complete more quizzes to see your progress.</p>');
            return;
        }

        // Populate skill gap data
        if (analyticsData.skill_gaps && analyticsData.skill_gaps.length > 0) {
            const skillGapsHtml = analyticsData.skill_gaps.map(gap => {
                return `
                    

                        ${gap.skill_name}
                        ${gap.current_score}%
                        Target: ${gap.recommended_score}%
                        
                            Improve This Skill
                        
                    

                `;
            }).join('');
            
            $('#skill-gaps-container').html(skillGapsHtml);
        } else {
            $('#skill-gaps-container').html('<p>No significant skill gaps detected.</p>');
        }

        // Populate strengths data
        if (analyticsData.strengths && analyticsData.strengths.length > 0) {
            const strengthsHtml = analyticsData.strengths.map(strength => {
                return `
                    

                        ${strength.skill_name}
                        ${strength.current_score}%
                    

                `;
            }).join('');
            
            $('#strengths-container').html(strengthsHtml);
        } else {
            $('#strengths-container').html('<p>Complete more quizzes to identify your strengths.</p>');
        }

        // Populate sector benchmark comparison
        if (analyticsData.sector_comparison) {
            const sectorComparisonData = analyticsData.sector_comparison;
            
            // Data processing for benchmark comparison would go here
            // This would typically populate a chart or visual element
            // Since we're focusing on code only, we'll leave the visual implementation out
        }

        // Performance trend data
        if (analyticsData.performance_trend && analyticsData.performance_trend.length > 0) {
            // Process trend data for display
            // Again, this would typically populate a chart
        }
    }

    // Attach event handlers to interactive elements
    function attachEventHandlers() {
        // Improve skill button click handler
        $('.improve-skill-btn').on('click', function() {
            const skillId = $(this).data('skillId');
            showSkillImprovementOptions(skillId);
        });
        
        // Export analytics data handler
        $('#export-analytics-btn').on('click', function() {
            exportAnalyticsData();
        });
    }
    
    // Show skill improvement options
    function showSkillImprovementOptions(skillId) {
        learningService.getSkillImprovementActivities(userId, skillId)
            .done(function(data) {
                // Build modal content with improvement options
                let optionsHtml = '';
                
                if (data.practice_options && data.practice_options.length > 0) {
                    optionsHtml += '<h4>Practice Exercises</h4>';
                    data.practice_options.forEach(option => {
                        optionsHtml += `
                            

                                ${option.title}
                                
                                    Start Practice
                                
                            

                        `;
                    });
                }
                
                if (data.resources && data.resources.length > 0) {
                    optionsHtml += '<h4>Learning Resources</h4>';
                    data.resources.forEach(resource => {
                        optionsHtml += `
                            

                                ${resource.title}
                                
                                    View Resource
                                
                            

                        `;
                    });
                }
                
                // Show in modal (using app's existing modal system or custom implementation)
                showImprovementModal(skillId, optionsHtml);
            })
            .fail(function(error) {
                console.error('Error loading improvement options:', error);
                showErrorMessage('Failed to load improvement options. Please try again later.');
            });
    }
    
    // Show improvement options modal
    function showImprovementModal(skillId, contentHtml) {
        // Uses the app's existing modal system
        // If no modal system exists, one would need to be implemented
        $('#improvement-modal-content').html(contentHtml);
        $('#improvement-modal-title').text('Skill Improvement Options');
        $('#improvement-modal').modal('show');
        
        // Attach handlers to the new buttons within the modal
        $('.start-practice-btn').on('click', function() {
            const difficulty = $(this).data('difficulty');
            startSkillPractice(skillId, difficulty);
            $('#improvement-modal').modal('hide');
        });
        
        $('.view-resource-btn').on('click', function() {
            const resourceId = $(this).data('resourceId');
            const resourceUrl = $(this).data('resourceUrl');
            
            // Record interaction before redirecting
            learningService.recordRecommendationInteraction(userId, resourceId, 'click')
                .always(function() {
                    window.open(resourceUrl, '_blank');
                });
        });
    }
    
    // Start skill practice session
    function startSkillPractice(skillId, difficultyLevel) {
        learningService.startSkillPractice(userId, skillId, difficultyLevel)
            .done(function(data) {
                window.location.href = `/practice/${data.session_id}`;
            })
            .fail(function(error) {
                console.error('Error starting practice session:', error);
                showErrorMessage('Failed to start practice session. Please try again later.');
            });
    }
    
    // Export analytics data
    function exportAnalyticsData() {
        learningService.getUserAnalytics(userId)
            .done(function(data) {
                // Format data for export (CSV or PDF)
                let exportData = {
                    user_name: data.user_name,
                    export_date: new Date().toISOString(),
                    skills: []
                };
                
                // Compile skills data
                if (data.all_skills) {
                    data.all_skills.forEach(skill => {
                        exportData.skills.push({
                            name: skill.name,
                            score: skill.current_score,
                            benchmark: skill.sector_benchmark,
                            last_assessed: skill.last_assessed
                        });
                    });
                }
                
                // Convert to CSV
                const csvContent = convertToCSV(exportData);
                
                // Trigger download
                downloadCSV(csvContent, `cybersecurity_skills_${userId}_${new Date().toISOString().slice(0,10)}.csv`);
            })
            .fail(function(error) {
                console.error('Error exporting analytics data:', error);
                showErrorMessage('Failed to export analytics data. Please try again.');
            });
    }
    
    // Convert data to CSV format
    function convertToCSV(data) {
        // CSV header
        let csvContent = "Skill Name,Current Score,Sector Benchmark,Last Assessed\n";
        
        // Add rows
        data.skills.forEach(skill => {
            csvContent += `"${skill.name}",${skill.score},${skill.benchmark},"${skill.last_assessed}"\n`;
        });
        
        return csvContent;
    }
    
    // Trigger CSV file download
    function downloadCSV(csvContent, filename) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
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
    initAnalyticsDashboard();
});
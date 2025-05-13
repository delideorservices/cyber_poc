// public/js/learning-plan.js

$(document).ready(function() {
    // Initialize tooltips and popovers
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    
    // Progress bar animations
    $('.progress-bar').each(function() {
        const percentage = $(this).attr('aria-valuenow');
        $(this).css('width', percentage + '%');
    });
    
    // Milestone completion toggle
    $('.milestone-checkbox').on('change', function() {
        const milestoneId = $(this).data('milestone-id');
        const isCompleted = $(this).prop('checked');
        const status = isCompleted ? 'completed' : 'in_progress';
        
        // Update UI to show loading state
        $(this).closest('.milestone-card').addClass('updating');
        
        // Call API to update milestone progress
        learningEnhancementService.updateMilestoneProgress(milestoneId, status)
            .then(response => {
                // Update UI based on response
                const milestone = $(this).closest('.milestone-card');
                milestone.removeClass('updating');
                
                if (isCompleted) {
                    milestone.addClass('completed');
                    updatePlanProgress();
                } else {
                    milestone.removeClass('completed');
                    updatePlanProgress();
                }
            })
            .catch(error => {
                console.error('Error updating milestone:', error);
                // Revert UI state
                $(this).prop('checked', !isCompleted);
                $(this).closest('.milestone-card').removeClass('updating');
                showErrorAlert('Failed to update milestone progress. Please try again.');
            });
    });
    
    // Module start buttons
    $('.module-start-btn').on('click', function(e) {
        e.preventDefault();
        const moduleId = $(this).data('module-id');
        const moduleType = $(this).data('module-type');
        
        // Show confirmation if needed for certain module types
        if (moduleType === 'assessment') {
            if (!confirm('Starting this assessment will begin a timed session. Are you ready to proceed?')) {
                return;
            }
        }
        
        // Call service to start module
        window.location.href = $(this).attr('href');
    });
    
    // Function to update overall plan progress
    function updatePlanProgress() {
        const totalMilestones = $('.milestone-card').length;
        const completedMilestones = $('.milestone-card.completed').length;
        const percentage = Math.round((completedMilestones / totalMilestones) * 100);
        
        // Update progress bar
        $('.plan-progress-bar').css('width', percentage + '%');
        $('.plan-progress-bar').attr('aria-valuenow', percentage);
        $('.plan-progress-percentage').text(percentage + '%');
    }
    
    // Error alert function
    function showErrorAlert(message) {
        const alert = $('<div class="alert alert-danger alert-dismissible fade show" role="alert">' +
            message +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span>' +
            '</button>' +
            '</div>');
        
        $('#alert-container').append(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.alert('close');
        }, 5000);
    }
});

$(document).ready(function() {
    const learningService = new LearningEnhancementService();
    const userId = $('#user-data').data('userId');
    const sessionId = $('#practice-data').data('sessionId');
    let questions = []; // Changed to let instead of const since we reassign it
    let currentQuestionIndex = 0;
    let userResponses = [];
    
    // Initialize practice session
    function initPracticeSession() {
        // Fetch practice session data
        $.ajax({
            url: `/api/practice-sessions/${sessionId}`,
            type: 'GET',
            headers: {
                'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content'),
                'Accept': 'application/json'
            }
        })
        .done(function(data) {
            if (!data || !data.questions || data.questions.length === 0) {
                showErrorMessage('No practice questions available.');
                return;
            }
            
            // Store questions
            questions = data.questions;
            
            // Init user responses array
            userResponses = questions.map((question) => ({ 
                question_id: question.id, // Set the question_id directly
                response: null, 
                is_correct: false,
                points_earned: 0,
                time_taken: 0,
                start_time: 0 // Initialize start_time
            }));
            
            // Show first question
            showQuestion(0);
            
            // Start timer if enabled
            if (data.timed_practice) {
                startPracticeTimer(data.time_limit);
            }
        })
        .fail(function(error) {
            console.error('Error loading practice session:', error);
            showErrorMessage('Failed to load practice session. Please try again later.');
        });
    }
    
    // Show a specific question
    function showQuestion(index) {
        if (index < 0 || index >= questions.length) {
            console.error('Invalid question index:', index);
            return;
        }
        
        currentQuestionIndex = index;
        const question = questions[index];
        
        // Update question number indicator
        $('#question-number').text(`Question ${index + 1} of ${questions.length}`);
        
        // Populate question content
        $('#question-content').html(question.content);
        
        // Clear previous options
        $('#question-options').empty();
        
        // Handle different question types
        switch (question.type) {
            case 'mcq':
                renderMultipleChoiceQuestion(question);
                break;
            case 'true_false':
                renderTrueFalseQuestion(question);
                break;
            case 'fill_blank':
                renderFillBlankQuestion(question);
                break;
            case 'drag_drop':
                renderDragDropQuestion(question);
                break;
            default:
                console.error('Unknown question type:', question.type);
        }
        
        // Record question start time
        userResponses[index].start_time = new Date().getTime();
        
        // Update navigation buttons
        updateNavigationButtons();
    }
    
    // Update navigation buttons based on current question
    function updateNavigationButtons() {
        // Disable previous button on first question
        $('#prev-question-btn').prop('disabled', currentQuestionIndex === 0);
        
        // Change next button to submit on last question
        if (currentQuestionIndex === questions.length - 1) {
            $('#next-question-btn').text('Submit Answers');
            $('#next-question-btn').data('action', 'submit');
        } else {
            $('#next-question-btn').text('Next Question');
            $('#next-question-btn').data('action', 'next');
        }
    }
    
    // Render multiple choice question
    function renderMultipleChoiceQuestion(question) {
        let optionsHtml = '';
        
        question.options.forEach((option, idx) => {
            optionsHtml += `
                <div class="option-container">
                    <input type="radio" class="mcq-option" name="mcq-answer" id="option-${idx}" data-option-index="${idx}">
                    <label for="option-${idx}">${option}</label>
                </div>
            `;
        });
        
        $('#question-options').html(optionsHtml);
        
        // Add event handler
        $('.mcq-option').on('change', function() {
            const optionIndex = $(this).data('optionIndex');
            recordAnswer(optionIndex);
        });
    }
    
    // Render true/false question
    function renderTrueFalseQuestion(question) {
        const optionsHtml = `
            <div class="option-container">
                <input type="radio" class="tf-option" name="tf-answer" id="option-true" data-option-value="True">
                <label for="option-true">True</label>
            </div>
            <div class="option-container">
                <input type="radio" class="tf-option" name="tf-answer" id="option-false" data-option-value="False">
                <label for="option-false">False</label>
            </div>
        `;
        
        $('#question-options').html(optionsHtml);
        
        // Add event handler
        $('.tf-option').on('change', function() {
            const optionValue = $(this).data('optionValue');
            recordAnswer(optionValue);
        });
    }
    
    // Render fill-in-the-blank question
    function renderFillBlankQuestion(question) {
        // Replace blanks in content with input fields
        let content = question.content;
        let blankIndex = 0;
        
        content = content.replace(/\{blank\}/g, function() {
            return `<input type="text" class="blank-input" data-blank-index="${blankIndex++}">`;
        });
        
        $('#question-content').html(content);
        
        // Add event handler
        $('.blank-input').on('input', function() {
            // Create an array of all blank values
            const allBlanks = [];
            $('.blank-input').each(function() {
                allBlanks[$(this).data('blankIndex')] = $(this).val();
            });
            
            recordAnswer(allBlanks);
        });
    }
    
    // Render drag and drop question
    function renderDragDropQuestion(question) {
        // This implementation would typically include drag-and-drop libraries
        // For simplicity, we'll just create a simple drag-drop interface
        
        let itemsHtml = '<div class="drag-items-container">';
        question.drag_items.forEach((item, idx) => {
            itemsHtml += `<div class="drag-item" draggable="true" data-item-id="${idx}">${item}</div>`;
        });
        itemsHtml += '</div>';
        
        let dropsHtml = '<div class="drop-zones-container">';
        question.drop_targets.forEach((target, idx) => {
            dropsHtml += `
                <div class="drop-target">
                    <div class="target-label">${target}</div>
                    <div class="drop-zone" data-target-id="${idx}"></div>
                </div>
            `;
        });
        dropsHtml += '</div>';
        
        $('#question-options').html(itemsHtml + dropsHtml);
        
        // Set up drag and drop functionality
        setupDragAndDrop();
    }
    
    // Setup drag and drop functionality
    function setupDragAndDrop() {
        const dragItems = document.querySelectorAll('.drag-item');
        const dropZones = document.querySelectorAll('.drop-zone');
        
        dragItems.forEach(item => {
            item.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', item.dataset.itemId);
                this.classList.add('dragging');
            });
            
            item.addEventListener('dragend', function() {
                this.classList.remove('dragging');
            });
        });
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });
            
            zone.addEventListener('dragleave', function() {
                this.classList.remove('drag-over');
            });
            
            zone.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                const itemId = e.dataTransfer.getData('text/plain');
                const targetId = this.dataset.targetId;
                
                // Move the dragged item to this drop zone
                const draggedItem = document.querySelector(`.drag-item[data-item-id="${itemId}"]`);
                
                // Check if target already has an item
                if (this.querySelector('.drag-item')) {
                    // Move existing item back to container
                    const existingItem = this.querySelector('.drag-item');
                    document.querySelector('.drag-items-container').appendChild(existingItem);
                }
                
                this.appendChild(draggedItem);
                
                // Record the mapping
                recordDragDropMapping();
            });
        });
    }
    
    // Record drag-drop mapping
    function recordDragDropMapping() {
        const mapping = {};
        
        document.querySelectorAll('.drop-zone').forEach(zone => {
            const targetId = zone.dataset.targetId;
            const item = zone.querySelector('.drag-item');
            
            if (item) {
                mapping[targetId] = item.dataset.itemId;
            }
        });
        
        recordAnswer(mapping);
    }
    
    // Record user's answer
    function recordAnswer(answer) {
        if (currentQuestionIndex >= 0 && currentQuestionIndex < userResponses.length) {
            userResponses[currentQuestionIndex].response = answer;
            userResponses[currentQuestionIndex].time_taken = 
                new Date().getTime() - userResponses[currentQuestionIndex].start_time;
        }
    }
    
    // Handle navigation button clicks
    function setupNavigationHandlers() {
        // Previous button
        $('#prev-question-btn').on('click', function() {
            if (currentQuestionIndex > 0) {
                showQuestion(currentQuestionIndex - 1);
            }
        });
        
        // Next/Submit button
        $('#next-question-btn').on('click', function() {
            const action = $(this).data('action');
            
            if (action === 'next') {
                if (currentQuestionIndex < questions.length - 1) {
                    showQuestion(currentQuestionIndex + 1);
                }
            } else if (action === 'submit') {
                confirmSubmission();
            }
        });
    }
    
    // Show confirmation dialog before final submission
    function confirmSubmission() {
        // Count unanswered questions
        const unanswered = userResponses.filter(r => r.response === null).length;
        
        let message = 'Are you sure you want to submit your answers?';
        if (unanswered > 0) {
            message = `You have ${unanswered} unanswered question(s). Are you sure you want to submit?`;
        }
        
        // Confirm with user
        if (confirm(message)) {
            submitPracticeSession();
        }
    }
    
    // Submit practice session
    function submitPracticeSession() {
        // Prepare submission data
        const submissionData = {
            session_id: sessionId,
            responses: userResponses
        };
        
        // Submit to server
        learningService.savePracticeResults(userId, sessionId, submissionData)
            .done(function(data) {
                // Redirect to results page
                window.location.href = `/practice/${sessionId}/results`;
            })
            .fail(function(error) {
                console.error('Error submitting practice session:', error);
                showErrorMessage('Failed to submit your answers. Please try again.');
            });
    }
    
    // Start practice timer
    function startPracticeTimer(timeLimit) {
        // Implementation for timer functionality
        let timeRemaining = timeLimit * 60; // Convert to seconds
        const timerElement = $('#practice-timer');
        
        if (timerElement.length === 0) {
            console.warn('Timer element not found in the DOM');
            return;
        }
        
        const timerInterval = setInterval(function() {
            timeRemaining--;
            
            // Format time as mm:ss
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Update timer display
            timerElement.text(formattedTime);
            
            // Auto-submit when time expires
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert('Time is up! Your answers will be submitted automatically.');
                submitPracticeSession();
            }
        }, 1000);
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
    
    // Initialize event handlers
    setupNavigationHandlers();
    
    // Initialize practice session
    initPracticeSession();
});
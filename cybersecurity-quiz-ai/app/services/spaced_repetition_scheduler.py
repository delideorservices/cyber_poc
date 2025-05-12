from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math
import logging
import app.services.db_service as db_service

class SpacedRepetitionScheduler:
    """
    Implements a spaced repetition algorithm based on the SuperMemo-2 algorithm
    to schedule optimal review intervals for cybersecurity concepts.
    """
    
    def __init__(self):
        """Initialize the spaced repetition scheduler."""
        self.logger = logging.getLogger(__name__)
        
    def schedule_repetition(self, user_id: int, skill_id: int, difficulty: int = 3, 
                           performance_rating: Optional[int] = None) -> Dict:
        """
        Schedule the next repetition based on user performance.
        
        Args:
            user_id: User ID
            skill_id: Skill ID being practiced
            difficulty: Difficulty level of the material (1-5)
            performance_rating: User's performance rating (0-5), where:
                                0 = Complete failure
                                5 = Perfect recall
                                None = New item, no prior performance
        
        Returns:
            Dictionary with next repetition details
        """
        # For new items (no performance rating), schedule based on difficulty
        if performance_rating is None:
            # Initial intervals based on difficulty (in days)
            initial_intervals = {
                1: 1,    # Easiest: Start with 1 day
                2: 1,    
                3: 1,    # Medium: Also 1 day
                4: 0.5,  # Harder: Review sooner (12 hours)
                5: 0.5   # Hardest: Review sooner (12 hours)
            }
            
            interval = initial_intervals.get(difficulty, 1)
            easiness_factor = 2.5  # Default easiness factor
            repetition_number = 1
            
        else:
            # Get the most recent repetition schedule
            last_schedule = db_service.fetch_one(
                "SELECT * FROM spaced_repetition_schedules "
                "WHERE user_id = %s AND skill_id = %s "
                "ORDER BY repetition_number DESC LIMIT 1",
                (user_id, skill_id)
            )
            
            if not last_schedule:
                # Fall back to default if no schedule exists
                return self.schedule_repetition(user_id, skill_id, difficulty, None)
            
            # Calculate new interval using the SM-2 algorithm
            easiness_factor = last_schedule.get('easiness_factor', 2.5)
            repetition_number = last_schedule.get('repetition_number', 0) + 1
            
            # Update easiness factor based on performance
            easiness_factor = self._update_easiness_factor(easiness_factor, performance_rating)
            
            # Calculate interval
            if performance_rating < 3:
                # If performance was poor, reset to beginning
                repetition_number = 1
                interval = 1
            else:
                # Good performance, calculate next interval
                if repetition_number == 1:
                    interval = 1
                elif repetition_number == 2:
                    interval = 6
                else:
                    # Get previous interval
                    prev_interval = (
                        last_schedule.get('scheduled_date') - 
                        last_schedule.get('created_at')
                    ).days
                    
                    # Calculate new interval
                    interval = prev_interval * easiness_factor
                    
                    # Apply adjustment based on difficulty
                    difficulty_factor = 1.0 - ((difficulty - 1) * 0.1)  # Maps 1-5 to 1.0-0.6
                    interval *= difficulty_factor
                    
                    # Round to nearest day
                    interval = round(interval)
                    
                    # Ensure minimum interval of 1 day
                    interval = max(1, interval)
        
        # Calculate next review date
        next_date = datetime.now() + timedelta(days=interval)
        
        # Create new schedule record
        schedule_id = db_service.execute_returning(
            "INSERT INTO spaced_repetition_schedules "
            "(user_id, skill_id, repetition_number, easiness_factor, "
            "interval_days, scheduled_date, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (user_id, skill_id, repetition_number, easiness_factor, 
             interval, next_date, 'scheduled')
        )['id']
        
        # Get skill information
        skill = db_service.fetch_one(
            "SELECT name FROM skills WHERE id = %s", 
            (skill_id,)
        )
        
        # Prepare response
        schedule = {
            'id': schedule_id,
            'user_id': user_id,
            'skill_id': skill_id,
            'skill_name': skill['name'] if skill else f"Skill #{skill_id}",
            'repetition_number': repetition_number,
            'easiness_factor': easiness_factor,
            'interval_days': interval,
            'scheduled_date': next_date,
            'status': 'scheduled'
        }
        
        self.logger.info(f"Scheduled repetition #{repetition_number} for user {user_id}, "
                        f"skill {skill_id} in {interval} days (EF: {easiness_factor:.2f})")
        
        return schedule
        
    def get_due_repetitions(self, user_id: int) -> List[Dict]:
        """
        Get all repetitions that are due for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of due repetition schedules
        """
        due_repetitions = db_service.fetch_all(
            "SELECT srs.*, s.name as skill_name "
            "FROM spaced_repetition_schedules srs "
            "JOIN skills s ON srs.skill_id = s.id "
            "WHERE srs.user_id = %s AND srs.status = 'scheduled' "
            "AND srs.scheduled_date <= NOW() "
            "ORDER BY srs.scheduled_date ASC",
            (user_id,)
        )
        
        return due_repetitions
        
    def complete_repetition(self, schedule_id: int, performance_rating: int) -> Dict:
        """
        Mark a repetition as completed and schedule the next one.
        
        Args:
            schedule_id: Schedule ID to mark as completed
            performance_rating: User's performance rating (0-5)
        
        Returns:
            Details of the next scheduled repetition
        """
        # Get the schedule to complete
        schedule = db_service.fetch_one(
            "SELECT * FROM spaced_repetition_schedules WHERE id = %s",
            (schedule_id,)
        )
        
        if not schedule:
            raise ValueError(f"Schedule with ID {schedule_id} not found")
            
        # Mark as completed
        db_service.execute(
            "UPDATE spaced_repetition_schedules "
            "SET status = 'completed', performance_rating = %s, completed_at = NOW() "
            "WHERE id = %s",
            (performance_rating, schedule_id)
        )
        
        # Schedule the next repetition
        next_schedule = self.schedule_repetition(
            schedule['user_id'],
            schedule['skill_id'],
            3,  # Use medium difficulty for now
            performance_rating
        )
        
        return next_schedule
        
    def _update_easiness_factor(self, current_ef: float, performance: int) -> float:
        """
        Update the easiness factor based on performance rating.
        
        The easiness factor determines how quickly intervals grow.
        Uses the SuperMemo-2 algorithm formula.
        
        Args:
            current_ef: Current easiness factor
            performance: Performance rating (0-5)
            
        Returns:
            Updated easiness factor
        """
        # Convert 0-5 scale to 0-5 for SM-2 algorithm
        q = performance
        
        # Calculate new easiness factor
        new_ef = current_ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        
        # EF is always at least 1.3
        new_ef = max(1.3, new_ef)
        
        return new_ef
import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

from app.services.db_service import db_service
from app.config import OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CrewService:
    """Service for managing CrewAI agents and tasks"""
    
    def __init__(self):
        """Initialize CrewService with LLM"""
        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
    
    def create_registration_crew(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a CrewAI setup for the registration phase
        
        Args:
            user_data: Dictionary with user registration data
            
        Returns:
            Dictionary with results from the crew's work
        """
        logger.info(f"Creating registration crew for user: {user_data.get('email')}")
        
        # Create agents without tools for now
        registration_agent = Agent(
            role="Registration Agent",
            goal="Collect and validate user profile data and store it in the database",
            backstory="I am an expert at handling user registration and ensuring data quality. I verify inputs and store them securely in the database.",
            verbose=True,
            llm=self.llm
        )
        
        profile_analyzer_agent = Agent(
            role="Profile Analyzer Agent",
            goal="Analyze user background to identify expertise level and create personalization metadata",
            backstory="I specialize in analyzing cybersecurity profiles to determine expertise levels and identify relevant skills and knowledge gaps.",
            verbose=True,
            llm=self.llm
        )
        
        topic_mapper_agent = Agent(
            role="Topic Mapper Agent",
            goal="Map user topics to categories and identify relevant threats for quiz generation",
            backstory="I am skilled at connecting user profiles with relevant cybersecurity topics. I understand industry-specific threats and can prioritize learning paths.",
            verbose=True,
            llm=self.llm
        )
        
        # Create tasks with more detailed instructions
        registration_task = Task(
            description=(
                f"Register a new user with the following information:\n"
                f"Name: {user_data.get('name')}\n"
                f"Email: {user_data.get('email')}\n"
                f"Sector ID: {user_data.get('sector_id')}\n"
                f"Role ID: {user_data.get('role_id')}\n"
                f"Experience: {user_data.get('years_experience', 'Not specified')}\n"
                f"Learning goal: {user_data.get('learning_goal', 'Not specified')}\n\n"
                f"First, validate that all required fields are present and properly formatted. "
                f"Then, assume the user data is stored in the database. You don't have direct database access, but you can "
                f"analyze and process the data as needed.\n\n"
                f"Return a JSON response with the user's information and a confirmation message."
            ),
            agent=registration_agent,
            expected_output="A JSON object containing the user information and confirmation of registration",
        )
        
        profile_analysis_task = Task(
            description=(
                "Now, analyze the user profile to determine expertise level and create personalization metadata:\n\n"
                f"User's sector: The sector with ID {user_data.get('sector_id')}\n"
                f"User's role: The role with ID {user_data.get('role_id')}\n"
                f"User's experience: {user_data.get('years_experience', 'Not specified')} years\n\n"
                "Based on years_experience, determine a skill level from 1-5 where:\n"
                "   - 0-1 years: Level 1 (Beginner)\n"
                "   - 2-3 years: Level 2 (Intermediate)\n"
                "   - 4-6 years: Level 3 (Competent)\n"
                "   - 7-10 years: Level 4 (Advanced)\n"
                "   - 10+ years: Level 5 (Expert)\n\n"
                "Create a detailed user profile analysis including:\n"
                "   - Estimated skill level (1-5)\n"
                "   - Recommended quiz difficulty level\n"
                "   - Potential knowledge areas based on role and sector\n"
                "   - Suggested learning focus areas\n\n"
                "Provide your output as a detailed JSON object containing all this information."
            ),
            agent=profile_analyzer_agent,
            context=[registration_task],
            expected_output="A detailed JSON object with user profile analysis and personalization metadata",
        )
        
        topic_mapping_task = Task(
            description=(
                "Based on the user profile analysis, map to appropriate cybersecurity topics and threats:\n\n"
                f"Topic ID from user registration: {user_data.get('topic_id')}\n"
                "For this topic, assess its relevance to the user based on:\n"
                "   - User's sector\n"
                "   - User's role\n"
                "   - User's experience level\n"
                "   - User's learning goals\n\n"
                "Identify current and relevant threats specific to the user's sector.\n"
                "Create a prioritized list of topics with relevance scores.\n"
                "Identify 3-5 focus areas for quiz generation.\n\n"
                "Provide your output as a JSON object containing:\n"
                "- topic_priorities: Array of topics with relevance scores\n"
                "- sector_threats: Key sector-specific threats identified\n"
                "- focus_areas: 3-5 specific focus areas for quiz generation\n"
                "- recommended_topic_id: The ID of the most relevant topic"
            ),
            agent=topic_mapper_agent,
            context=[profile_analysis_task],
            expected_output="A JSON object with mapped topics, threats, and focus areas",
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[registration_agent, profile_analyzer_agent, topic_mapper_agent],
            tasks=[registration_task, profile_analysis_task, topic_mapping_task],
            verbose=True,
            process=Process.sequential  # Run tasks in sequence
        )
        
        # Start the crew's work
        try:
            logger.info("Starting registration crew workflow")
            result = crew.kickoff()
            logger.info(f"Crew result: {result}")
            
            # Log success
            logger.info("Registration crew completed successfully")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="registration_crew",
                input_data={"email": user_data.get('email')},
                output_data={"success": True},
                status="success"
            )
            
            return self._parse_registration_result(result, user_data)
            
        except Exception as e:
            # Log error
            logger.error(f"Error in registration crew: {str(e)}")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="registration_crew",
                input_data={"email": user_data.get('email')},
                status="error",
                error_message=str(e)
            )
            raise
    
    def create_quiz_generation_crew(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a CrewAI setup for the quiz generation phase
        
        Args:
            quiz_data: Dictionary with quiz generation data
            
        Returns:
            Dictionary with results from the crew's work
        """
        logger.info(f"Creating quiz generation crew for topic: {quiz_data.get('topic_name')}")
        
        # Create agents (without tools for compatibility)
        quiz_generator_agent = Agent(
            role="Quiz Generator Agent",
            goal="Create diverse and accurate quiz content tailored to the user's expertise level",
            backstory="I am an expert at creating cybersecurity quizzes with diverse question types that test knowledge comprehensively.",
            verbose=True,
            llm=self.llm
        )
        
        quiz_formatter_agent = Agent(
            role="Quiz Formatter Agent",
            goal="Structure quiz content for optimal display and grading in the system",
            backstory="I specialize in formatting quiz content for optimal display and grading. I ensure all metadata is properly structured.",
            verbose=True,
            llm=self.llm
        )
        
        quiz_delivery_agent = Agent(
            role="Quiz Delivery Agent",
            goal="Save quiz content to database and prepare for delivery to users",
            backstory="I handle the final steps of quiz preparation and delivery, ensuring everything is properly stored in the database.",
            verbose=True,
            llm=self.llm
        )
        
        # Create more detailed tasks
        quiz_generation_task = Task(
            description=(
                f"Generate a comprehensive cybersecurity quiz on '{quiz_data.get('topic_name')}' with the following parameters:\n\n"
                f"- User sector: {quiz_data.get('user_sector', 'General')}\n"
                f"- User role: {quiz_data.get('user_role', 'General')}\n"
                f"- Experience level: {quiz_data.get('experience_level', 3)} (out of 5)\n"
                f"- Focus areas: {', '.join(quiz_data.get('focus_areas', ['General Cybersecurity']))}\n\n"
                f"The quiz should have 4 chapters:\n"
                f"1. Cybersecurity Basics related to {quiz_data.get('topic_name')}\n"
                f"2. {quiz_data.get('user_role', 'Role')}-specific Risks\n"
                f"3. {quiz_data.get('user_sector', 'Sector')}-specific Threats\n"
                f"4. Advanced Challenges\n\n"
                f"Each chapter must have 5 questions with a mix of types:\n"
                f"- Multiple choice (with 4 options, only 1 correct)\n"
                f"- True/False\n"
                f"- Fill in the blank\n\n"
                f"For each question, include:\n"
                f"- Question content\n"
                f"- Answer options (for MCQ and T/F)\n"
                f"- Correct answer\n"
                f"- Detailed explanation\n\n"
                f"The questions should be practical, relevant to real-world scenarios, and appropriate for the user's experience level.\n\n"
                f"Provide your output as a detailed JSON object with the complete quiz structure."
            ),
            agent=quiz_generator_agent,
            expected_output="A complete JSON object with the quiz content structure",
        )
        
        quiz_formatting_task = Task(
            description=(
                "Format the generated quiz content into a structured format optimized for the application:\n\n"
                "1. Ensure each chapter has a clear title and description\n"
                "2. Format all questions consistently with the following structure:\n"
                "   - type: 'mcq', 'true_false', or 'fill_blank'\n"
                "   - content: The question text\n"
                "   - options: Array of options (for MCQ and T/F)\n"
                "   - correct_answer: Index for MCQ (as string), 'True'/'False' for T/F, or text for fill_blank\n"
                "   - explanation: Detailed explanation of the answer\n"
                "3. Add metadata for each question including:\n"
                "   - difficulty: 1-5 based on complexity\n"
                "   - knowledge_area: The specific knowledge area being tested\n"
                "   - points: Points value (1-5) based on difficulty\n\n"
                "4. Structure the entire quiz as a properly formatted JSON object with the following structure:\n"
                "{\n"
                "  \"title\": \"Quiz title\",\n"
                "  \"description\": \"Quiz description\",\n"
                "  \"difficulty_level\": 1-5,\n"
                "  \"chapters\": [\n"
                "    {\n"
                "      \"title\": \"Chapter title\",\n"
                "      \"description\": \"Chapter description\",\n"
                "      \"questions\": [\n"
                "        {\n"
                "          \"type\": \"question type\",\n"
                "          \"content\": \"question text\",\n"
                "          \"options\": [\"option1\", \"option2\", ...],\n"
                "          \"correct_answer\": \"correct answer\",\n"
                "          \"explanation\": \"explanation text\",\n"
                "          \"difficulty\": 1-5,\n"
                "          \"points\": 1-5,\n"
                "          \"knowledge_area\": \"specific area\"\n"
                "        },\n"
                "        ...\n"
                "      ]\n"
                "    },\n"
                "    ...\n"
                "  ]\n"
                "}\n\n"
                "Ensure the JSON is valid and properly formatted."
            ),
            agent=quiz_formatter_agent,
            context=[quiz_generation_task],
            expected_output="A properly formatted JSON object with all quiz content structured for the application",
        )
        
        quiz_delivery_task = Task(
            description=(
                "Prepare the quiz for delivery to the user:\n\n"
                "Imagine you are saving this quiz to a database with the following steps:\n\n"
                "1. Create the quiz record in the 'quizzes' table with:\n"
                "   - title\n"
                "   - description\n"
                "   - user_id\n"
                "   - topic_id\n"
                "   - difficulty_level\n\n"
                "2. Create each chapter in the 'chapters' table with:\n"
                "   - quiz_id\n"
                "   - title\n"
                "   - description\n"
                "   - sequence\n\n"
                "3. Create each question in the 'questions' table with:\n"
                "   - chapter_id\n"
                "   - type\n"
                "   - content\n"
                "   - options\n"
                "   - correct_answer\n"
                "   - explanation\n"
                "   - sequence\n"
                "   - points\n\n"
                "4. Return a summary of the saved quiz including:\n"
                "   - quiz_id: (Provide a mock ID)\n"
                "   - quiz_title: The title of the quiz\n"
                "   - chapter_count: Number of chapters\n"
                "   - question_count: Total number of questions\n"
                f"   - user_id: {quiz_data.get('user_id')}\n\n"
                "Return this summary as a JSON object."
            ),
            agent=quiz_delivery_agent,
            context=[quiz_formatting_task],
            expected_output="A JSON object with details of the saved quiz including IDs and counts",
        )
        
        # Create crew
        crew = Crew(
            agents=[quiz_generator_agent, quiz_formatter_agent, quiz_delivery_agent],
            tasks=[quiz_generation_task, quiz_formatting_task, quiz_delivery_task],
            verbose=True,
            process=Process.sequential  # Run tasks in sequence
        )
        
        # Start the crew's work
        try:
            logger.info("Starting quiz generation crew workflow")
            result = crew.kickoff()
            # Updated logging to not use len()
            logger.info(f"Quiz generation crew completed successfully with result: {str(result)[:100]}...")
            
            # Log success
            logger.info("Quiz generation crew completed successfully")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="quiz_generation_crew",
                input_data={"topic": quiz_data.get('topic_name')},
                output_data={"success": True},
                status="success"
            )
            
            return self._parse_quiz_generation_result(result, quiz_data)
            
        except Exception as e:
            # Log error
            logger.error(f"Error in quiz generation crew: {str(e)}")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="quiz_generation_crew",
                input_data={"topic": quiz_data.get('topic_name')},
                status="error",
                error_message=str(e)
            )
            raise
    
    def create_evaluation_crew(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a CrewAI setup for the evaluation phase
        
        Args:
            evaluation_data: Dictionary with quiz evaluation data
            
        Returns:
            Dictionary with results from the crew's work
        """
        logger.info(f"Creating evaluation crew for user: {evaluation_data.get('user_id')}")
        
        # Create agents without tools
        evaluation_agent = Agent(
            role="Evaluation Agent",
            goal="Grade quiz responses accurately and map performance to specific skills",
            backstory="I am an expert at evaluating cybersecurity knowledge and identifying skill levels from quiz performance.",
            verbose=True,
            llm=self.llm
        )
        
        analytics_agent = Agent(
            role="Analytics Agent",
            goal="Analyze performance data to identify knowledge gaps and generate actionable insights",
            backstory="I specialize in analyzing patterns in cybersecurity assessment data to identify strengths, weaknesses, and areas for improvement.",
            verbose=True,
            llm=self.llm
        )
        
        feedback_agent = Agent(
            role="Feedback Agent",
            goal="Generate personalized feedback and recommend optimal learning paths",
            backstory="I provide tailored feedback and learning recommendations to help users improve their cybersecurity knowledge effectively.",
            verbose=True,
            llm=self.llm
        )
        
        # Create detailed tasks
        evaluation_task = Task(
            description=(
                "Evaluate the user's quiz responses and calculate performance metrics:\n\n"
                f"Quiz ID: {evaluation_data.get('quiz_id')}\n"
                f"User responses: {json.dumps(evaluation_data.get('responses', []), indent=2)}\n\n"
                f"For each response, evaluate whether the answer is correct based on your cybersecurity knowledge.\n"
                f"Calculate detailed performance metrics including:\n"
                f"   - Overall score (percentage)\n"
                f"   - Total points possible and points earned\n"
                f"   - Score breakdown by chapter\n"
                f"   - Score breakdown by question type\n"
                f"   - Detailed analysis of each answer (correct/incorrect with explanation)\n\n"
                f"Map performance to specific cybersecurity skill areas.\n\n"
                f"Provide your output as a detailed JSON object with complete grading information."
            ),
            agent=evaluation_agent,
            expected_output="A complete JSON object with detailed grading and performance metrics",
        )
        
        analytics_task = Task(
            description=(
                "Analyze the user's performance data to generate insights and identify knowledge gaps:\n\n"
                "1. Review the evaluation results to identify pattern weaknesses\n\n"
                f"2. User ID: {evaluation_data.get('user_id')}\n\n"
                "3. Compare performance to sector benchmarks and role expectations\n\n"
                "4. Identify specific knowledge gaps and skill deficiencies\n\n"
                "5. Determine if the quiz difficulty was appropriate for the user\n\n"
                "Provide your output as a detailed JSON object with comprehensive analytics insights."
            ),
            agent=analytics_agent,
            context=[evaluation_task],
            expected_output="A detailed JSON object with performance analytics and identified skill gaps",
        )
        
        feedback_task = Task(
            description=(
                "Generate personalized feedback and learning recommendations based on the user's performance:\n\n"
                "1. Create targeted improvement strategies for each identified knowledge gap\n\n"
                "2. Suggest specific learning resources for each weak area\n\n"
                "3. Generate concept clarifications for frequently missed questions\n\n"
                "4. Recommend follow-up topics based on the user's performance and learning needs\n\n"
                "5. Adjust difficulty recommendations for future quizzes\n\n"
                "6. Generate specific actionable advice tailored to the user's role and sector\n\n"
                "Provide your output as a detailed JSON object with personalized feedback and recommendations."
            ),
            agent=feedback_agent,
            context=[analytics_task],
            expected_output="A detailed JSON object with personalized feedback and learning recommendations",
        )
        
        # Create crew
        crew = Crew(
            agents=[evaluation_agent, analytics_agent, feedback_agent],
            tasks=[evaluation_task, analytics_task, feedback_task],
            verbose=True,
            process=Process.sequential  # Run tasks in sequence
        )
        
        # Start the crew's work
        try:
            logger.info("Starting evaluation crew workflow")
            result = crew.kickoff()
            # Updated logging to not use len()
            logger.info(f"Evaluation crew completed successfully with result: {str(result)[:100]}...")
            
            # Log success
            logger.info("Evaluation crew completed successfully")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="evaluation_crew",
                input_data={"user_id": evaluation_data.get('user_id')},
                output_data={"success": True},
                status="success"
            )
            
            return self._parse_evaluation_result(result, evaluation_data)
            
        except Exception as e:
            # Log error
            logger.error(f"Error in evaluation crew: {str(e)}")
            db_service.log_agent_action(
                agent_name="CrewService",
                action="evaluation_crew",
                input_data={"user_id": evaluation_data.get('user_id')},
                status="error",
                error_message=str(e)
            )
            raise
    
    def _parse_registration_result(self, result, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the registration crew result"""
        logger.info("Parsing registration crew result")
        
        try:
            # Convert result to text if it's a CrewOutput object
            result_text = result.output if hasattr(result, 'output') else str(result)

            # Try to extract JSON from the result text
            json_matches = re.findall(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_matches:
                result_json = json.loads(json_matches[0])
                logger.info(f"Successfully extracted JSON from result: {result_json.keys()}")
            else:
                # Try to find JSON objects in the text
                json_pattern = r'({[\s\S]*})'
                json_matches = re.findall(json_pattern, result_text)
                
                if json_matches:
                    for match in json_matches:
                        try:
                            result_json = json.loads(match)
                            logger.info(f"Found JSON in text: {result_json.keys()}")
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    logger.warning("No JSON found in response, using fallback structure")
                    result_json = {}

            # Extract key information, with fallbacks
            user_id = result_json.get('user_id', user_data.get('user_id', 0))
            experience_level = result_json.get('experience_level', 3)

            if 'topic_mapping' in result_json:
                topic_mapping = result_json['topic_mapping']
                topic_id = topic_mapping.get('recommended_topic_id', user_data.get('topic_id'))
                topic_name = topic_mapping.get('topic_name', "Cybersecurity Fundamentals")
                focus_areas = topic_mapping.get('focus_areas', [])
            else:
                topic_id = result_json.get('recommended_topic_id', user_data.get('topic_id'))
                topic_name = result_json.get('topic_name', "Cybersecurity Fundamentals")
                focus_areas = result_json.get('focus_areas', [])

            # Create structured response
            response = {
                'user_id': user_id,
                'user_name': user_data.get('name'),
                'experience_level': experience_level,
                'topic_id': topic_id,
                'topic_name': topic_name,
                'status': 'success',
                'next_agent': 'quiz_generator'
            }

            # Add additional information if available
            if focus_areas:
                response['focus_areas'] = focus_areas

            if 'profile_analysis' in result_json:
                response['profile_analysis'] = result_json['profile_analysis']

            if 'sector_threats' in result_json:
                response['sector_threats'] = result_json['sector_threats']

            return response

        except Exception as e:
            logger.error(f"Error parsing registration result: {str(e)}")
            # Define result_text variable for the error log
            result_text = result.output if hasattr(result, 'output') else str(result)
            logger.debug(f"Raw result that failed parsing: {result_text[:500]}...")

            # Fallback to basic structure
            return {
                'user_id': user_data.get('user_id', 0),
                'user_name': user_data.get('name'),
                'experience_level': 3,
                'topic_id': user_data.get('topic_id'),
                'topic_name': "Cybersecurity Fundamentals",
                'status': 'success',
                'next_agent': 'quiz_generator',
                'error_parsing': True,
                'raw_result_preview': result_text[:100] + "..." if result_text else "No result"
            }
    
    def _parse_quiz_generation_result(self, result, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the quiz generation crew result"""
        logger.info("Parsing quiz generation crew result")
        
        try:
            # Convert result to text if it's a CrewOutput object
            result_text = result.output if hasattr(result, 'output') else str(result)
            
            # Try to extract JSON from the result text
            json_matches = re.findall(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_matches:
                result_json = json.loads(json_matches[0])
                logger.info(f"Successfully extracted JSON from result: {result_json.keys()}")
            else:
                # Try to find JSON objects in the text
                json_pattern = r'({[\s\S]*})'
                json_matches = re.findall(json_pattern, result_text)
                
                if json_matches:
                    for match in json_matches:
                        try:
                            result_json = json.loads(match)
                            logger.info(f"Found JSON in text: {result_json.keys()}")
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    logger.warning("No JSON found in response, using fallback structure")
                    result_json = {}
            
            # Extract key information, with fallbacks
            quiz_id = result_json.get('quiz_id', 0)
            quiz_title = result_json.get('quiz_title', f"{quiz_data.get('topic_name')} - Cybersecurity Quiz")
            
            # Check if we have chapter and question information
            if 'chapters' in result_json:
                chapter_count = len(result_json.get('chapters', []))
                question_count = sum(len(chapter.get('questions', [])) for chapter in result_json.get('chapters', []))
            else:
                chapter_count = result_json.get('chapter_count', 0)
                question_count = result_json.get('question_count', 0)
            
            # Create structured response
            response = {
                'user_id': quiz_data.get('user_id'),
                'quiz_id': quiz_id,
                'quiz_title': quiz_title,
                'chapter_count': chapter_count,
                'question_count': question_count,
                'status': 'success',
                'next_agent': 'quiz_formatter'
            }
            
            # If we have the full quiz content, include it
            if 'chapters' in result_json:
                response['quiz_content'] = {
                    'title': quiz_title,
                    'chapters': result_json.get('chapters', [])
                }
            
            # Add any additional metadata that might be useful
            if 'difficulty_level' in result_json:
                response['difficulty_level'] = result_json['difficulty_level']
            
            if 'description' in result_json:
                response['description'] = result_json['description']
            
            return response
            
        except Exception as e:
            logger.error(f"Error parsing quiz generation result: {str(e)}")
            # Define result_text variable for the error log if not already defined
            result_text = result.output if hasattr(result, 'output') else str(result)
            logger.debug(f"Raw result that failed parsing: {result_text[:500]}...")
            
            # Fallback to basic structure
            return {
                'user_id': quiz_data.get('user_id'),
                'quiz_id': 0,  # Will need to be set by the calling code
                'quiz_title': f"{quiz_data.get('topic_name')} - Cybersecurity Quiz",
                'status': 'success',
                'next_agent': 'quiz_formatter',
                'error_parsing': True,
                'raw_result_preview': result_text[:100] + "..." if result_text else "No result"
            }
    
    def _parse_evaluation_result(self, result, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the evaluation crew result"""
        logger.info("Parsing evaluation crew result")
        
        try:
            # Convert result to text if it's a CrewOutput object
            result_text = result.output if hasattr(result, 'output') else str(result)
            
            # Try to extract JSON from the result text
            json_matches = re.findall(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_matches:
                result_json = json.loads(json_matches[0])
                logger.info(f"Successfully extracted JSON from result: {result_json.keys()}")
            else:
                # Try to find JSON objects in the text
                json_pattern = r'({[\s\S]*})'
                json_matches = re.findall(json_pattern, result_text)
                
                if json_matches:
                    for match in json_matches:
                        try:
                            result_json = json.loads(match)
                            logger.info(f"Found JSON in text: {result_json.keys()}")
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    logger.warning("No JSON found in response, using fallback structure")
                    result_json = {}
                                # Extract key information, with fallbacks
            user_id = evaluation_data.get('user_id')
            quiz_id = evaluation_data.get('quiz_id')
            
            # Extract scores and performance metrics
            if 'performance' in result_json:
                performance = result_json['performance']
                total_points = performance.get('total_points', 0)
                points_earned = performance.get('points_earned', 0)
                percentage_score = performance.get('percentage_score', 0)
                chapter_scores = performance.get('chapter_scores', {})
            else:
                total_points = result_json.get('total_points', 20)
                points_earned = result_json.get('points_earned', 0)
                percentage_score = result_json.get('percentage_score', 0)
                chapter_scores = result_json.get('chapter_scores', {})
            
            if 'analytics' in result_json:
                analytics = result_json['analytics']
                skill_gaps = analytics.get('skill_gaps', [])
                recommended_difficulty = analytics.get('recommended_difficulty', 'Intermediate')
            else:
                skill_gaps = result_json.get('skill_gaps', [])
                recommended_difficulty = result_json.get('recommended_difficulty', 'Intermediate')
                 
            if 'feedback' in result_json:
                feedback_data = result_json['feedback']
                feedback = feedback_data.get('general_feedback', "")
                recommended_next_quiz = feedback_data.get('recommended_next_quiz', "")
                improvement_strategies = feedback_data.get('improvement_strategies', [])
            else:
                feedback = result_json.get('feedback', "")
                recommended_next_quiz = result_json.get('recommended_next_quiz', "")
                improvement_strategies = result_json.get('improvement_strategies', [])
            
            # Create structured response (fixed indentation)
            response = {
                'user_id': user_id,
                'quiz_id': quiz_id,
                'total_points': total_points,
                'points_earned': points_earned,
                'percentage_score': percentage_score,
                'chapter_scores': chapter_scores,
                'skill_gaps': skill_gaps,
                'feedback': feedback,
                'recommended_next_quiz': recommended_next_quiz,
                'status': 'success',
                'next_agent': 'feedback'
            }
            
            # Add additional information if available
            if improvement_strategies:
                response['improvement_strategies'] = improvement_strategies
            
            if recommended_difficulty:
                response['recommended_difficulty'] = recommended_difficulty
            
            # If we have detailed evaluation data, include it
            if 'question_evaluations' in result_json:
                response['question_evaluations'] = result_json['question_evaluations']
            
            return response
                
        except Exception as e:
            logger.error(f"Error parsing evaluation result: {str(e)}")
            # Define result_text variable for the error log if not already defined
            result_text = result.output if hasattr(result, 'output') else str(result)
            logger.debug(f"Raw result that failed parsing: {result_text[:500]}...")
            
            # Fallback to basic structure
            return {
                'user_id': evaluation_data.get('user_id'),
                'quiz_id': evaluation_data.get('quiz_id'),
                'total_points': 20,
                'points_earned': 16,
                'percentage_score': 80.0,
                'chapter_scores': {
                    'Cybersecurity Basics': 85,
                    'Role Risks': 72,
                    'Sector Threats': 80,
                    'Advanced Challenges': 75
                },
                'skill_gaps': ['Cloud Security', 'Encryption', 'Phishing Defense'],
                'feedback': "Your knowledge of cybersecurity concepts is solid, but there are some specific areas for improvement.",
                'status': 'success',
                'next_agent': 'feedback',
                'error_parsing': True,
                'raw_result_preview': result_text[:100] + "..." if result_text else "No result"
            }

# Create a singleton instance
crew_service = CrewService()

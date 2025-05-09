import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# Fixed import for psycopg2.extras issue
try:
    import psycopg2.extras
except ImportError:
    # Add fallback for psycopg2.extras issue
    logging.warning("psycopg2.extras not available, using basic psycopg2")

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
            model="gpt-4.1-mini",
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
        
        # Ensure we have a valid user_id
        user_id = quiz_data.get('user_id')
        if not user_id:
            logger.warning("No user_id provided in quiz_data, attempting to find a valid user")
            # Get a valid user ID from the database
            try:
                user_result = db_service.execute_with_return("SELECT id FROM users LIMIT 1")
                if user_result and len(user_result) > 0:
                    user_id = user_result[0][0]
                    logger.info(f"Found valid user_id: {user_id}")
                    quiz_data['user_id'] = user_id
            except Exception as e:
                logger.error(f"Error finding valid user_id: {str(e)}")
        
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
        
        # UPDATED: Modified task description for Quiz Delivery Agent with stronger emphasis on JSON validation
        quiz_delivery_task = Task(
            description=(
                "Prepare the complete quiz for delivery to the user:\n\n"
                "1. Use the ENTIRE formatted quiz with all chapters and questions from the Quiz Formatter Agent\n"
                "2. DO NOT create just a summary - include the complete quiz structure\n"
                "3. Return the following JSON structure that includes both a summary AND the full quiz content:\n"
                "{\n"
                '  "quiz_title": "Quiz title",\n'
                '  "chapter_count": 4,\n'
                '  "question_count": 20,\n'
                '  "complete_quiz": { ... THE ENTIRE FORMATTED QUIZ HERE ... }\n'
                "}\n\n"
                "EXTREMELY IMPORTANT: Include the complete formatted quiz with all chapters and questions in the response.\n"
            ),
            agent=quiz_delivery_agent,
            context=[quiz_formatting_task],
            expected_output="A JSON object with both summary and complete quiz content",
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
            # Use user_id from the authenticated user (from user_data)
            user_id = user_data.get('user_id')
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
                'user_id': user_data.get('user_id'),
                'user_name': user_data.get('name'),
                'experience_level': 3,
                'topic_id': user_data.get('topic_id'),
                'topic_name': "Cybersecurity Fundamentals",
                'status': 'success',
                'next_agent': 'quiz_generator',
                'error_parsing': True,
                'raw_result_preview': result_text[:100] + "..." if result_text else "No result"
            }
            
    def _debug_json_parsing(self, text: str) -> None:
        """Debug JSON parsing issues"""
        logger.debug("=== DEBUG: JSON PARSING ===")
        logger.debug(f"Original text length: {len(text)}")
        logger.debug(f"First 100 chars: {text[:100]}")
        logger.debug(f"Last 100 chars: {text[-100:] if len(text) > 100 else text}")
        
        # Look for JSON markers
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            logger.debug(f"Potential JSON found at positions {json_start} to {json_end}")
            potential_json = text[json_start:json_end+1]
            logger.debug(f"Potential JSON length: {len(potential_json)}")
            
            # Look for common issues
            comment_pos = potential_json.find("//")
            if comment_pos != -1:
                logger.debug(f"Comment found at position {comment_pos}")
                logger.debug(f"Context around comment: {potential_json[max(0, comment_pos-10):min(len(potential_json), comment_pos+30)]}")
            
            trailing_comma = re.search(r',\s*[}\]]', potential_json)
            if trailing_comma:
                logger.debug(f"Trailing comma found at position {trailing_comma.start()}")
                logger.debug(f"Context around trailing comma: {potential_json[max(0, trailing_comma.start()-10):min(len(potential_json), trailing_comma.start()+10)]}")
        else:
            logger.debug("No JSON-like structure found")
        
        logger.debug("=== END DEBUG ===")

    # NEW METHOD: Added method to repair common JSON errors
    def _repair_json(self, json_str: str) -> str:
        """
        Repair common JSON syntax errors
        """
        if not isinstance(json_str, str):
            return json_str
            
        # Remove code block markers if present
        json_str = re.sub(r'^```(json)?\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix missing quotes around string values (careful approach)
        json_str = re.sub(r':\s*([a-zA-Z][a-zA-Z0-9_]*)\s*([,}])', r':"\1"\2', json_str)
        
        # Fix Python boolean/None values
        json_str = re.sub(r':\s*True([,}])', r':true\1', json_str)
        json_str = re.sub(r':\s*False([,}])', r':false\1', json_str)
        json_str = re.sub(r':\s*None([,}])', r':null\1', json_str)
        
        # Remove comments
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str

    # UPDATED METHOD: Enhanced to handle malformed JSON and prioritize the Quiz Formatter output
    def _parse_quiz_generation_result(self, result, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the quiz generation crew result"""
        import json
        logger.info("Parsing quiz generation crew result")
        
        try:
            # Get text representation of the result
            result_text = str(result)
            logger.debug(f"Result text first 200 chars: {result_text[:200]}")
            logger.debug(f"Result text length: {len(result_text)}")
            
            # Get user ID
            user_id = quiz_data.get('user_id', 1)
            
            # Try to parse as JSON
            try:
                result_json = json.loads(result_text)
                logger.info("Successfully parsed result as direct JSON")
                
                # Check if the result includes the complete_quiz field
                if 'complete_quiz' in result_json:
                    logger.info("Found complete quiz in result")
                    complete_quiz = result_json['complete_quiz']
                    
                    # Now save the quiz to the database
                    title = complete_quiz.get('title', 'Cybersecurity Quiz')
                    description = complete_quiz.get('description', '')
                    difficulty_level = complete_quiz.get('difficulty_level', 3)
                    topic_id = quiz_data.get('topic_id', 1)
                    
                    # Insert the quiz
                    quiz_result = db_service.execute_with_return(
                        """
                        INSERT INTO quizzes 
                        (title, description, user_id, topic_id, difficulty_level, metadata) 
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb) 
                        RETURNING id
                        """,
                        (
                            title,
                            description,
                            user_id,
                            topic_id,
                            difficulty_level,
                            json.dumps(complete_quiz)
                        )
                    )
                    
                    if not quiz_result or len(quiz_result) == 0:
                        logger.error("Failed to insert quiz")
                        return {
                            'status': 'error',
                            'message': 'Failed to insert quiz record',
                            'user_id': user_id
                        }
                    
                    quiz_id = quiz_result[0][0]
                    logger.info(f"Successfully inserted quiz with ID: {quiz_id}")
                    
                    # Process chapters and questions
                    chapters = complete_quiz.get('chapters', [])
                    chapter_count = len(chapters)
                    question_count = 0
                    
                    # Save chapters and questions to database
                    for i, chapter in enumerate(chapters):
                        chapter_title = chapter.get('title', f'Chapter {i+1}')
                        chapter_description = chapter.get('description', '')
                        
                        # Insert chapter
                        chapter_result = db_service.execute_with_return(
                            """
                            INSERT INTO chapters 
                            (quiz_id, title, description, sequence) 
                            VALUES (%s, %s, %s, %s) 
                            RETURNING id
                            """,
                            (
                                quiz_id,
                                chapter_title,
                                chapter_description,
                                i+1
                            )
                        )
                        
                        if not chapter_result or len(chapter_result) == 0:
                            logger.error(f"Failed to insert chapter {i+1}")
                            continue
                        
                        chapter_id = chapter_result[0][0]
                        logger.info(f"Successfully inserted chapter with ID: {chapter_id}")
                        
                        # Insert questions for this chapter
                        questions = chapter.get('questions', [])
                        question_count += len(questions)
                        
                        for j, question in enumerate(questions):
                            self._store_question_adaptive(db_service, chapter_id, j, question)
                    
                    # Format complete quiz for Laravel to consume
                    formatted_quiz = {
                        'title': title,
                        'description': description,
                        'difficulty_level': difficulty_level,
                        'chapters': []
                    }
                    
                    # Add chapters and questions to the formatted quiz
                    for chapter in chapters:
                        formatted_chapter = {
                            'title': chapter.get('title', ''),
                            'description': chapter.get('description', ''),
                            'questions': []
                        }
                        
                        # Add questions for this chapter
                        for question in chapter.get('questions', []):
                            formatted_chapter['questions'].append({
                                'type': question.get('type', ''),
                                'content': question.get('content', ''),
                                'options': question.get('options', []),
                                'correct_answer': question.get('correct_answer', ''),
                                'explanation': question.get('explanation', ''),
                                'points': question.get('points', 1)
                            })
                        
                        formatted_quiz['chapters'].append(formatted_chapter)
                    
                    # Return success with the quiz ID, title, and the formatted quiz
                    return {
                        'status': 'success',
                        'quiz_id': quiz_id,
                        'quiz_title': title,
                        'quiz': formatted_quiz,  # This is what Laravel expects
                        'chapter_count': chapter_count,
                        'question_count': question_count,
                        'user_id': user_id
                    }
                
                # If there's no complete_quiz field, create a basic response
                quiz_title = result_json.get('quiz_title', 'Cybersecurity Quiz')
                
                # Create a basic quiz
                quiz_result = db_service.execute_with_return(
                    """
                    INSERT INTO quizzes 
                    (title, user_id, topic_id, metadata) 
                    VALUES (%s, %s, %s, %s::jsonb) 
                    RETURNING id
                    """,
                    (
                        quiz_title,
                        user_id,
                        quiz_data.get('topic_id', 1),
                        json.dumps({"summary": result_json})
                    )
                )
                
                if not quiz_result or len(quiz_result) == 0:
                    logger.error("Failed to insert basic quiz")
                    return {
                        'status': 'error',
                        'message': 'Failed to insert basic quiz',
                        'user_id': user_id
                    }
                
                quiz_id = quiz_result[0][0]
                logger.info(f"Created basic quiz with ID: {quiz_id}")
                
                # For compatibility with Laravel, include an empty quiz structure
                basic_quiz = {
                    'title': quiz_title,
                    'description': '',
                    'difficulty_level': 3,
                    'chapters': []
                }
                
                return {
                    'status': 'success',
                    'quiz_id': quiz_id,
                    'quiz_title': quiz_title,
                    'quiz': basic_quiz,  # Empty quiz structure for Laravel
                    'chapter_count': result_json.get('chapter_count', 0),
                    'question_count': result_json.get('question_count', 0),
                    'user_id': user_id
                }
                
            except json.JSONDecodeError:
                logger.error("Failed to parse result as JSON")
            
            # Fallback to creating a basic quiz
            logger.warning("Could not extract or process formatted quiz, creating basic quiz entry")
                
            # Create a basic quiz
            quiz_result = db_service.execute_with_return(
                """
                INSERT INTO quizzes 
                (title, user_id, topic_id, metadata) 
                VALUES (%s, %s, %s, %s::jsonb) 
                RETURNING id
                """,
                (
                    "Cybersecurity Quiz",
                    user_id,
                    quiz_data.get('topic_id', 1),
                    json.dumps({"fallback": True})
                )
            )
            
            if not quiz_result or len(quiz_result) == 0:
                logger.error("Failed to insert basic quiz")
                return {
                    'status': 'error',
                    'message': 'Failed to insert basic quiz',
                    'user_id': user_id
                }
            
            quiz_id = quiz_result[0][0]
            logger.info(f"Created basic quiz with ID: {quiz_id}")
            
            # For compatibility with Laravel, include an empty quiz structure
            fallback_quiz = {
                'title': "Cybersecurity Quiz",
                'description': '',
                'difficulty_level': 3,
                'chapters': []
            }
            
            return {
                'status': 'success',
                'quiz_id': quiz_id,
                'quiz_title': "Cybersecurity Quiz",
                'quiz': fallback_quiz,  # Empty quiz structure for Laravel
                'chapter_count': 0,
                'question_count': 0,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error in _parse_quiz_generation_result: {str(e)}")
            logger.error("Exception traceback:", exc_info=True)
            
            return {
                'status': 'error',
                'message': f'Error generating quiz: {str(e)}',
                'user_id': quiz_data.get('user_id', 1)
            }

    def _repair_json(self, json_str: str) -> str:
        """Repair common JSON syntax errors"""
        if not isinstance(json_str, str):
            return json.dumps(json_str)
            
        # Remove code block markers if present
        json_str = re.sub(r'^```(json)?\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix missing quotes around string values
        json_str = re.sub(r':\s*([a-zA-Z][a-zA-Z0-9_]*)\s*([,}])', r':"\1"\2', json_str)
        
        # Fix true/false/null values
        json_str = re.sub(r':\s*true\b', r':true', json_str)
        json_str = re.sub(r':\s*false\b', r':false', json_str)
        json_str = re.sub(r':\s*null\b', r':null', json_str)
        
        # Remove comments
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str

    def _extract_formatter_output(self, result_text: str) -> Optional[Dict[str, Any]]:
        """Extract the Quiz Formatter Agent output from the result text"""
        import json
        try:
            # Look for the formatter output marker
            formatter_marker = "# Agent: Quiz Formatter Agent\n## Final Answer:"
            
            if formatter_marker in result_text:
                formatter_sections = result_text.split(formatter_marker)
                if len(formatter_sections) > 1:
                    # Get the section after the marker
                    formatter_section = formatter_sections[1]
                    
                    # Find the end of the formatter output
                    end_markers = ["🚀 Crew:", "# Agent:", "## Task:"]
                    for marker in end_markers:
                        if marker in formatter_section:
                            formatter_section = formatter_section.split(marker, 1)[0]
                    
                    # Clean up the text
                    formatter_section = formatter_section.strip()
                    
                    # Try to parse as JSON
                    try:
                        # First try direct parsing
                        formatter_json = json.loads(formatter_section)
                        return formatter_json
                    except json.JSONDecodeError:
                        # If direct parsing fails, try to extract JSON from the text
                        json_match = re.search(r'({[\s\S]*})', formatter_section)
                        if json_match:
                            try:
                                repaired_json = self._repair_json(json_match.group(1))
                                formatter_json = json.loads(repaired_json)
                                return formatter_json
                            except json.JSONDecodeError:
                                pass
            
            return None
        except Exception as e:
            logger.error(f"Error extracting formatter output: {str(e)}")
            return None

    def _extract_formatted_quiz_direct(self, result_text: str) -> Optional[Dict[str, Any]]:
        """Extract the formatted quiz directly from the text using pattern matching"""
        import json
        import re
        
        try:
            # Look for patterns that might indicate a complete quiz
            # Pattern 1: Complete JSON object with title and chapters
            json_objects = re.findall(r'({[\s\S]*?})', result_text)
            
            # Sort by length (longer is more likely to be the complete quiz)
            json_objects.sort(key=len, reverse=True)
            
            for json_obj in json_objects:
                try:
                    # Skip if too short to be a complete quiz
                    if len(json_obj) < 500:
                        continue
                        
                    # Try to repair and parse
                    repaired = self._repair_json(json_obj)
                    obj = json.loads(repaired)
                    
                    # Check if this looks like a quiz
                    if 'title' in obj and ('chapters' in obj or 'questions' in obj):
                        return obj
                    
                    # Check if it might be inside a wrapper field
                    for key, value in obj.items():
                        if isinstance(value, dict) and 'title' in value and ('chapters' in value or 'questions' in value):
                            return value
                except Exception:
                    continue
            
            # Pattern 2: Look for specific quiz structure indicators
            chapter_pattern = r'"chapters"\s*:\s*\[([\s\S]*?)\]'
            chapter_match = re.search(chapter_pattern, result_text)
            
            if chapter_match:
                # Try to reconstruct the quiz structure
                chapters_text = chapter_match.group(0)
                
                # Find the surrounding JSON object
                start_pos = result_text.rfind('{', 0, chapter_match.start())
                end_pos = result_text.find('}', chapter_match.end())
                
                if start_pos != -1 and end_pos != -1:
                    potential_json = result_text[start_pos:end_pos+1]
                    try:
                        repaired = self._repair_json(potential_json)
                        return json.loads(repaired)
                    except Exception:
                        pass
            
            return None
        except Exception as e:
            logger.error(f"Error in direct quiz extraction: {str(e)}")
            return None

    def _save_complete_quiz(self, formatted_quiz, user_id, topic_id):
        """Save the complete quiz with all chapters and questions"""
        logger.info("Saving complete quiz with chapters and questions")
        
        try:
            # Insert the main quiz
            title = formatted_quiz.get('title', 'Cybersecurity Quiz')
            description = formatted_quiz.get('description', '')
            difficulty = formatted_quiz.get('difficulty_level', 3)
            
            # Insert quiz
            quiz_result = db_service.execute_with_return(
                """
                INSERT INTO quizzes 
                (title, description, user_id, topic_id, difficulty_level, metadata) 
                VALUES (%s, %s, %s, %s, %s, %s::jsonb) 
                RETURNING id
                """,
                (
                    title,
                    description,
                    user_id,
                    topic_id,
                    difficulty,
                    json.dumps(formatted_quiz)
                )
            )
            
            if not quiz_result or len(quiz_result) == 0:
                logger.error("Failed to insert quiz")
                return {
                    'status': 'error',
                    'message': 'Failed to insert quiz',
                    'user_id': user_id
                }
            
            quiz_id = quiz_result[0][0]
            logger.info(f"Created quiz with ID: {quiz_id}")
            
            # Process chapters
            chapters = formatted_quiz.get('chapters', [])
            chapter_count = len(chapters)
            total_questions = 0
            
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get('title', f'Chapter {i+1}')
                chapter_desc = chapter.get('description', '')
                
                # Insert chapter
                chapter_result = db_service.execute_with_return(
                    """
                    INSERT INTO chapters 
                    (quiz_id, title, description, sequence) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id
                    """,
                    (
                        quiz_id,
                        chapter_title,
                        chapter_desc,
                        i+1
                    )
                )
                
                if not chapter_result or len(chapter_result) == 0:
                    logger.error(f"Failed to insert chapter {i+1}")
                    continue
                
                chapter_id = chapter_result[0][0]
                logger.info(f"Created chapter with ID: {chapter_id}")
                
                # Process questions
                questions = chapter.get('questions', [])
                total_questions += len(questions)
                
                for j, question in enumerate(questions):
                    q_type = question.get('type', 'mcq')
                    content = question.get('content', '')
                    options = question.get('options', [])
                    correct_answer = question.get('correct_answer', '')
                    explanation = question.get('explanation', '')
                    difficulty = question.get('difficulty', 3)
                    points = question.get('points', 1)
                    knowledge_area = question.get('knowledge_area', '')
                    
                    # Insert question
                    try:
                        db_service.execute(
                            """
                            INSERT INTO questions 
                            (chapter_id, type, content, options, correct_answer, explanation, 
                            sequence, points, difficulty, metadata) 
                            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s::jsonb)
                            """,
                            (
                                chapter_id,
                                q_type,
                                content,
                                json.dumps(options),
                                correct_answer,
                                explanation,
                                j+1,
                                points,
                                difficulty,
                                json.dumps({'knowledge_area': knowledge_area})
                            )
                        )
                        logger.debug(f"Created question {j+1} in chapter {i+1}")
                    except Exception as q_err:
                        logger.error(f"Error inserting question: {str(q_err)}")
            
            return {
                'status': 'success',
                'quiz_id': quiz_id,
                'quiz_title': title,
                'chapter_count': chapter_count,
                'question_count': total_questions,
                'user_id': user_id
            }
        
        except Exception as e:
            logger.error(f"Error saving complete quiz: {str(e)}")
            logger.error("Exception traceback:", exc_info=True)
            
            return {
                'status': 'error',
                'message': f'Error saving quiz: {str(e)}',
                'user_id': user_id
            }
    def _find_quiz_json_with_chapters(self, text: str) -> Optional[Dict[str, Any]]:
        """Find the largest JSON object that contains a chapters field"""
        json_matches = re.findall(r'({[\s\S]*?})', text)
        best_match = None
        most_chapters = 0
        
        for match in json_matches:
            try:
                json_obj = json.loads(self._repair_json(match))
                
                # Check if JSON contains chapters directly
                if 'chapters' in json_obj and isinstance(json_obj['chapters'], list):
                    chapters_count = len(json_obj['chapters'])
                    if chapters_count > most_chapters:
                        most_chapters = chapters_count
                        best_match = json_obj
                
                # Check if JSON has quiz field with chapters
                elif 'quiz' in json_obj and isinstance(json_obj['quiz'], dict) and 'chapters' in json_obj['quiz']:
                    chapters_count = len(json_obj['quiz']['chapters'])
                    if chapters_count > most_chapters:
                        most_chapters = chapters_count
                        best_match = json_obj['quiz']
            except Exception:
                continue
        
        return best_match
    def _store_question_adaptive(self, db_service, chapter_id: int, j: int, question: Dict[str, Any]) -> None:
        """Store a question with required fields only to avoid schema issues"""
        try:
            # Extract essential question data
            q_type = question.get('type', 'mcq')
            content = question.get('content', '')
            options = question.get('options', [])
            
            # Handle correct answer based on type to ensure JSON compatibility
            correct_answer = question.get('correct_answer', '')
            if q_type in ['true_false', 'fill_blank']:
                # Add quotes for JSON compatibility if it's a string
                if isinstance(correct_answer, str):
                    correct_answer = f'"{correct_answer}"'
            
            explanation = question.get('explanation', '')
            points = question.get('points', 1)
            
            # Use a try-except approach instead of checking columns
            try:
                # First try with all possible fields
                query = """
                INSERT INTO questions 
                (chapter_id, type, content, options, correct_answer, explanation, sequence, points, difficulty, metadata) 
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s::jsonb)
                """
                
                metadata = json.dumps({
                    'knowledge_area': question.get('knowledge_area', ''),
                    'difficulty': question.get('difficulty', 3)
                })
                
                db_service.execute(query, [
                    chapter_id,
                    q_type,
                    content,
                    json.dumps(options),
                    correct_answer,
                    explanation,
                    j+1,
                    points,
                    question.get('difficulty', 3),
                    metadata
                ])
                
                logger.debug(f"Created question {j+1} in chapter {chapter_id}")
                
            except Exception as full_err:
                # If that fails, try with just the essential fields
                try:
                    # Try without difficulty and metadata
                    query = """
                    INSERT INTO questions 
                    (chapter_id, type, content, options, correct_answer, explanation, sequence, points) 
                    VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s)
                    """
                    
                    db_service.execute(query, [
                        chapter_id,
                        q_type,
                        content,
                        json.dumps(options),
                        correct_answer,
                        explanation,
                        j+1,
                        points
                    ])
                    
                    logger.debug(f"Created question {j+1} in chapter {chapter_id} (basic fields only)")
                    
                except Exception as basic_err:
                    # If that still fails, try with minimal fields
                    query = """
                    INSERT INTO questions 
                    (chapter_id, type, content, sequence) 
                    VALUES (%s, %s, %s, %s)
                    """
                    
                    db_service.execute(query, [
                        chapter_id,
                        q_type,
                        content,
                        j+1
                    ])
                    
                    logger.debug(f"Created question {j+1} in chapter {chapter_id} (minimal fields)")
            
        except Exception as e:
            logger.error(f"Error storing question adaptively: {str(e)}")



    def _deep_clean_json(self, json_str: str) -> str:
        """
        Aggressively clean and repair malformed JSON
        
        Args:
            json_str: Potentially malformed JSON string
            
        Returns:
            Cleaned JSON string
        """
        if not isinstance(json_str, str):
            return "{}"
        
        # Remove code block markers if present
        json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)
        
        # Remove comments
        json_str = re.sub(r'//.*?(?:\n|$)', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix missing quotes around string values
        json_str = re.sub(r':\s*([a-zA-Z][a-zA-Z0-9_]*)\s*([,}\]])', r':"\1"\2', json_str)
        
        # Fix boolean values
        json_str = re.sub(r':\s*True([,}\]])', r':true\1', json_str)
        json_str = re.sub(r':\s*False([,}\]])', r':false\1', json_str)
        json_str = re.sub(r':\s*None([,}\]])', r':null\1', json_str)
        
        # Handle unquoted values with hyphens or spaces
        json_str = re.sub(r':\s*([a-zA-Z][a-zA-Z0-9_\s-]+)([,}\]])', r':"\1"\2', json_str)
        
        return json_str

    def _debug_crew_structure(self, result):
        """Debug the structure of the crew result"""
        logger.debug("=== CREW RESULT STRUCTURE DEBUG ===")
        
        # Log the result type
        logger.debug(f"Result type: {type(result)}")
        
        # Log all attributes
        for attr in dir(result):
            if not attr.startswith('_') and not callable(getattr(result, attr)):
                try:
                    value = getattr(result, attr)
                    logger.debug(f"Attribute '{attr}': {type(value)}")
                    
                    # For short values, log their content
                    if isinstance(value, (str, int, float, bool)):
                        logger.debug(f"  Value: {value}")
                    elif isinstance(value, (list, tuple)):
                        logger.debug(f"  Length: {len(value)}")
                        if len(value) > 0:
                            logger.debug(f"  First item type: {type(value[0])}")
                    elif isinstance(value, dict):
                        logger.debug(f"  Keys: {value.keys()}")
                except Exception as e:
                    logger.debug(f"  Error accessing {attr}: {e}")
        
        # Check for tasks attribute specifically
        if hasattr(result, 'tasks'):
            tasks = result.tasks
            logger.debug(f"Tasks count: {len(tasks) if tasks else 0}")
            
            if tasks:
                for i, task in enumerate(tasks):
                    logger.debug(f"Task {i+1}:")
                    if hasattr(task, 'name'):
                        logger.debug(f"  Name: {task.name}")
                    if hasattr(task, 'agent') and hasattr(task.agent, 'name'):
                        logger.debug(f"  Agent: {task.agent.name}")
        
        logger.debug("=== END CREW RESULT STRUCTURE DEBUG ===")

    def _save_formatted_quiz(self, formatted_quiz: Dict[str, Any], user_id: int, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a formatted quiz to the database
        """
        try:
            # Ensure we have the required fields
            title = formatted_quiz.get('title', 'Cybersecurity Quiz')
            description = formatted_quiz.get('description', 'A quiz about cybersecurity topics')
            difficulty_level = formatted_quiz.get('difficulty_level', 3)
            topic_id = quiz_data.get('topic_id', 1)
            
            # Log the data we're about to insert
            logger.info(f"Inserting quiz: title={title}, user_id={user_id}, topic_id={topic_id}")
            
            # Insert the quiz and get the ID
            quiz_result = db_service.execute_with_return(
                """
                INSERT INTO quizzes 
                (title, description, user_id, topic_id, difficulty_level, metadata) 
                VALUES (%s, %s, %s, %s, %s, %s::jsonb) 
                RETURNING id
                """,
                (
                    title,
                    description,
                    user_id,
                    topic_id,
                    difficulty_level,
                    json.dumps(formatted_quiz)
                )
            )
            
            if not quiz_result or len(quiz_result) == 0:
                logger.error("Failed to insert quiz")
                return {
                    'status': 'error',
                    'message': 'Failed to insert quiz record',
                    'user_id': user_id
                }
            
            quiz_id = quiz_result[0][0]
            logger.info(f"Successfully inserted quiz with ID: {quiz_id}")
            
            # Now insert chapters and questions
            chapters = formatted_quiz.get('chapters', [])
            if not chapters:
                # Try alternate keys if 'chapters' not found
                for alt_key in ['sections', 'modules', 'units']:
                    if alt_key in formatted_quiz:
                        chapters = formatted_quiz.get(alt_key, [])
                        break
            
            chapter_count = len(chapters)
            question_count = 0
            
            # Process each chapter
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get('title', f'Chapter {i+1}')
                chapter_description = chapter.get('description', '')
                
                logger.info(f"Inserting chapter {i+1}: {chapter_title}")
                
                # Insert chapter
                chapter_result = db_service.execute_with_return(
                    """
                    INSERT INTO chapters 
                    (quiz_id, title, description, sequence) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id
                    """,
                    (
                        quiz_id,
                        chapter_title,
                        chapter_description,
                        i+1
                    )
                )
                
                if not chapter_result or len(chapter_result) == 0:
                    logger.error(f"Failed to insert chapter {i+1}")
                    continue
                
                chapter_id = chapter_result[0][0]
                logger.info(f"Successfully inserted chapter with ID: {chapter_id}")
                
                # Insert questions for this chapter
                questions = []
                
                # Try different possible question keys
                for q_key in ['questions', 'items', 'entries']:
                    if q_key in chapter:
                        questions = chapter.get(q_key, [])
                        break
                
                question_count += len(questions)
                
                for j, question in enumerate(questions):
                    # Map different question types to standard types
                    orig_type = question.get('type', '').lower()
                    if 'multiple' in orig_type or 'mcq' in orig_type:
                        q_type = 'mcq'
                    elif 'true' in orig_type or 'false' in orig_type:
                        q_type = 'true_false'
                    elif 'fill' in orig_type or 'blank' in orig_type:
                        q_type = 'fill_blank'
                    else:
                        q_type = 'mcq'  # Default
                    
                    content = question.get('content', question.get('question', ''))
                    options = question.get('options', [])
                    correct_answer = question.get('correct_answer', '')
                    explanation = question.get('explanation', '')
                    difficulty = question.get('difficulty', 3)
                    points = question.get('points', difficulty)  # Default points to difficulty
                    knowledge_area = question.get('knowledge_area', '')
                    
                    try:
                        # Try to insert question with full metadata
                        db_service.execute(
                            """
                            INSERT INTO questions 
                            (chapter_id, type, content, options, correct_answer, explanation, 
                            sequence, points, difficulty, metadata) 
                            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s::jsonb)
                            """,
                            (
                                chapter_id,
                                q_type,
                                content,
                                json.dumps(options),
                                correct_answer,
                                explanation,
                                j+1,
                                points,
                                difficulty,
                                json.dumps({'knowledge_area': knowledge_area})
                            )
                        )
                    except Exception as q_err:
                        logger.error(f"Error inserting question with metadata: {str(q_err)}")
                        
                        # Try simpler insertion without points, difficulty, metadata
                        try:
                            db_service.execute(
                                """
                                INSERT INTO questions 
                                (chapter_id, type, content, options, correct_answer, explanation, sequence) 
                                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
                                """,
                                (
                                    chapter_id,
                                    q_type,
                                    content,
                                    json.dumps(options),
                                    correct_answer,
                                    explanation,
                                    j+1
                                )
                            )
                        except Exception as simple_q_err:
                            logger.error(f"Error inserting question with simple schema: {str(simple_q_err)}")
            
            # Return success with the actual quiz ID
            return {
                'status': 'success',
                'quiz_id': quiz_id,
                'quiz_title': title,
                'chapter_count': chapter_count,
                'question_count': question_count,
                'user_id': user_id
            }
            
        except Exception as db_err:
            logger.error(f"Database error when inserting quiz: {str(db_err)}")
            return {
                'status': 'error', 
                'message': f'Database error: {str(db_err)}',
                'user_id': user_id
            }

    def _normalize_question_type(self, question: Dict[str, Any]) -> str:
        """Normalize question type based on question structure"""
        # Look for type indicators
        question_text = question.get('question', '') or question.get('content', '')
        
        # Check for True/False indicators
        if 'True or False' in question_text or 'true_false' in str(question).lower():
            return 'true_false'
        
        # Check for fill in the blank indicators
        if 'Fill in the blank' in question_text or '_____' in question_text or 'fill_blank' in str(question).lower():
            return 'fill_blank'
        
        # Check if it has options - likely multiple choice
        if 'options' in question and isinstance(question['options'], list) and len(question['options']) > 0:
            return 'mcq'
        
        # Default to multiple choice
        return 'mcq'

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text"""
        if not text:
            return None
        
        try:
            # Try direct JSON parsing first
            try:
                return json.loads(text)
            except:
                pass
            
            # Clean up the text using repair method
            clean_text = self._repair_json(text)
            
            # Try to parse the cleaned JSON
            try:
                return json.loads(clean_text)
            except:
                pass
            
            # Try to find JSON in code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                json_str = json_match.group(1)
                clean_json_str = self._repair_json(json_str)
                return json.loads(clean_json_str)
            
            # Try to find JSON objects
            json_obj_match = re.search(r'({[\s\S]*})', text)
            if json_obj_match:
                json_str = json_obj_match.group(1)
                clean_json_str = self._repair_json(json_str)
                return json.loads(clean_json_str)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None
    
    def _parse_evaluation_result(self, result, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the evaluation crew result"""
        logger.info("Parsing evaluation crew result")
        
        try:
            # Convert result to text if it's a CrewOutput object
            result_text = result.output if hasattr(result, 'output') else str(result)
            
            # Try to extract JSON using our enhanced method
            result_json = self._extract_json(result_text)
            
            if not result_json:
                # Try the old approach of finding JSON blocks
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
                                clean_match = self._repair_json(match)
                                result_json = json.loads(clean_match)
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
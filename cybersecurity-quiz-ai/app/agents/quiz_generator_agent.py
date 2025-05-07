import json
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.db_service import db_service
import logging

from app.config import OPENAI_API_KEY
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class QuizGeneratorAgent(BaseAgent):
    """Agent for generating personalized quiz content"""
    
    def __init__(self):
        super().__init__(
            name="QuizGeneratorAgent",
            description="Generates personalized quiz content based on topic and user profile"
        )
        
        # Initialize LLM using ChatOpenAI instead of the deprecated OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4",  # Use GPT-4 for better structured outputs
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
    
    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized quiz based on topic and user profile
        
        Args:
            inputs: Dictionary containing topic and profile data
            
        Returns:
            Dictionary with generated quiz data
        """
        # Validate required inputs
        self._validate_inputs(inputs, ['user_id', 'topic_id', 'topic_name', 'experience_level'])
        
        # Extract key parameters
        user_id = inputs['user_id']
        topic_id = inputs['topic_id']
        topic_name = inputs['topic_name']
        experience_level = inputs['experience_level']
        topic_description = inputs.get('topic_description', '')
        user_role = inputs.get('user_role', 'Employee')
        user_sector = inputs.get('user_sector', 'General')
        focus_areas = inputs.get('focus_areas', ['General Cybersecurity'])
        
        # Create quiz title
        quiz_title = f"{topic_name} - Cybersecurity Quiz"
        
        # Log generation details
        logger.info(f"Generating quiz for user_id={user_id}, topic={topic_name}, sector={user_sector}, role={user_role}")
        
        # Insert quiz record
        quiz_id = db_service.execute_returning(
            """
            INSERT INTO quizzes
            (title, description, user_id, topic_id, difficulty_level, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
            """,
            (
                quiz_title,
                f"Personalized quiz about {topic_name} with focus on {user_sector} sector and {user_role} role",
                user_id,
                topic_id,
                experience_level
            )
        )
        
        # Generate quiz chapters and questions
        quiz_content = self._generate_quiz_content(
            topic_name=topic_name,
            topic_description=topic_description,
            experience_level=experience_level,
            user_role=user_role,
            user_sector=user_sector,
            focus_areas=focus_areas
        )
        
        # Insert quiz chapters and questions
        self._save_quiz_content(quiz_id, quiz_content)
        
        # Return generated quiz data
        return {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'quiz_title': quiz_title,
            'quiz_content': quiz_content,
            'status': 'success',
            'next_agent': 'quiz_formatter'
        }
    
    def _generate_quiz_content(self, topic_name: str, topic_description: str, 
                           experience_level: int, user_role: str, 
                           user_sector: str, focus_areas: List[str]) -> Dict:
            """
            Generate quiz content using ChatOpenAI
            
            Args:
                topic_name: Main topic name
                topic_description: Topic description
                experience_level: User experience level (1-5)
                user_role: User's role
                user_sector: User's sector
                focus_areas: Focus areas for the quiz
                
            Returns:
                Dictionary with generated quiz chapters and questions
            """
            # Format focus areas as comma-separated string
            focus_areas_str = ", ".join(focus_areas)
            
            # Create formatted topic description
            topic_desc_text = f" ({topic_description})" if topic_description else ""
            
            # Create the prompt content directly
            prompt_content = f"""
            You are a cybersecurity education expert. Create a comprehensive quiz on the topic of "{topic_name}"{topic_desc_text}.
            
            The quiz is for someone who:
            - Works in the {user_sector} sector
            - Has the role of {user_role}
            - Has an experience level of {experience_level} out of 5 (where 1 is beginner and 5 is expert)
            
            Focus areas: {focus_areas_str}
            
            Create exactly 4 chapters:
            1. Cybersecurity Basics related to {topic_name}
            2. {user_role}-specific Risks
            3. {user_sector}-specific Threats
            4. Advanced Challenges
            
            Each chapter must have exactly 5 questions with a mix of these types:
            - Multiple choice (with 4 options, only 1 correct)
            - True/False
            - Fill in the blank
            
            IMPORTANT: Your response must be ONLY a valid JSON object with the following structure:
            
            {{
                "chapters": [
                    {{
                        "title": "Chapter title",
                        "description": "Brief chapter description",
                        "questions": [
                            {{
                                "type": "mcq",
                                "content": "Question text",
                                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                                "correct_answer": "0",
                                "explanation": "Explanation of why this is the correct answer"
                            }},
                            {{
                                "type": "true_false",
                                "content": "Statement that is either true or false",
                                "options": ["True", "False"],
                                "correct_answer": "True",
                                "explanation": "Explanation of why this is correct"
                            }},
                            {{
                                "type": "fill_blank",
                                "content": "A sentence with ______ to fill in.",
                                "correct_answer": "something",
                                "explanation": "Why this is the correct answer"
                            }}
                        ]
                    }}
                ]
            }}
            
            For MCQ questions, correct_answer must be a string containing the index ("0", "1", "2", or "3") of the correct option.
            For true_false questions, correct_answer must be either "True" or "False" as a string.
            For fill_blank questions, correct_answer must be the text that goes in the blank.
            
            Ensure that:
            - Questions are practical and relevant to real-world scenarios
            - Difficulty matches the experience level ({experience_level}/5)
            - Questions focus on cybersecurity best practices
            - The JSON is valid and properly formatted
            
            DO NOT include any explanatory text before or after the JSON.
            Your entire response should be only the JSON object.
            """
            
            # Log the request
            logger.info(f"Requesting quiz generation from OpenAI for topic: {topic_name}")
            
            try:
                # Use human message directly instead of using ChatPromptTemplate
                messages = [HumanMessage(content=prompt_content)]
                
                # Run the prompt through the LLM
                result = self.llm.invoke(messages)
                response_content = result.content
                
                # Log a preview of the response
                logger.info(f"Received response from OpenAI (length: {len(response_content)} chars)")
                logger.debug(f"Response preview: {response_content[:200]}...")
                
                # Try to parse JSON directly
                try:
                    quiz_data = json.loads(response_content)
                    chapter_count = len(quiz_data.get('chapters', []))
                    logger.info(f"Successfully parsed quiz JSON with {chapter_count} chapters")
                    
                    # Validate the quiz has the expected structure
                    if chapter_count == 0:
                        logger.warning("Quiz has no chapters, falling back to default quiz")
                        return self._generate_fallback_quiz(topic_name, user_role, user_sector)
                    
                    # Log quiz data structure
                    total_questions = sum(len(chapter.get('questions', [])) for chapter in quiz_data.get('chapters', []))
                    logger.info(f"Quiz has {chapter_count} chapters with {total_questions} total questions")
                    
                    # Return the successfully parsed quiz data
                    return quiz_data
                    
                except json.JSONDecodeError as json_err:
                    # If direct parsing fails, try to extract JSON from the response
                    logger.warning(f"Direct JSON parsing failed: {str(json_err)}")
                    logger.debug(f"Attempting to extract JSON from response")
                    
                    json_start = response_content.find('{')
                    json_end = response_content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_content = response_content[json_start:json_end]
                        logger.info(f"Extracted JSON content (length: {len(json_content)})")
                        
                        try:
                            quiz_data = json.loads(json_content)
                            chapter_count = len(quiz_data.get('chapters', []))
                            logger.info(f"Successfully parsed extracted JSON with {chapter_count} chapters")
                            return quiz_data
                        except json.JSONDecodeError as extract_err:
                            logger.error(f"Failed to parse extracted JSON: {str(extract_err)}")
                    else:
                        logger.error("Could not find JSON markers in response")
                    
                    # If we got here, JSON parsing failed
                    logger.error("Using fallback quiz due to JSON parsing failure")
                    db_service.log_agent_action(
                        agent_name=self.name,
                        action="parse_quiz_json",
                        input_data={"response_preview": response_content[:500]},
                        status="error",
                        error_message=str(json_err)
                    )
                    return self._generate_fallback_quiz(topic_name, user_role, user_sector)
                    
            except Exception as e:
                # Log any other errors
                logger.error(f"Error generating quiz content: {str(e)}")
                db_service.log_agent_action(
                    agent_name=self.name,
                    action="generate_quiz_content",
                    input_data={"topic": topic_name, "sector": user_sector, "role": user_role},
                    status="error",
                    error_message=str(e)
                )
                
                # Return fallback content
                logger.info("Using fallback quiz due to exception")
                return self._generate_fallback_quiz(topic_name, user_role, user_sector)

    
    def _save_quiz_content(self, quiz_id: int, quiz_content: Dict) -> None:
        """
        Save generated quiz content to the database
        
        Args:
            quiz_id: ID of the quiz
            quiz_content: Generated quiz content
        """
        chapters = quiz_content.get('chapters', [])
        
        for chapter_idx, chapter in enumerate(chapters):
            # Insert chapter
            chapter_id = db_service.execute_returning(
                """
                INSERT INTO chapters
                (quiz_id, title, description, sequence, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING id
                """,
                (
                    quiz_id,
                    chapter.get('title', f"Chapter {chapter_idx + 1}"),
                    chapter.get('description', ''),
                    chapter_idx + 1
                )
            )
            
            # Insert questions
            questions = chapter.get('questions', [])
            for question_idx, question in enumerate(questions):
                # Ensure options is a list
                options = question.get('options', [])
                if question.get('type') == 'true_false':
                    options = ['True', 'False']
                
                # Format correct answer based on question type
                correct_answer = question.get('correct_answer')
                if isinstance(correct_answer, int) or (isinstance(correct_answer, str) and correct_answer.isdigit()):
                    # Handle index-based answer (convert to string for consistency)
                    correct_answer = str(correct_answer)
                
                db_service.execute(
                    """
                    INSERT INTO questions
                    (chapter_id, type, content, options, correct_answer, explanation, sequence, points, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        chapter_id,
                        question.get('type', 'mcq'),
                        question.get('content', ''),
                        json.dumps(options),
                        json.dumps(correct_answer),
                        question.get('explanation', ''),
                        question_idx + 1,
                        1  # Default point value
                    )
                )
                
            logger.info(f"Saved chapter '{chapter.get('title')}' with {len(questions)} questions")
    
    def _generate_fallback_quiz(self, topic_name: str, user_role: str, user_sector: str) -> Dict:
        """
        Generate a fallback quiz in case of LLM failure
        
        Args:
            topic_name: Main topic name
            user_role: User's role
            user_sector: User's sector
            
        Returns:
            Dictionary with fallback quiz structure
        """
        logger.warning(f"Generating fallback quiz for topic: {topic_name}")
        
        return {
            "chapters": [
                {
                    "title": "Cybersecurity Basics",
                    "description": f"Fundamental concepts related to {topic_name}",
                    "questions": [
                        {
                            "type": "mcq",
                            "content": f"Which of the following is a common {topic_name} threat?",
                            "options": ["Phishing attacks", "Social engineering", "Malware", "All of the above"],
                            "correct_answer": "3",
                            "explanation": "All of these are common cybersecurity threats."
                        },
                        {
                            "type": "true_false",
                            "content": "Strong passwords must be changed every 90 days.",
                            "options": ["True", "False"],
                            "correct_answer": "False",
                            "explanation": "Current NIST guidelines suggest changing passwords only when compromised."
                        },
                        {
                            "type": "mcq",
                            "content": "Which of these is NOT a good security practice?",
                            "options": ["Using multi-factor authentication", "Sharing passwords with trusted colleagues", "Regular security training", "Keeping software updated"],
                            "correct_answer": "1",
                            "explanation": "Passwords should never be shared, even with trusted colleagues."
                        },
                        {
                            "type": "fill_blank",
                            "content": "A ______ is a malicious software designed to block access to a computer system until money is paid.",
                            "correct_answer": "ransomware",
                            "explanation": "Ransomware encrypts files and demands payment for the decryption key."
                        },
                        {
                            "type": "mcq",
                            "content": "Which security principle ensures that only authorized individuals can access sensitive information?",
                            "options": ["Integrity", "Confidentiality", "Availability", "Accountability"],
                            "correct_answer": "1",
                            "explanation": "Confidentiality ensures that information is accessible only to those authorized to have access."
                        }
                    ]
                },
                {
                    "title": f"{user_role} Specific Risks",
                    "description": f"Security risks specific to {user_role} roles",
                    "questions": [
                        {
                            "type": "mcq",
                            "content": f"As a {user_role}, what is your primary security responsibility?",
                            "options": ["Following security policies", "Reporting incidents", "Protecting customer data", "All of the above"],
                            "correct_answer": "3",
                            "explanation": "All of these are important security responsibilities."
                        },
                        {
                            "type": "true_false",
                            "content": f"A {user_role} has no responsibility for reporting suspicious activities.",
                            "options": ["True", "False"],
                            "correct_answer": "False",
                            "explanation": "Every employee has a responsibility to report suspicious activities."
                        },
                        {
                            "type": "fill_blank",
                            "content": f"In the role of {user_role}, ______ is the most important security principle to follow.",
                            "correct_answer": "least privilege",
                            "explanation": "The principle of least privilege means giving users only the access they need to perform their job functions."
                        },
                        {
                            "type": "mcq",
                            "content": "Which of these practices increases security risks?",
                            "options": ["Regular password changes", "Locking computers when away", "Using personal email for work", "Security awareness training"],
                            "correct_answer": "2",
                            "explanation": "Using personal email for work introduces significant security risks."
                        },
                        {
                            "type": "mcq",
                            "content": "What should you do if you suspect a security breach?",
                            "options": ["Ignore it if it doesn't affect you directly", "Try to fix it yourself first", "Report it immediately", "Wait to see if others notice it"],
                            "correct_answer": "2",
                            "explanation": "Security incidents should be reported immediately to the proper authorities."
                        }
                    ]
                },
                {
                    "title": f"{user_sector} Specific Threats",
                    "description": f"Threats specific to the {user_sector} sector",
                    "questions": [
                        {
                            "type": "fill_blank",
                            "content": f"The most common type of attack in the {user_sector} sector is ______.",
                            "correct_answer": "data breach",
                            "explanation": "Data breaches are particularly common in this sector."
                        },
                        {
                            "type": "mcq",
                            "content": f"Which regulatory framework is most relevant to the {user_sector} sector?",
                            "options": ["GDPR", "HIPAA", "PCI DSS", "ISO 27001"],
                            "correct_answer": "0",
                            "explanation": "GDPR is a widely applicable data protection regulation."
                        },
                        {
                            "type": "true_false",
                            "content": f"Security threats in the {user_sector} sector are mostly from external actors.",
                            "options": ["True", "False"],
                            "correct_answer": "False",
                            "explanation": "Both internal and external threats are significant in all sectors."
                        },
                        {
                            "type": "mcq",
                            "content": f"Which is NOT a common security vulnerability in the {user_sector} sector?",
                            "options": ["Outdated systems", "Insider threats", "Quantum computing attacks", "Poor access controls"],
                            "correct_answer": "2",
                            "explanation": "While emerging, quantum computing attacks are not yet common."
                        },
                        {
                            "type": "fill_blank",
                            "content": f"In the {user_sector} sector, ______ is particularly important for maintaining security.",
                            "correct_answer": "employee training",
                            "explanation": "Regular security awareness training helps prevent many common attacks."
                        }
                    ]
                },
                {
                    "title": "Advanced Challenges",
                    "description": "Complex security scenarios requiring critical thinking",
                    "questions": [
                        {
                            "type": "mcq",
                            "content": "Which approach is most effective for securing a complex IT environment?",
                            "options": ["Installing the latest antivirus software", "Implementing defense in depth", "Outsourcing all security", "Focusing on physical security"],
                            "correct_answer": "1",
                            "explanation": "Defense in depth uses multiple security layers to protect assets."
                        },
                        {
                            "type": "true_false",
                            "content": "Zero-day vulnerabilities are impossible to defend against.",
                            "options": ["True", "False"],
                            "correct_answer": "False",
                            "explanation": "While challenging, defense in depth can help mitigate zero-day risks."
                        },
                        {
                            "type": "fill_blank",
                            "content": "A ______ tests an organization's security by simulating real-world attacks.",
                            "correct_answer": "penetration test",
                            "explanation": "Penetration testing identifies vulnerabilities before attackers can exploit them."
                        },
                        {
                            "type": "mcq",
                            "content": "What is NOT typically included in a security incident response plan?",
                            "options": ["Containment strategies", "Evidence collection procedures", "Financial compensation details", "Communication protocols"],
                            "correct_answer": "2",
                            "explanation": "Financial compensation is typically handled separately from incident response."
                        },
                        {
                            "type": "mcq",
                            "content": "Which is considered the most secure authentication method?",
                            "options": ["Complex passwords", "Biometric authentication", "Multi-factor authentication", "Security questions"],
                            "correct_answer": "2",
                            "explanation": "Multi-factor authentication combines multiple verification methods."
                        }
                    ]
                }
            ]
        }

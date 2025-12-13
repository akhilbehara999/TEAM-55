import os
import tempfile
import json
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import google.generativeai as genai
from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
import logging
from typing import Dict, Any
from pydantic import BaseModel

# Add gTTS import for text-to-speech
from gtts import gTTS
import io
import uuid

# Add the database and history imports
from database.config import get_db
from sqlalchemy.orm import Session
from utils.history_manager import HistoryManager

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configurations
from config import settings

# Configure Gemini API with error handling
try:
    if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "YOUR_NEW_GOOGLE_API_KEY_HERE":
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        logger.info("Gemini API configured successfully")
    else:
        logger.warning("No valid Google API key found. Some features may not work.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")

# Import agent classes
from agents.resume_agent import ResumeIntelligenceAgent
from agents.interview_agent import InterviewSimulationAgent
from agents.docs_agent import AutoDocsAgent
from agents.orchestrator import MasterOrchestratorAgent

# Import schemas
from schemas.user import UserCreate, UserResponse
from schemas.document import DocumentUpload, DocumentResponse
from schemas.settings import UserSettings, UpdateSettings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware with support for multiple origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL, 
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://localhost:8002",
        "http://127.0.0.1:8002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = MasterOrchestratorAgent()

# Initialize history manager
history_manager = HistoryManager()

# Pydantic models
class ResumeAnalysisRequest(BaseModel):
    job_description: str
    target_vibe: str

class InterviewStartRequest(BaseModel):
    role: str
    experience_level: str

class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer_text: str

# Add new Pydantic models for human interview endpoints
class HumanInterviewStartRequest(BaseModel):
    role: str
    experience_level: str

class HumanInterviewAnswerRequest(BaseModel):
    session_id: str
    answer_text: str

# Add session storage for interview sessions
interview_sessions = {}

# Add session storage for human interview sessions
human_interview_sessions = {}

# Add a set to track active sessions to prevent concurrent processing
active_interview_sessions = set()

# Add audio directory for storing generated audio files
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Add audio endpoint for serving generated audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve generated audio files
    """
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    else:
        # If file doesn't exist, generate a default audio
        tts = gTTS("Audio not available", lang='en')
        temp_filename = os.path.join(AUDIO_DIR, filename)
        tts.save(temp_filename)
        return FileResponse(temp_filename, media_type="audio/mpeg")

# Enhanced human interview endpoints with better question generation
@app.post("/api/human_interview/start")
async def start_human_interview(request: HumanInterviewStartRequest):
    """
    Start a new human-like interview session with realistic questions based on experience level
    """
    try:
        # Generate a unique session_id
        import uuid
        session_id = str(uuid.uuid4())
        
        # Initialize session memory with user inputs
        human_interview_sessions[session_id] = {
            "role": request.role,
            "experience_level": request.experience_level,
            "history_list": [],
            "total_questions_asked": 0,
            "last_question": None
        }
        
        # Generate appropriate first question based on experience level
        if request.experience_level == "Beginner":
            first_question = "Thank you for coming in today. To start, could you tell me a little about yourself and what drew you to this field?"
        elif request.experience_level == "Intermediate":
            first_question = "Thanks for joining us today. Can you walk me through your background and highlight a couple of accomplishments you're particularly proud of in your career so far?"
        else:  # Expert
            first_question = "Thank you for your time today. Given your extensive experience, I'd love to hear about a significant challenge you've faced in your career and how you approached solving it."
        
        # Generate audio file for the question
        audio_filename = f"{session_id}_q1.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        tts = gTTS(first_question, lang='en')
        tts.save(audio_filepath)
        
        # Generate audio URL
        audio_url = f"/audio/{audio_filename}"
        
        # Store the first question
        human_interview_sessions[session_id]["last_question"] = first_question
        
        return JSONResponse(content={
            "session_id": session_id,
            "question_text": first_question,
            "audio_url": audio_url,
            "status": "continue"
        })
    except Exception as e:
        logger.error(f"Error starting human interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting human interview: {str(e)}"
        )

@app.post("/api/human_interview/answer")
async def submit_human_interview_answer(request: HumanInterviewAnswerRequest):
    """
    Submit a human interview answer and get the next realistic question with adaptive difficulty
    """
    # Check if session is already being processed
    if request.session_id in active_interview_sessions:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Session is already being processed. Please wait."
        )
    
    try:
        # Mark session as active
        active_interview_sessions.add(request.session_id)
        
        # Retrieve session_id from memory
        if request.session_id not in human_interview_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session not found"
            )
        
        session = human_interview_sessions[request.session_id]
        
        # Check if this is a duplicate submission by comparing with last answer
        # This prevents the same answer from being processed multiple times
        if session['history_list']:
            last_entry = session['history_list'][-1]
            if last_entry.get('answer') == request.answer_text:
                # This is a duplicate submission, return the same next question
                if session.get('next_question'):
                    # Generate audio file for the question
                    audio_filename = f"{request.session_id}_q{session['total_questions_asked'] + 1}.mp3"
                    audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
                    tts = gTTS(session['next_question'], lang='en')
                    tts.save(audio_filepath)
                    
                    return JSONResponse(content={
                        "session_id": request.session_id,
                        "question_text": session['next_question'],
                        "audio_url": f"/audio/{audio_filename}",
                        "status": "continue"
                    })
        
        # Append user's answer to the session's history_list
        session['history_list'].append({
            "question": session.get('last_question', 'Initial question'),
            "answer": request.answer_text
        })
        
        session['total_questions_asked'] += 1
        
        # Check if interview should be concluded (after 7 questions)
        if session['total_questions_asked'] >= 7:
            # Generate final assessment based on experience level
            session_copy = session.copy()  # Make a copy before deleting
            del human_interview_sessions[request.session_id]
            
            # Customize feedback based on experience level
            if session_copy['experience_level'] == "Beginner":
                feedback = "You did a great job explaining your background and motivations. For future interviews, try to connect your experiences more directly to the role requirements. Your enthusiasm is a strength!"
                strengths = ["Clear communication", "Enthusiasm and motivation", "Good foundational understanding"]
                weaknesses = ["Could connect experiences more directly to role", "Need more specific examples", "Technical depth could be improved"]
            elif session_copy['experience_level'] == "Intermediate":
                feedback = "You demonstrated solid experience and good problem-solving abilities. To elevate your performance, focus on quantifying your achievements with specific metrics and showing more leadership initiative."
                strengths = ["Relevant experience", "Good problem-solving approach", "Clear communication"]
                weaknesses = ["Could include more specific metrics", "Need to elaborate on leadership examples", "Technical depth could be improved"]
            else:  # Expert
                feedback = "You showcased extensive experience and strategic thinking. To refine your approach, consider providing more concise answers while maintaining depth, and ensure you're directly addressing the question asked."
                strengths = ["Extensive experience", "Strategic thinking", "Strong technical foundation"]
                weaknesses = ["Answers could be more concise", "Need to directly address questions", "Could show more innovative approaches"]
            
            # Remove from active sessions
            active_interview_sessions.discard(request.session_id)
            
            return JSONResponse(content={
                "session_id": request.session_id,
                "status": "complete",
                "final_score": 88,
                "overall_feedback": feedback,
                "strengths": strengths,
                "weaknesses": weaknesses
            })
        
        # Generate next question based on experience level and context
        last_answer = request.answer_text.lower()
        
        # Adaptive questioning logic
        if session['experience_level'] == "Beginner":
            # For beginners, focus on basic understanding and motivation
            if "don't know" in last_answer or "not sure" in last_answer or len(last_answer.split()) < 20:
                # If answer was vague or short, ask for clarification
                next_question = "Could you provide a more specific example? Think about a time when you faced a challenge and how you overcame it."
            else:
                # If answer was decent, move to a slightly more complex question
                next_question = "That's helpful. Can you tell me about a time when you had to work with a difficult team member? How did you handle the situation?"
        elif session['experience_level'] == "Intermediate":
            # For intermediate candidates, focus on tactical skills
            if "led" in last_answer or "managed" in last_answer or "coordinated" in last_answer:
                # If they mentioned leadership, probe deeper
                next_question = "That's interesting. Can you quantify the impact of that leadership role? What specific results did your team achieve?"
            elif "problem" in last_answer or "challenge" in last_answer:
                # If they mentioned problems, ask about solutions
                next_question = "You mentioned a challenge. What would you do differently if you faced a similar situation in the future?"
            else:
                # General intermediate question
                next_question = "Let's talk about your technical skills. Can you describe a complex project you've worked on and your specific contributions to its success?"
        else:  # Expert
            # For experts, focus on strategic thinking
            if "strategy" in last_answer or "vision" in last_answer or "long-term" in last_answer:
                # If they mentioned strategy, probe deeper
                next_question = "That's a compelling vision. How would you measure the success of that strategy, and what key performance indicators would you track?"
            elif "team" in last_answer or "people" in last_answer:
                # If they mentioned people management, ask about development
                next_question = "You've mentioned leading teams. How do you approach developing talent and building high-performing teams?"
            else:
                # General expert question
                next_question = "Given your experience, how do you approach making decisions when you have incomplete information? Can you walk me through your decision-making framework?"
        
        # Generate audio file for the question
        audio_filename = f"{request.session_id}_q{session['total_questions_asked'] + 1}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        tts = gTTS(next_question, lang='en')
        tts.save(audio_filepath)
        
        # Generate audio URL
        audio_url = f"/audio/{audio_filename}"
        
        # Store last question and next question for next iteration
        session['last_question'] = next_question
        session['next_question'] = next_question  # Store for duplicate check
        
        # Remove from active sessions
        active_interview_sessions.discard(request.session_id)
        
        return JSONResponse(content={
            "session_id": request.session_id,
            "question_text": next_question,
            "audio_url": audio_url,
            "status": "continue"
        })
    except HTTPException:
        # Remove from active sessions on error
        active_interview_sessions.discard(request.session_id)
        raise
    except Exception as e:
        # Remove from active sessions on error
        active_interview_sessions.discard(request.session_id)
        logger.error(f"Error submitting human interview answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting human interview answer: {str(e)}"
        )

# Add new interview endpoints
@app.post("/api/interview/start")
async def start_interview(request: InterviewStartRequest):
    """
    Start a new interview session
    """
    try:
        # Initialize session memory with role and level
        session_id = f"session_{request.user_id}"
        interview_sessions[session_id] = {
            "user_id": request.user_id,
            "role": request.role,
            "level": request.level,
            "questions_asked": [],
            "answers_given": [],
            "score": 0,
            "question_count": 0
        }
        
        # Use the HR Interview Agent System Prompt to generate the first question
        system_prompt = f"""
You are the CareerFlow AI Interview Simulation Agent, specialized in Human Resources (HR).
Your sole purpose is to conduct a highly realistic, contextual, and role-specific mock interview.

--- CONTEXT ---
Target Role: {request.role} (e.g., HR Analyst, HR Manager)
Experience Level: {request.level} (BEGINNER, INTERMEDIATE, or EXPERT)
Previous Dialogue: []
---

--- INSTRUCTIONS ---
1.  **Difficulty Calibration:** Tailor your questions based on the 'Experience Level'.
    * **BEGINNER:** Focus on definitions, basic policy adherence, and entry-level tasks.
    * **INTERMEDIATE:** Focus on tactical implementation, policy interpretation, and handling common scenarios.
    * **EXPERT:** Focus on strategic planning, organizational change management, legal risk mitigation, and leadership philosophy.
2.  **Question Generation:** Generate only one, single question per turn. The question must be a direct and professional follow-up or a new question highly relevant to the HR role.
3.  **Interview Flow:** If a user answers well, increase the complexity in the next question. If the user answers poorly, probe deeper into that specific area for validation.
4.  **Do NOT provide the correct answer or coach the user.** Maintain the role of a neutral interviewer.
5.  **After the final turn (determined by the backend logic), you MUST provide a score and a detailed feedback report.**
6.  **Format your output STRICTLY as a single JSON object.**

--- JSON OUTPUT FORMAT ---
{{
    "question": "Your single, generated HR question here.",
    "interview_status": "continue"
}}

# IF interview_status is "complete", ADD THESE FIELDS to the JSON:
# {{
#    "final_score": INTEGER (0-100 based on the overall quality and depth of answers),
#    "overall_feedback": "A concise, professional report summarizing the user's performance, strengths, weaknesses, and a recommendation based on their stated {request.level} status."
# }}
"""

        # Create the prompt
        prompt = f"{system_prompt}\n\nGenerate the first interview question for an {request.level} {request.role}."
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text and parse as JSON
            response_text = response.text.strip()
            
            # Handle potential markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            
            parsed_response = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['question', 'interview_status']
            for field in required_fields:
                if field not in parsed_response:
                    raise ValueError(f"Missing required field: {field}")
            
            # Store the question in session
            question_id = f"q_{len(interview_sessions[session_id]['questions_asked']) + 1}"
            interview_sessions[session_id]['questions_asked'].append({
                "id": question_id,
                "text": parsed_response['question'],
                "status": parsed_response['interview_status']
            })
            interview_sessions[session_id]['question_count'] += 1
            
            # Generate audio file for the question
            audio_filename = f"{question_id}.mp3"
            audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
            tts = gTTS(parsed_response['question'], lang='en')
            tts.save(audio_filepath)
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": parsed_response['question'],
                "audio_url": f"/audio/{audio_filename}"
            })
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response: {response.text}")
            # Return a fallback response
            question_id = f"q_{len(interview_sessions[session_id]['questions_asked']) + 1}"
            fallback_question = "Can you tell me about your experience in HR and what interests you most about this field?"
            interview_sessions[session_id]['questions_asked'].append({
                "id": question_id,
                "text": fallback_question,
                "status": "continue"
            })
            interview_sessions[session_id]['question_count'] += 1
            
            # Generate audio file for the fallback question
            audio_filename = f"{question_id}.mp3"
            audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
            tts = gTTS(fallback_question, lang='en')
            tts.save(audio_filepath)
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": fallback_question,
                "audio_url": f"/audio/{audio_filename}"
            })
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting interview: {str(e)}"
        )

@app.post("/api/interview/answer")
async def submit_interview_answer(request: InterviewAnswerRequest):
    """
    Submit an interview answer and get the next question
    """
    try:
        # Retrieve session
        session_id = f"session_{request.user_id}"
        if session_id not in interview_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session not found"
            )
        
        session = interview_sessions[session_id]
        
        # Append user answer
        session['answers_given'].append({
            "question_id": request.question_id,
            "answer": request.user_answer
        })
        
        # Check if interview is complete (after 5 questions)
        if session['question_count'] >= 5:
            # Generate final score and feedback
            final_score = 85  # In a real implementation, this would be calculated based on answers
            overall_feedback = f"Excellent response to strategic questions. Need to be more precise on policy details. Overall, {session['level']}-level proficiency demonstrated."
            
            # Save to history
            try:
                history_manager.save_history(
                    user_id=1,  # Dummy user ID
                    agent_name="Interview Simulator",
                    summary_text=f"Score: {final_score}",
                    full_output={
                        "final_score": final_score,
                        "overall_feedback": overall_feedback,
                        "role": session['role'],
                        "level": session['level']
                    }
                )
            except Exception as e:
                logger.error(f"Failed to save history record: {e}")
            
            # Remove session
            del interview_sessions[session_id]
            
            return JSONResponse(content={
                "status": "complete",
                "final_score": final_score,
                "overall_feedback": overall_feedback
            })
        
        # Generate next question based on context
        system_prompt = f"""
You are the CareerFlow AI Interview Simulation Agent, specialized in Human Resources (HR).
Your sole purpose is to conduct a highly realistic, contextual, and role-specific mock interview.

--- CONTEXT ---
Target Role: {session['role']} (e.g., HR Analyst, HR Manager)
Experience Level: {session['level']} (BEGINNER, INTERMEDIATE, or EXPERT)
Previous Dialogue: {session['questions_asked'][-1]['text']} - {request.user_answer}
---

--- INSTRUCTIONS ---
1.  **Difficulty Calibration:** Tailor your questions based on the 'Experience Level'.
    * **BEGINNER:** Focus on definitions, basic policy adherence, and entry-level tasks.
    * **INTERMEDIATE:** Focus on tactical implementation, policy interpretation, and handling common scenarios.
    * **EXPERT:** Focus on strategic planning, organizational change management, legal risk mitigation, and leadership philosophy.
2.  **Question Generation:** Generate only one, single question per turn. The question must be a direct and professional follow-up or a new question highly relevant to the HR role.
3.  **Interview Flow:** If a user answers well, increase the complexity in the next question. If the user answers poorly, probe deeper into that specific area for validation.
4.  **Do NOT provide the correct answer or coach the user.** Maintain the role of a neutral interviewer.
5.  **After the final turn (determined by the backend logic), you MUST provide a score and a detailed feedback report.**
6.  **Format your output STRICTLY as a single JSON object.**

--- JSON OUTPUT FORMAT ---
{{
    "question": "Your single, generated HR question here.",
    "interview_status": "continue"
}}

# IF interview_status is "complete", ADD THESE FIELDS to the JSON:
# {{
#    "final_score": INTEGER (0-100 based on the overall quality and depth of answers),
#    "overall_feedback": "A concise, professional report summarizing the user's performance, strengths, weaknesses, and a recommendation based on their stated {session['level']} status."
# }}
"""

        # Create the prompt with context
        previous_dialogue = ""
        if session['questions_asked'] and session['answers_given']:
            previous_dialogue = f"Previous Question: {session['questions_asked'][-1]['text']}\nUser Answer: {request.user_answer}"
        
        prompt = f"{system_prompt}\n\n{previous_dialogue}\n\nGenerate the next interview question."
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text and parse as JSON
            response_text = response.text.strip()
            
            # Handle potential markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            
            parsed_response = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['question', 'interview_status']
            for field in required_fields:
                if field not in parsed_response:
                    raise ValueError(f"Missing required field: {field}")
            
            # Store the question in session
            question_id = f"q_{len(interview_sessions[session_id]['questions_asked']) + 1}"
            interview_sessions[session_id]['questions_asked'].append({
                "id": question_id,
                "text": parsed_response['question'],
                "status": parsed_response['interview_status']
            })
            interview_sessions[session_id]['question_count'] += 1
            
            # Generate audio file for the question
            audio_filename = f"{question_id}.mp3"
            audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
            tts = gTTS(parsed_response['question'], lang='en')
            tts.save(audio_filepath)
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": parsed_response['question'],
                "audio_url": f"/audio/{audio_filename}"
            })
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response: {response.text}")
            # Return a fallback response
            question_id = f"q_{len(interview_sessions[session_id]['questions_asked']) + 1}"
            fallback_question = "Can you elaborate more on that point?"
            interview_sessions[session_id]['questions_asked'].append({
                "id": question_id,
                "text": fallback_question,
                "status": "continue"
            })
            interview_sessions[session_id]['question_count'] += 1
            
            # Generate audio file for the fallback question
            audio_filename = f"{question_id}.mp3"
            audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
            tts = gTTS(fallback_question, lang='en')
            tts.save(audio_filepath)
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": fallback_question,
                "audio_url": f"/audio/{audio_filename}"
            })
    except Exception as e:
        logger.error(f"Error submitting interview answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting interview answer: {str(e)}"
        )

# Auto-Docs endpoint for README generation
@app.post("/api/autodocs/generate")
async def generate_readme(request: dict):
    """
    Generate README.md for a GitHub repository using the Auto-Docs Agent
    """
    try:
        github_url = request.get('github_url')
        project_title = request.get('project_title')
        
        if not github_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub URL is required"
            )
        
        # Import git here to avoid issues if not installed
        import git
        import shutil
        
        # Create a temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone the repository
                repo = git.Repo.clone_from(github_url, temp_dir)
                
                # Extract file contents
                concatenated_contents = ""
                ignored_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.vscode', '.idea'}
                ignored_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.tar', '.gz', '.exe', '.dll', '.so'}
                
                for root, dirs, files in os.walk(temp_dir):
                    # Skip ignored directories
                    dirs[:] = [d for d in dirs if d not in ignored_dirs]
                    
                    for file in files:
                        # Skip ignored file extensions
                        if any(file.endswith(ext) for ext in ignored_extensions):
                            continue
                        
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                concatenated_contents += f"---FILE: {relative_path}---\n{content}\n\n"
                        except (UnicodeDecodeError, PermissionError):
                            # Skip binary or unreadable files
                            continue
                
                # If no content was extracted, provide a fallback
                if not concatenated_contents:
                    concatenated_contents = "No readable source files found in the repository."
                
                # Determine project title
                repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
                final_project_title = project_title if project_title else repo_name
                
                # Define the system prompt for the Auto-Docs Agent
                AUTO_DOCS_SYSTEM_PROMPT = """
You are the Auto-Docs Agent. Your task is to generate a comprehensive and professional README.md file based on the provided codebase structure and content.

--- CONTEXT ---
Project Title Override: {project_title_or_repo_name}
All File Contents:
{concatenated_file_contents_from_cloned_repo}
---

--- INSTRUCTIONS ---
1.  **Format:** Your entire response MUST be clean, valid Markdown suitable for a GitHub README.md file. Do not include any text outside the Markdown content (e.g., no conversational greetings or explanations).
2.  **Sections:** Include the following standard sections, inferring content from the code provided:
    * # Project Title (Use the Override or infer from code)
    * ## Description (What does the project do?)
    * ## Features (List key functionalities, e.g., API endpoints, core calculations)
    * ## Installation (Provide clear steps, referencing requirements.txt or package.json)
    * ## Usage (Provide a code snippet or simple steps to run the main functionality)
    * ## Technologies Used (List inferred languages/frameworks)
3.  **Tone:** Professional, informative, and concise.
"""
                
                # Create the prompt
                prompt = AUTO_DOCS_SYSTEM_PROMPT.format(
                    project_title_or_repo_name=final_project_title,
                    concatenated_file_contents_from_cloned_repo=concatenated_contents[:10000]  # Limit content size
                )
                
                # Initialize the Gemini model
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Generate content
                response = model.generate_content(prompt)
                
                # Get the raw Markdown response
                readme_content = response.text.strip()
                
                # Handle potential markdown code blocks
                if readme_content.startswith("```"):
                    readme_content = readme_content[3:]  # Remove ```
                if readme_content.endswith("```"):
                    readme_content = readme_content[:-3]  # Remove ```
                
                # Save to history
                try:
                    history_manager.save_history(
                        user_id=1,  # Dummy user ID
                        agent_name="Auto-Docs Generator",
                        summary_text="Generated Successfully",
                        full_output={
                            "readme_content": readme_content,
                            "filename": "README.md",
                            "github_url": github_url
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to save history record: {e}")
                
                return JSONResponse(content={
                    "status": "success",
                    "readme_content": readme_content,
                    "filename": "README.md"
                })
                
            except git.exc.GitCommandError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to clone repository: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Error processing repository: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing repository: {str(e)}"
                )
                
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating README with Gemini: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating README: {str(e)}"
        )

# Add ContractReviewRequest model
class ContractReviewRequest(BaseModel):
    file: UploadFile

# Contract Guardian endpoint for PDF analysis
@app.post("/api/analyze/contract")
async def analyze_contract(file: UploadFile = File(...)):
    """
    Analyze contract PDF and extract key terms and risk clauses
    """
    # Validate file type
    if not file.content_type.startswith("application/pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text from the PDF using PyMuPDF
        try:
            doc = fitz.open(temp_file_path)
            contract_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                contract_text += page.get_text()
            doc.close()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
        finally:
            # Delete the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
        
        # Check if text was extracted
        if not contract_text or len(contract_text.strip()) == 0:
            logger.warning("No text could be extracted from the PDF file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF file. Please ensure it's a valid PDF with text content."
            )
        
        logger.info(f"Successfully extracted {len(contract_text)} characters from PDF")
        
        # Limit contract text length to prevent API timeouts
        max_length = 50000  # About 10-15 pages of text
        if len(contract_text) > max_length:
            contract_text = contract_text[:max_length]
            logger.info(f"Truncated contract text to {len(contract_text)} characters")
        
        # Use the orchestrator to analyze the contract
        try:
            logger.info("Sending contract text to orchestrator for analysis")
            result = orchestrator.route_request("contract", {"contract_text": contract_text})
            logger.info(f"Received response from orchestrator: success={result.get('success')}")
            
            if result.get("success", False):
                # The orchestrator returns the contract analysis result directly
                # If it's wrapped in a data field, extract it; otherwise use the result as-is
                data = result.get("data", result)
                logger.info("Contract analysis completed successfully")
                
                # Save to history
                try:
                    overall_score = data.get("overall_score", "N/A")
                    summary = data.get("summary", "Analysis completed")
                    history_manager.save_history(
                        user_id=1,  # Dummy user ID
                        agent_name="Contract Guardian",
                        summary_text=f"Score: {overall_score}",
                        full_output=data
                    )
                except Exception as e:
                    logger.error(f"Failed to save history record: {e}")
                
                return data
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Contract analysis failed: {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error during contract analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing contract: {str(e)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in contract analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing contract: {str(e)}"
        )

# Add new Pydantic models for resume analysis endpoints

# Add Pydantic model for file upload
class ResumeFileAnalysisRequest(BaseModel):
    target_vibe: str
    job_description: str = ""

# Resume Guardian endpoint for resume analysis with file upload
@app.post("/api/analyze/resume/file")
async def analyze_resume_file(
    file: UploadFile = File(...),
    target_vibe: str = Form(...),
    job_description: str = Form("")
):
    """
    Analyze resume file and provide feedback based on job description and target vibe
    """
    # Validate file type
    if not file.content_type.startswith("application/pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Extract text from the PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text from the PDF using PyMuPDF
        try:
            doc = fitz.open(temp_file_path)
            resume_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                resume_text += page.get_text()
            doc.close()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
        finally:
            # Delete the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
        
        # Check if text was extracted
        if not resume_text or len(resume_text.strip()) == 0:
            logger.warning("No text could be extracted from the PDF file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF file. Please ensure it's a valid PDF with text content."
            )
        
        logger.info(f"Successfully extracted {len(resume_text)} characters from PDF")
        
        # Initialize the ResumeIntelligenceAgent
        agent = ResumeIntelligenceAgent()
        
        # Generate the analysis result
        analysis_result = agent.analyze_resume(
            resume_content=resume_text,
            job_description=job_description,
            target_vibe=target_vibe
        )
        
        # Save to history
        try:
            overall_score = analysis_result.get("ats_score", "N/A")
            history_manager.save_history(
                user_id=1,  # Dummy user ID
                agent_name="Resume Analyzer",
                summary_text=f"Score: {overall_score}",
                full_output=analysis_result
            )
        except Exception as e:
            logger.error(f"Failed to save history record: {e}")
        
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )

# Resume Guardian endpoint for resume analysis (existing endpoint)
@app.post("/api/analyze/resume")
async def analyze_resume(request: ResumeAnalysisRequest):
    """
    Analyze resume and provide feedback based on job description and target vibe
    """
    try:
        # Initialize the ResumeIntelligenceAgent
        agent = ResumeIntelligenceAgent()
        
        # For now, we'll use a dummy resume content since we're not uploading a file
        # In a full implementation, you would extract text from an uploaded PDF
        dummy_resume_content = "John Doe\nSoftware Engineer\nExperience: 5 years in Python and JavaScript\nEducation: BS in Computer Science"
        
        # Generate the analysis result
        analysis_result = agent.analyze_resume(
            resume_content=dummy_resume_content,
            job_description=request.job_description,
            target_vibe=request.target_vibe
        )
        
        # Save to history
        try:
            overall_score = analysis_result.get("ats_score", "N/A")
            history_manager.save_history(
                user_id=1,  # Dummy user ID
                agent_name="Resume Analyzer",
                summary_text=f"Score: {overall_score}",
                full_output=analysis_result
            )
        except Exception as e:
            logger.error(f"Failed to save history record: {e}")
        
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )

# Add helper function for audio processing
def preprocess_audio_for_speech_recognition(audio_data):
    """
    Preprocess audio data to improve speech recognition accuracy
    """
    try:
        # This is a placeholder for actual audio preprocessing
        # In a real implementation, you would:
        # 1. Apply noise reduction filters
        # 2. Normalize audio levels
        # 3. Enhance speech frequencies
        # 4. Remove background noise
        
        # For now, we'll just return the audio data as-is
        # but in a production environment, you would integrate
        # with libraries like scipy, librosa, or pydub for processing
        return audio_data
    except Exception as e:
        logger.error(f"Error preprocessing audio: {str(e)}")
        return audio_data

@app.get("/api/user/settings")
async def get_user_settings(db: Session = Depends(get_db)):
    """
    Retrieve the current settings for the authenticated user
    
    Returns:
        JSON with user settings
    """
    try:
        # For now, we'll use a dummy user ID (1) since we don't have authentication
        # In a real implementation, this would come from the authenticated user
        user_id = 1
        
        # Get user from database
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return user settings
        return UserSettings(
            username=user.username or f"user{user.id}",
            email=user.email,
            full_name=user.full_name or "",
            default_experience=user.default_experience or "Beginner",
            default_vibe=user.default_vibe or "Startup"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving settings: {str(e)}"
        )

@app.patch("/api/user/settings")
async def update_user_settings(settings_update: UpdateSettings, db: Session = Depends(get_db)):
    """
    Update the settings for the authenticated user
    
    Args:
        settings_update: Partial settings update object
        
    Returns:
        JSON with success message
    """
    try:
        # For now, we'll use a dummy user ID (1) since we don't have authentication
        # In a real implementation, this would come from the authenticated user
        user_id = 1
        
        # Get user from database
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user settings with only the provided fields
        update_data = settings_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        # Save changes to database
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "message": "Settings updated successfully."
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )

@app.get("/api/user/history")
async def get_user_history(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve paginated history records for the authenticated user
    
    Args:
        page: Page number (1-indexed)
        limit: Number of records per page
        db: Database session
        
    Returns:
        JSON with pagination info and history records
    """
    try:
        # For now, we'll use a dummy user ID (1) since we don't have authentication
        # In a real implementation, this would come from the authenticated user
        user_id = 1
        
        # Get paginated history records
        total_records, history_records = history_manager.get_user_history(user_id, page, limit)
        
        return {
            "status": "success",
            "total_records": total_records,
            "data": history_records
        }
    except Exception as e:
        logger.error(f"Error retrieving user history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

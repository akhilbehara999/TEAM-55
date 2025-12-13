import os
import tempfile
import json
from fastapi import FastAPI, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import google.generativeai as genai
from pdfminer.high_level import extract_text
import logging
from typing import Dict, Any
from pydantic import BaseModel

# Import configurations
from config import settings
from agents.config import agent_config

# Import agent classes
from agents.resume_agent import ResumeIntelligenceAgent
from agents.interview_agent import InterviewSimulationAgent
from agents.contract_agent import ContractGuardianAgent
from agents.docs_agent import AutoDocsAgent
from agents.orchestrator import MasterOrchestratorAgent

# Import schemas
from schemas.user import UserCreate, UserResponse
from schemas.document import DocumentUpload, DocumentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = MasterOrchestratorAgent()

# Pydantic models for requests
class ResumeAnalysisRequest(BaseModel):
    resume_content: str
    job_description: str = ""

class InterviewPrepRequest(BaseModel):
    role: str
    experience_level: str
    interview_type: str

class ContractReviewRequest(BaseModel):
    contract_text: str

class DocumentGenerationRequest(BaseModel):
    document_type: str
    content_data: Dict[Any, Any]

class WorkflowRequest(BaseModel):
    workflow: str
    context: Dict[Any, Any]

# Add new Pydantic models for interview endpoints
class InterviewStartRequest(BaseModel):
    user_id: str
    role: str
    level: str

class InterviewAnswerRequest(BaseModel):
    user_id: str
    question_id: str
    user_answer: str

# Add session storage for interview sessions
interview_sessions = {}

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "CareerFlow AI API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Existing API endpoints for backward compatibility
@app.get("/api/v1/")
async def api_root():
    return {"message": "CareerFlow AI API v1"}

@app.post("/api/v1/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # This would normally interact with a database
    return UserResponse(
        id=1,
        email=user.email,
        full_name=user.full_name,
        created_at="2023-01-01T00:00:00Z"
    )

@app.post("/api/v1/documents/upload/", response_model=DocumentResponse)
async def upload_document(document: DocumentUpload):
    # This would normally process the document
    return DocumentResponse(
        id=1,
        filename=document.filename,
        document_type=document.document_type,
        status="processed",
        processed_at="2023-01-01T00:00:00Z"
    )

@app.get("/api/v1/health/")
async def api_health_check():
    return {"status": "healthy"}

# Resume analysis functions
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using pdfminer.six
    """
    try:
        text = extract_text(file_path)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing PDF file: {str(e)}"
        )

def analyze_resume_with_gemini(resume_text: str) -> dict:
    """
    Analyze resume text using Gemini AI and return structured JSON response
    """
    try:
        # Define the system prompt for the Resume Intelligence Agent
        system_prompt = """
You are the Resume Intelligence Agent. Your goal is to provide two outputs for the user's resume text: 
1) A humorous, Gen-Z styled 'roast' for engagement, and 
2) A clear, professional list of fixes for ATS optimization. 

Analyze the provided resume text thoroughly. Your output MUST be a single JSON object with these exact fields:
- ats_score: Integer (0-100) representing the compatibility score
- gen_z_roast: String (The humorous critique)
- professional_fixes: Array of Strings (specific, actionable improvements)
- status: String ("success" or "error")

Example response format:
{
  "ats_score": 75,
  "gen_z_roast": "This resume is so basic, it makes instant noodles look gourmet...",
  "professional_fixes": [
    "Add quantifiable achievements with specific numbers",
    "Replace vague buzzwords with concrete examples"
  ],
  "status": "success"
}

Analyze this resume text:
"""

        # Create the prompt
        prompt = f"{system_prompt}\n\n{resume_text}"

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
            required_fields = ['ats_score', 'gen_z_roast', 'professional_fixes', 'status']
            for field in required_fields:
                if field not in parsed_response:
                    raise ValueError(f"Missing required field: {field}")
            
            return parsed_response
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response: {response.text}")
            # Return a fallback response
            return {
                "ats_score": 70,
                "gen_z_roast": "Oops! My circuits are fried trying to parse this resume. But hey, at least you submitted something!",
                "professional_fixes": [
                    "Ensure your resume is well-formatted for easy parsing",
                    "Use standard section headings (Experience, Education, Skills)",
                    "Avoid complex layouts that might confuse ATS systems"
                ],
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Error analyzing resume with Gemini: {str(e)}")
        return {
            "ats_score": 0,
            "gen_z_roast": "Even my AI powers couldn't make this resume look good. Time for a major overhaul!",
            "professional_fixes": [
                "Consider seeking professional resume writing help",
                "Start with a clean, simple template",
                "Focus on quantifiable achievements"
            ],
            "status": "error"
        }

# Unified API endpoints for all agent functionalities
@app.post("/api/analyze/resume/file")
async def analyze_resume_file(file: UploadFile):
    """
    Resume analysis endpoint that:
    1. Receives a PDF file
    2. Extracts text from the PDF
    3. Calls Gemini with a specialized system prompt
    4. Returns a predictable JSON structure
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
        
        # Extract text from the PDF
        resume_text = extract_text_from_pdf(temp_file_path)
        
        # Delete the temporary file
        os.unlink(temp_file_path)
        
        # Check if text was extracted
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF file. Please ensure it's a valid PDF with text content."
            )
        
        # Analyze the resume with Gemini
        analysis_result = analyze_resume_with_gemini(resume_text)
        
        return JSONResponse(content=analysis_result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/api/v1/api/analyze/resume")
async def analyze_resume_file_v1(file: UploadFile):
    """
    Resume analysis endpoint for frontend compatibility
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
        
        # Extract text from the PDF
        resume_text = extract_text_from_pdf(temp_file_path)
        
        # Delete the temporary file
        os.unlink(temp_file_path)
        
        # Check if text was extracted
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF file. Please ensure it's a valid PDF with text content."
            )
        
        # Analyze the resume with Gemini
        analysis_result = analyze_resume_with_gemini(resume_text)
        
        return JSONResponse(content=analysis_result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/api/analyze/resume/text")
async def analyze_resume_text(request: ResumeAnalysisRequest):
    """
    Analyze resume text using the Resume Intelligence Agent
    """
    try:
        result = orchestrator.resume_agent.analyze_resume(
            request.resume_content,
            request.job_description
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )

@app.post("/api/simulate/interview")
async def simulate_interview(request: InterviewPrepRequest):
    """
    Simulate interview using the Interview Simulation Agent
    """
    try:
        result = orchestrator.interview_agent.simulate_interview(
            request.role,
            request.experience_level,
            request.interview_type
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error simulating interview: {str(e)}"
        )

@app.post("/api/review/contract")
async def review_contract(request: ContractReviewRequest):
    """
    Review contract using the Contract Guardian Agent
    """
    try:
        result = orchestrator.contract_agent.review_contract(
            request.contract_text
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reviewing contract: {str(e)}"
        )

@app.post("/api/generate/document")
async def generate_document(request: DocumentGenerationRequest):
    """
    Generate document using the Auto-Docs Agent
    """
    try:
        result = orchestrator.docs_agent.generate_document(
            request.document_type,
            request.content_data
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating document: {str(e)}"
        )

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    """
    Execute complex workflows using the Master Orchestrator Agent
    """
    try:
        result = orchestrator.coordinate_agents(
            request.workflow,
            request.context
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing workflow: {str(e)}"
        )

# Add new Pydantic models for human interview endpoints
class HumanInterviewStartRequest(BaseModel):
    role: str
    experience_level: str

class HumanInterviewAnswerRequest(BaseModel):
    session_id: str
    answer_text: str

# Add session storage for human interview sessions
human_interview_sessions = {}

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
        
        # Generate a simple audio URL (in a real implementation, this would be actual TTS)
        audio_url = f"/audio/{session_id}_q1.mp3"
        
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
    try:
        # Retrieve session_id from memory
        if request.session_id not in human_interview_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session not found"
            )
        
        session = human_interview_sessions[request.session_id]
        
        # Append user's answer to the session's history_list
        session['history_list'].append({
            "question": session.get('last_question', 'Initial question'),
            "answer": request.answer_text
        })
        
        session['total_questions_asked'] += 1
        
        # Check if interview should be concluded (after 7 questions)
        if session['total_questions_asked'] >= 7:
            # Generate final assessment based on experience level
            del human_interview_sessions[request.session_id]
            
            # Customize feedback based on experience level
            if session['experience_level'] == "Beginner":
                feedback = "You did a great job explaining your background and motivations. For future interviews, try to connect your experiences more directly to the role requirements. Your enthusiasm is a strength!"
                strengths = ["Clear communication", "Enthusiasm and motivation", "Good foundational understanding"]
                weaknesses = ["Could connect experiences more directly to role", "Need more specific examples", "Technical depth could be improved"]
            elif session['experience_level'] == "Intermediate":
                feedback = "You demonstrated solid experience and good problem-solving abilities. To elevate your performance, focus on quantifying your achievements with specific metrics and showing more leadership initiative."
                strengths = ["Relevant experience", "Good problem-solving approach", "Clear communication"]
                weaknesses = ["Could include more specific metrics", "Need to elaborate on leadership examples", "Technical depth could be improved"]
            else:  # Expert
                feedback = "You showcased extensive experience and strategic thinking. To refine your approach, consider providing more concise answers while maintaining depth, and ensure you're directly addressing the question asked."
                strengths = ["Extensive experience", "Strategic thinking", "Strong technical foundation"]
                weaknesses = ["Answers could be more concise", "Need to directly address questions", "Could show more innovative approaches"]
            
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
        
        # Generate a simple audio URL (in a real implementation, this would be actual TTS)
        audio_url = f"/audio/{request.session_id}_q{session['total_questions_asked'] + 1}.mp3"
        
        # Store last question for next iteration
        session['last_question'] = next_question
        
        return JSONResponse(content={
            "session_id": request.session_id,
            "question_text": next_question,
            "audio_url": audio_url,
            "status": "continue"
        })
    except HTTPException:
        raise
    except Exception as e:
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
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": parsed_response['question'],
                "audio_url": f"/api/audio/{question_id}.mp3"
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
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": fallback_question,
                "audio_url": f"/api/audio/{question_id}.mp3"
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
        
        # Create the prompt
        prompt = f"{system_prompt}\n\nGenerate the next interview question based on the previous dialogue."
        
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
            question_id = f"q_{len(session['questions_asked']) + 1}"
            session['questions_asked'].append({
                "id": question_id,
                "text": parsed_response['question'],
                "status": parsed_response['interview_status']
            })
            session['question_count'] += 1
            
            # Check if interview is complete
            if parsed_response['interview_status'] == 'complete':
                final_score = 85  # In a real implementation, this would be calculated based on answers
                overall_feedback = f"Excellent response to strategic questions. Need to be more precise on policy details. Overall, {session['level']}-level proficiency demonstrated."
                
                # Remove session
                del interview_sessions[session_id]
                
                return JSONResponse(content={
                    "status": "complete",
                    "final_score": final_score,
                    "overall_feedback": overall_feedback
                })
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": parsed_response['question'],
                "audio_url": f"/api/audio/{question_id}.mp3"
            })
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response: {response.text}")
            # Return a fallback response
            question_id = f"q_{len(session['questions_asked']) + 1}"
            fallback_question = "What strategies would you use to improve employee engagement in our organization?"
            session['questions_asked'].append({
                "id": question_id,
                "text": fallback_question,
                "status": "continue"
            })
            session['question_count'] += 1
            
            return JSONResponse(content={
                "status": "success",
                "question_id": question_id,
                "question_text": fallback_question,
                "audio_url": f"/api/audio/{question_id}.mp3"
            })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting interview answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting interview answer: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
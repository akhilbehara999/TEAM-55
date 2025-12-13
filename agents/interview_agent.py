from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import settings
from agents.config import agent_config

class InterviewSimulationAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=agent_config.INTERVIEW_AGENT_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=agent_config.INTERVIEW_AGENT_TEMPERATURE
        )
        
        # Define prompt template for interview simulation
        self.interview_prompt = PromptTemplate(
            input_variables=["role", "experience_level", "interview_type"],
            template="""
            You are an expert interviewer conducting a {interview_type} interview for a {role} position.
            The candidate has {experience_level} experience level.
            
            Generate a realistic interview question appropriate for this role and experience level.
            Provide:
            1. The interview question
            2. Tips on how to approach answering this question
            3. What the interviewer is looking for in a good answer
            
            Format your response as JSON with keys: question, tips, expectations.
            """
        )
        
        # Define prompt template for interview preparation
        self.prep_prompt = PromptTemplate(
            input_variables=["job_description", "resume_content"],
            template="""
            You are helping a candidate prepare for an interview based on their resume and a job description.
            
            Job Description:
            {job_description}
            
            Resume Content:
            {resume_content}
            
            Provide:
            1. Key topics the candidate should be prepared to discuss
            2. Potential technical questions based on their experience
            3. Behavioral questions they should prepare for
            4. Specific examples from their resume to highlight
            
            Format your response as JSON with keys: topics, technical_questions, behavioral_questions, examples.
            """
        )
        
        # Create chains
        self.interview_chain = LLMChain(llm=self.llm, prompt=self.interview_prompt)
        self.prep_chain = LLMChain(llm=self.llm, prompt=self.prep_prompt)
    
    def simulate_interview(self, role: str, experience_level: str, interview_type: str) -> dict:
        """
        Simulate an interview question for a specific role and experience level
        """
        try:
            response = self.interview_chain.run(
                role=role,
                experience_level=experience_level,
                interview_type=interview_type
            )
            return {"success": True, "question": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def prepare_interview(self, job_description: str, resume_content: str) -> dict:
        """
        Prepare a candidate for an interview based on job description and resume
        """
        try:
            response = self.prep_chain.run(
                job_description=job_description,
                resume_content=resume_content
            )
            return {"success": True, "preparation": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    agent = InterviewSimulationAgent()
    result = agent.simulate_interview("Software Engineer", "Mid-level", "Technical")
    print(result)
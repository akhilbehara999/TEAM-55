from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import settings
from agents.config import agent_config

class ResumeIntelligenceAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=agent_config.RESUME_AGENT_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=agent_config.RESUME_AGENT_TEMPERATURE
        )
        
        # Define prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["resume_content", "job_description"],
            template="""
            You are an expert resume reviewer. Analyze the following resume content against the job description.
            
            Resume Content:
            {resume_content}
            
            Job Description:
            {job_description}
            
            Please provide:
            1. A score out of 100 for how well the resume matches the job description
            2. Specific suggestions for improvement
            3. Keywords that should be added or emphasized
            4. Formatting recommendations
            
            Format your response as JSON with keys: score, suggestions, keywords, formatting.
            """
        )
        
        # Create chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def analyze_resume(self, resume_content: str, job_description: str) -> dict:
        """
        Analyze a resume against a job description
        """
        try:
            response = self.chain.run(
                resume_content=resume_content,
                job_description=job_description
            )
            return {"success": True, "analysis": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    agent = ResumeIntelligenceAgent()
    result = agent.analyze_resume(
        "Sample resume content here...",
        "Sample job description here..."
    )
    print(result)
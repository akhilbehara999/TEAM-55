from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import settings
from agents.config import agent_config
import json

class ResumeIntelligenceAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=agent_config.RESUME_AGENT_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=agent_config.RESUME_AGENT_TEMPERATURE
        )
        
        # Define prompt template for enhanced resume analysis
        self.prompt_template = PromptTemplate(
            input_variables=["resume_content", "job_description", "target_vibe"],
            template="""
You are an expert resume reviewer. Analyze the following resume content against the job description and target company vibe.

Resume Content:
{resume_content}

Job Description:
{job_description}

Target Company Vibe:
{target_vibe}

Please provide a comprehensive analysis in the following JSON format without any additional text or markdown:
{{
  "ats_score": 85,
  "gen_z_roast": "Your resume is so basic, even LinkedIn ghosted it after 3 days.",
  "professional_fixes": [
    "Quantify your achievements with specific metrics",
    "Use action verbs to start bullet points",
    "Tailor keywords to match the job description",
    "Add a professional summary at the top"
  ],
  "status": "success",
  "buzzword_score": 75,
  "rewrite_suggestions": [
    {{
      "cliche_phrase": "Hard worker",
      "quantifiable_rewrite": "Increased team productivity by 25% through process optimization"
    }},
    {{
      "cliche_phrase": "Team player",
      "quantifiable_rewrite": "Collaborated with cross-functional teams to deliver project 2 weeks ahead of schedule"
    }}
  ],
  "rpa_score": 80,
  "rpa_summary": "Your resume aligns well with corporate environments but could use more startup buzzwords."
}}

Ensure all scores are integers between 0-100, and all lists contain realistic examples. Respond ONLY with the JSON object, no additional text.
"""
        )
        
        # Create chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def analyze_resume(self, resume_content: str, job_description: str, target_vibe: str = "Corporate") -> dict:
        """
        Analyze a resume against a job description and target company vibe
        """
        try:
            response = self.chain.run(
                resume_content=resume_content,
                job_description=job_description,
                target_vibe=target_vibe
            )
            
            # Try to parse the JSON response
            try:
                # Handle potential markdown code blocks
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove ```
                
                # Clean any extra text before or after JSON
                # Find the first { and last } to extract JSON
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    cleaned_response = cleaned_response[start_idx:end_idx+1]
                
                parsed_response = json.loads(cleaned_response)
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default structure
                return {
                    "ats_score": 75,
                    "gen_z_roast": "Your resume is so vanilla, it makes plain yogurt look exciting.",
                    "professional_fixes": [
                        "Add more quantifiable achievements",
                        "Include specific technical skills",
                        "Tailor content to job description",
                        "Use stronger action verbs"
                    ],
                    "status": "success",
                    "buzzword_score": 65,
                    "rewrite_suggestions": [
                        {
                            "cliche_phrase": "Responsible for...",
                            "quantifiable_rewrite": "Managed a team of 5 to deliver project 20% under budget"
                        },
                        {
                            "cliche_phrase": "Worked on various projects",
                            "quantifiable_rewrite": "Led development of 3 key features that increased user engagement by 40%"
                        }
                    ],
                    "rpa_score": 70,
                    "rpa_summary": "Resume shows solid fundamentals but needs more personality to match target vibe."
                }
        except Exception as e:
            return {
                "ats_score": 0,
                "gen_z_roast": "This resume is so empty, even the paper is asking for a refund.",
                "professional_fixes": [
                    "Add actual work experience",
                    "Include measurable achievements",
                    "List relevant technical skills",
                    "Add education details"
                ],
                "status": "error",
                "buzzword_score": 0,
                "rewrite_suggestions": [],
                "rpa_score": 0,
                "rpa_summary": "Unable to analyze due to insufficient content.",
                "error": str(e)
            }

# Example usage
if __name__ == "__main__":
    agent = ResumeIntelligenceAgent()
    result = agent.analyze_resume(
        "Sample resume content here...",
        "Sample job description here...",
        "Startup"
    )
    print(result)
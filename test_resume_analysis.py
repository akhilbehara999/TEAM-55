import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.resume_agent import ResumeIntelligenceAgent

# Test the resume analysis with sample content
if __name__ == "__main__":
    agent = ResumeIntelligenceAgent()
    
    # Sample resume content
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Software Developer at Tech Corp (2020-Present)
    - Developed scalable web applications using Python and JavaScript
    - Led a team of 5 developers
    
    Skills:
    - Python, JavaScript, React, Node.js
    - SQL, MongoDB
    - AWS, Docker
    
    Education:
    - B.S. Computer Science, University of Technology (2016-2020)
    """
    
    # Sample job description
    job_description = """
    We are looking for a Senior Software Engineer with experience in cloud technologies.
    Responsibilities include developing microservices, mentoring junior developers, 
    and working with modern DevOps practices.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong experience with Python and cloud platforms (AWS/GCP)
    - Experience with containerization technologies (Docker/Kubernetes)
    """
    
    # Target vibe
    target_vibe = "Startup"
    
    print("Testing resume analysis...")
    result = agent.analyze_resume(sample_resume, job_description, target_vibe)
    print("Analysis result:")
    print(result)
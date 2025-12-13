import os

class AgentConfig:
    # Resume Intelligence Agent configuration
    RESUME_AGENT_MODEL = "gemini-2.5-flash"
    RESUME_AGENT_TEMPERATURE = 0.7
    
    # Interview Simulation Agent configuration
    INTERVIEW_AGENT_MODEL = "gemini-2.5-flash"
    INTERVIEW_AGENT_TEMPERATURE = 0.8
    
    # Contract Guardian Agent configuration
    CONTRACT_AGENT_MODEL = "gemini-2.5-flash"
    CONTRACT_AGENT_TEMPERATURE = 0.3  # Lower temperature for more precise legal analysis
    
    # Auto-Docs Agent configuration
    DOCS_AGENT_MODEL = "gemini-2.5-flash"
    DOCS_AGENT_TEMPERATURE = 0.7
    
    # Master Orchestrator Agent configuration
    ORCHESTRATOR_AGENT_MODEL = "gemini-2.5-flash"
    ORCHESTRATOR_AGENT_TEMPERATURE = 0.5
    
    # Common configuration
    MAX_TOKENS = 2048
    TIMEOUT_SECONDS = 30

# Create agent config instance
agent_config = AgentConfig()
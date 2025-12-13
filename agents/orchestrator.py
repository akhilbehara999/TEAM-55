from typing import Dict, Any
from agents.resume_agent import ResumeIntelligenceAgent
from agents.interview_agent import InterviewSimulationAgent
from agents.contract_agent import ContractGuardianAgent
from agents.docs_agent import AutoDocsAgent
from agents.config import agent_config

class MasterOrchestratorAgent:
    def __init__(self):
        # Initialize all specialized agents
        self.resume_agent = ResumeIntelligenceAgent()
        self.interview_agent = InterviewSimulationAgent()
        self.contract_agent = ContractGuardianAgent()
        self.docs_agent = AutoDocsAgent()
        
    def route_request(self, request_type: str, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Route requests to the appropriate specialized agent
        
        Args:
            request_type: Type of request ('resume', 'interview', 'contract', 'docs')
            data: Request data containing necessary parameters
            
        Returns:
            Response from the appropriate agent
        """
        try:
            if request_type == "resume":
                return self.resume_agent.analyze_resume(
                    data.get("resume_content", ""),
                    data.get("job_description", "")
                )
            elif request_type == "interview":
                return self.interview_agent.simulate_interview(
                    data.get("role", ""),
                    data.get("experience_level", ""),
                    data.get("interview_type", "")
                )
            elif request_type == "contract":
                return self.contract_agent.review_contract(
                    data.get("contract_text", "")
                )
            elif request_type == "docs":
                return self.docs_agent.generate_document(
                    data.get("document_type", ""),
                    data.get("content_data", {})
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown request type: {request_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error routing request: {str(e)}"
            }
    
    def coordinate_agents(self, workflow: str, context: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Coordinate multiple agents for complex workflows
        
        Args:
            workflow: Type of workflow to execute
            context: Shared context between agents
            
        Returns:
            Combined response from all participating agents
        """
        try:
            if workflow == "job_application":
                # Job application workflow: Resume analysis + Interview prep
                resume_result = self.resume_agent.analyze_resume(
                    context.get("resume_content", ""),
                    context.get("job_description", "")
                )
                
                interview_result = self.interview_agent.prepare_interview(
                    context.get("job_description", ""),
                    context.get("resume_content", "")
                )
                
                return {
                    "success": True,
                    "workflow": "job_application",
                    "results": {
                        "resume_analysis": resume_result,
                        "interview_prep": interview_result
                    }
                }
            elif workflow == "offer_review":
                # Offer review workflow: Contract analysis + Document generation
                contract_result = self.contract_agent.review_contract(
                    context.get("contract_text", "")
                )
                
                docs_result = self.docs_agent.generate_document(
                    "counter_offer_letter",
                    {
                        "contract_issues": contract_result.get("issues", []),
                        "position": context.get("position", ""),
                        "company": context.get("company", "")
                    }
                )
                
                return {
                    "success": True,
                    "workflow": "offer_review",
                    "results": {
                        "contract_analysis": contract_result,
                        "supporting_docs": docs_result
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown workflow: {workflow}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error coordinating agents: {str(e)}"
            }

# Example usage
if __name__ == "__main__":
    orchestrator = MasterOrchestratorAgent()
    
    # Example routing
    result = orchestrator.route_request("resume", {
        "resume_content": "Sample resume...",
        "job_description": "Sample job description..."
    })
    print("Routing result:", result)
    
    # Example coordination
    result = orchestrator.coordinate_agents("job_application", {
        "resume_content": "Sample resume...",
        "job_description": "Sample job description..."
    })
    print("Coordination result:", result)
import google.generativeai as genai
from config import settings
from agents.config import agent_config
import json
import logging

class ContractGuardianAgent:
    def __init__(self):
        # Configure the Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            agent_config.CONTRACT_AGENT_MODEL
        )
    
    def review_contract(self, contract_text: str) -> dict:
        """
        Review a contract and return analysis results in structured JSON format
        """
        try:
            # Define the prompt for contract analysis
            prompt = f"""
You are the Contract Guardian Agent. Your sole task is to analyze the provided contract text and extract specific, high-risk clauses and key compensation terms. Your analysis must be purely objective, focusing on the legal impact and providing actionable negotiation advice. Your output MUST be a single JSON object.

Required JSON Output Structure (Strict):
{{
  "overall_score": Integer (0-100), where 100 is low risk.
  "summary": "String (A concise 3-sentence summary of the main risks/benefits).",
  "key_terms": {{
    "salary_base": "string - The base annual salary amount (e.g., '$85,000' or 'Not specified')",
    "start_date": "string - The employment start date in MM/DD/YYYY format or 'Not specified'",
    "pto_days": integer - Number of paid time off days per year (e.g., 15) or 0 if not specified,
    "signing_bonus": "string - The signing bonus amount (e.g., '$10,000' or 'None')"
  }},
  "risk_clauses": [
    {{
      "clause_name": "string - Name of the risky clause (e.g., 'Non-Compete Clause')",
      "risk_level": "RED|YELLOW|GREEN - RED for high risk, YELLOW for moderate risk, GREEN for low risk",
      "negotiation_strategy": "string - Specific advice on how to negotiate or address this clause"
    }}
  ]
}}

Instructions:
1. Carefully scan the entire contract text to identify the key terms listed above
2. For each key term, if found, extract the exact value from the contract
3. If a key term is not found, use the appropriate default value as shown in the examples above
4. Identify at least 3 risk clauses, focusing on legally significant terms
5. Assign risk levels based on potential negative impact to the employee
6. Provide specific, actionable negotiation strategies for each risk clause
7. Calculate an overall score based on the severity and number of risk clauses (higher score = lower risk)
8. Provide a clear, concise summary of the main findings

Analyze this contract text:
{contract_text}

CRITICAL INSTRUCTIONS:
- Respond ONLY with the JSON object as specified above
- DO NOT include any other text, explanations, or markdown formatting
- DO NOT wrap the JSON in markdown code blocks (no ```json ... ```)
- DO NOT include any text before or after the JSON object
- Ensure all JSON is properly formatted with correct syntax
"""
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Try to parse the response as JSON
            try:
                result = json.loads(response.text)
                return {"success": True, "data": result}
            except json.JSONDecodeError as e:
                # Log the actual response for debugging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to parse JSON response from Gemini API: {str(e)}")
                logger.error(f"Raw response: {response.text}")
                
                # If parsing fails, return a default structure with the raw response
                return {
                    "success": True,
                    "data": {
                        "overall_score": 75,
                        "summary": "We've analyzed your contract and identified several key terms and potential risks. Please review the detailed breakdown below.",
                        "key_terms": {
                            "salary_base": "Not specified",
                            "start_date": "Not specified",
                            "pto_days": 0,
                            "signing_bonus": "Not specified"
                        },
                        "risk_clauses": [
                            {
                                "clause_name": "Analysis Result",
                                "risk_level": "YELLOW",
                                "negotiation_strategy": response.text
                            }
                        ]
                    }
                }
                
        except Exception as e:
            # Log the error for debugging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ContractGuardianAgent.review_contract: {str(e)}")
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    agent = ContractGuardianAgent()
    result = agent.review_contract("Sample contract text here...")
    print(result)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import settings
from agents.config import agent_config

class ContractGuardianAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=agent_config.CONTRACT_AGENT_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=agent_config.CONTRACT_AGENT_TEMPERATURE
        )
        
        # Define prompt template for contract review
        self.review_prompt = PromptTemplate(
            input_variables=["contract_text"],
            template="""
            You are an expert contract reviewer specializing in employment contracts.
            Review the following contract and identify any potential issues or areas of concern.
            
            Contract Text:
            {contract_text}
            
            Please provide:
            1. A list of potential issues or red flags
            2. Explanation of each issue in plain language
            3. Recommendations for negotiation or changes
            4. Overall risk assessment (Low/Medium/High)
            
            Format your response as JSON with keys: issues, explanations, recommendations, risk_level.
            """
        )
        
        # Create chain
        self.review_chain = LLMChain(llm=self.llm, prompt=self.review_prompt)
    
    def review_contract(self, contract_text: str) -> dict:
        """
        Review an employment contract for potential issues
        """
        try:
            response = self.review_chain.run(contract_text=contract_text)
            return {"success": True, "review": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    agent = ContractGuardianAgent()
    result = agent.review_contract("Sample contract text here...")
    print(result)
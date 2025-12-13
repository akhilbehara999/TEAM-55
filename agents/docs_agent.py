from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import settings
from agents.config import agent_config

class AutoDocsAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=agent_config.DOCS_AGENT_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=agent_config.DOCS_AGENT_TEMPERATURE
        )
        
        # Define prompt template for document generation
        self.doc_prompt = PromptTemplate(
            input_variables=["document_type", "content_data"],
            template="""
            You are an expert document writer. Generate a professional {document_type} based on the provided information.
            
            Content Data:
            {content_data}
            
            Please provide:
            1. A well-formatted document following standard conventions for this document type
            2. Professional language and tone
            3. Proper structure and organization
            4. Relevant content based on the provided data
            
            Format your response as a properly formatted document.
            """
        )
        
        # Create chain
        self.doc_chain = LLMChain(llm=self.llm, prompt=self.doc_prompt)
    
    def generate_document(self, document_type: str, content_data: dict) -> dict:
        """
        Generate a professional document of a specific type
        """
        try:
            response = self.doc_chain.run(
                document_type=document_type,
                content_data=str(content_data)
            )
            return {"success": True, "document": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    agent = AutoDocsAgent()
    result = agent.generate_document("cover_letter", {
        "position": "Software Engineer",
        "company": "Tech Corp",
        "experience": "5 years in software development"
    })
    print(result)
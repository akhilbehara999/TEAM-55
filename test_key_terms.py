#!/usr/bin/env python3
"""
Test script to debug key terms extraction in the Contract Guardian feature.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from agents.contract_agent import ContractGuardianAgent

def test_key_terms_extraction():
    """Test the key terms extraction functionality"""
    print("=== Testing Key Terms Extraction ===")
    
    # Sample contract text with clear key terms
    sample_contract = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement ("Agreement") is made and entered into as of January 1, 2024,
    by and between TechCorp Inc. ("Employer") and John Doe ("Employee").
    
    1. POSITION AND DUTIES
    Employee shall serve as Senior Software Engineer and perform such duties as are
    customarily associated with such position.
    
    2. COMPENSATION
    Base Salary: Employee shall receive an annual base salary of $85,000, payable in
    accordance with Employer's standard payroll practices.
    
    3. BENEFITS
    Paid Time Off: Employee shall be entitled to fifteen (15) days of paid time off per
    calendar year.
    
    4. TERM
    The initial term of this Agreement shall commence on January 1, 2024 and continue
    until December 31, 2024.
    
    5. SIGNING BONUS
    Employee shall receive a one-time signing bonus of $10,000 upon commencement of employment.
    
    6. TERMINATION
    This Agreement may be terminated by either party upon thirty (30) days written notice.
    
    7. NON-COMPETE
    During the term of employment and for a period of two (2) years thereafter, Employee
    shall not engage in any business that competes with Employer within a fifty (50) mile
    radius of Employer's principal place of business.
    """
    
    try:
        # Initialize the contract agent
        agent = ContractGuardianAgent()
        print("✅ Contract agent initialized successfully")
        
        # Analyze the contract
        print("\n🔍 Analyzing contract...")
        result = agent.review_contract(sample_contract)
        
        if result.get("success"):
            data = result.get("data", {})
            print("✅ Contract analysis completed successfully")
            
            # Check key terms
            key_terms = data.get("key_terms", {})
            print(f"\n📋 Key Terms Extracted:")
            print(f"   Base Salary: {key_terms.get('salary_base', 'Not found')}")
            print(f"   Start Date: {key_terms.get('start_date', 'Not found')}")
            print(f"   PTO Days: {key_terms.get('pto_days', 'Not found')}")
            print(f"   Signing Bonus: {key_terms.get('signing_bonus', 'Not found')}")
            
            # Check if all required key terms are present
            required_terms = ['salary_base', 'start_date', 'pto_days', 'signing_bonus']
            missing_terms = [term for term in required_terms if term not in key_terms]
            
            if missing_terms:
                print(f"\n⚠️  Missing key terms: {missing_terms}")
            else:
                print(f"\n✅ All required key terms are present")
                
            # Display the full response structure
            print(f"\n📊 Full Response Structure:")
            print(f"   Overall Score: {data.get('overall_score', 'Not found')}")
            print(f"   Summary: {data.get('summary', 'Not found')[:50]}...")
            print(f"   Risk Clauses Count: {len(data.get('risk_clauses', []))}")
            print(f"   Key Terms Count: {len(key_terms)}")
            
            return True
        else:
            print(f"❌ Contract analysis failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_key_terms_extraction()
    if success:
        print("\n🎉 Key terms extraction test completed successfully!")
    else:
        print("\n❌ Key terms extraction test failed!")
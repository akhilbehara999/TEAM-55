#!/usr/bin/env python3
"""
Test script to debug the complete flow of key terms from backend to frontend simulation.
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from agents.contract_agent import ContractGuardianAgent

def test_complete_flow():
    """Test the complete flow of key terms extraction and response"""
    print("=== Testing Complete Key Terms Flow ===")
    
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
            
            # Simulate what the backend endpoint would return
            print("\n📤 Simulating backend endpoint response...")
            # The endpoint returns just the data portion, not the wrapper
            backend_response = data
            
            print("✅ Backend response prepared")
            
            # Simulate what the frontend would receive
            print("\n📥 Simulating frontend receipt of response...")
            frontend_data = backend_response
            
            # Check key terms structure
            if "key_terms" in frontend_data:
                key_terms = frontend_data["key_terms"]
                print("✅ Key terms structure found in response")
                
                # Display key terms as frontend would
                print(f"\n📋 Key Terms (Frontend Display):")
                print(f"   Base Salary: {key_terms.get('salary_base', 'Not specified')}")
                print(f"   Start Date: {key_terms.get('start_date', 'Not specified')}")
                print(f"   PTO Days: {key_terms.get('pto_days', 0)}")
                print(f"   Signing Bonus: {key_terms.get('signing_bonus', 'Not specified')}")
                
                # Verify data types
                print(f"\n🔢 Data Types Verification:")
                print(f"   Base Salary Type: {type(key_terms.get('salary_base'))}")
                print(f"   Start Date Type: {type(key_terms.get('start_date'))}")
                print(f"   PTO Days Type: {type(key_terms.get('pto_days'))} (Value: {key_terms.get('pto_days')})")
                print(f"   Signing Bonus Type: {type(key_terms.get('signing_bonus'))}")
                
                # Check if PTO days is an integer
                pto_days = key_terms.get('pto_days')
                if isinstance(pto_days, int):
                    print("✅ PTO Days is correctly formatted as integer")
                else:
                    print(f"⚠️  PTO Days is not an integer: {type(pto_days)}")
                
                return True
            else:
                print("❌ Key terms structure missing from response")
                print(f"Available keys: {list(frontend_data.keys())}")
                return False
        else:
            print(f"❌ Contract analysis failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 Complete key terms flow test completed successfully!")
    else:
        print("\n❌ Complete key terms flow test failed!")
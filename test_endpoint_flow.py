#!/usr/bin/env python3
"""
Test script to debug the complete endpoint flow for key terms extraction.
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from agents.orchestrator import MasterOrchestratorAgent

def test_endpoint_flow():
    """Test the complete endpoint flow for key terms extraction"""
    print("=== Testing Endpoint Flow for Key Terms ===")
    
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
        # Initialize the orchestrator
        orchestrator = MasterOrchestratorAgent()
        print("✅ Orchestrator initialized successfully")
        
        # Simulate the endpoint flow
        print("\n🔄 Simulating endpoint flow...")
        
        # This mimics what happens in the endpoint
        result = orchestrator.route_request("contract", {"contract_text": sample_contract})
        print(f"✅ Orchestrator response received")
        print(f"   Success: {result.get('success', 'Not found')}")
        
        if result.get("success", False):
            # This is what the endpoint does now with our fix
            data = result.get("data", result)  # Our fix
            print("✅ Data extracted from orchestrator response")
            
            # Verify the structure
            print(f"\n📊 Response Structure Check:")
            print(f"   Overall Score: {data.get('overall_score', 'Not found')}")
            print(f"   Summary: {data.get('summary', 'Not found')[:50]}...")
            
            # Check key terms specifically
            key_terms = data.get("key_terms", {})
            print(f"\n📋 Key Terms Check:")
            print(f"   Key Terms Present: {'key_terms' in data}")
            print(f"   Key Terms Type: {type(key_terms)}")
            print(f"   Key Terms Keys: {list(key_terms.keys())}")
            
            if key_terms:
                print(f"   Base Salary: {key_terms.get('salary_base', 'Not found')}")
                print(f"   Start Date: {key_terms.get('start_date', 'Not found')}")
                print(f"   PTO Days: {key_terms.get('pto_days', 'Not found')}")
                print(f"   Signing Bonus: {key_terms.get('signing_bonus', 'Not found')}")
                
                # Verify data types
                print(f"\n🔢 Data Types Verification:")
                print(f"   Base Salary Type: {type(key_terms.get('salary_base'))}")
                print(f"   Start Date Type: {type(key_terms.get('start_date'))}")
                print(f"   PTO Days Type: {type(key_terms.get('pto_days'))}")
                print(f"   Signing Bonus Type: {type(key_terms.get('signing_bonus'))}")
                
                return True
            else:
                print("❌ Key terms missing from response")
                return False
        else:
            print(f"❌ Orchestrator failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_endpoint_flow()
    if success:
        print("\n🎉 Endpoint flow test completed successfully!")
        print("The Key Terms section should now work properly in the frontend.")
    else:
        print("\n❌ Endpoint flow test failed!")